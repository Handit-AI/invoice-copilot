import os
import yaml  # Add YAML support
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# Import utility functions
from utils.call_llm import call_llm
from utils.read_file import read_file
from utils.replace_file import replace_file
from utils.semantic_search import semantic_search, format_search_results

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('coding_agent.log')
    ]
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger('coding_agent')

def format_history_summary(history: List[Dict[str, Any]]) -> str:
    if not history:
        return "No previous actions."
    
    history_str = "\n"
    
    for i, action in enumerate(history):
        # Header for all entries - removed timestamp
        history_str += f"Action {i+1}:\n"
        history_str += f"- Tool: {action['tool']}\n"
        history_str += f"- Reason: {action['reason']}\n"
        
        # Add parameters
        params = action.get("params", {})
        if params:
            history_str += f"- Parameters:\n"
            for k, v in params.items():
                history_str += f"  - {k}: {v}\n"
        
        # Add detailed result information
        result = action.get("result")
        if result:
            if isinstance(result, dict):
                success = result.get("success", False)
                history_str += f"- Result: {'Success' if success else 'Failed'}\n"
                
                # Add tool-specific details
                if action['tool'] == 'read_file' and success:
                    content = result.get("content", "")
                    # Show full content without truncating
                    history_str += f"- Content: {content}\n"
                elif action['tool'] == 'grep_search' and success:
                    matches = result.get("matches", [])
                    history_str += f"- Matches: {len(matches)}\n"
                    # Show all matches without limiting to first 3
                    for j, match in enumerate(matches):
                        history_str += f"  {j+1}. {match.get('file')}:{match.get('line')}: {match.get('content')}\n"
                elif action['tool'] == 'semantic_search' and success:
                    total_results = result.get("total_results", 0)
                    query = result.get("query", "")
                    namespace = result.get("namespace", "")
                    history_str += f"- Semantic Search Results: {total_results} found\n"
                    history_str += f"- Query: '{query}' in namespace '{namespace}'\n"
                    # Include formatted results if available
                    formatted_results = result.get("formatted_results", "")
                    if formatted_results:
                        history_str += f"- Results:\n{formatted_results}\n"
                elif action['tool'] == 'edit_file' and success:
                    operations = result.get("operations", 0)
                    history_str += f"- Operations: {operations}\n"
                    
                    # Include the reasoning if available
                    reasoning = result.get("reasoning", "")
                    if reasoning:
                        history_str += f"- Reasoning: {reasoning}\n"
                elif action['tool'] == 'list_dir' and success:
                    # Get the tree visualization string
                    tree_visualization = result.get("tree_visualization", "")
                    history_str += "- Directory structure:\n"
                    
                    # Properly handle and format the tree visualization
                    if tree_visualization and isinstance(tree_visualization, str):
                        # First, ensure we handle any special line ending characters properly
                        clean_tree = tree_visualization.replace('\r\n', '\n').strip()
                        
                        if clean_tree:
                            # Add each line with proper indentation
                            for line in clean_tree.split('\n'):
                                # Ensure the line is properly indented
                                if line.strip():  # Only include non-empty lines
                                    history_str += f"  {line}\n"
                        else:
                            history_str += "  (No tree structure data)\n"
                    else:
                        history_str += "  (Empty or inaccessible directory)\n"
                        logger.debug(f"Tree visualization missing or invalid: {tree_visualization}")
            else:
                history_str += f"- Result: {result}\n"
        
        # Add separator between actions
        history_str += "\n" if i < len(history) - 1 else ""
    
    return history_str

#############################################
# Main Decision Agent
#############################################
class MainDecisionAgent:
    def analyze_and_decide(self, user_query: str, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        logger.info(f"MainDecisionAgent: Analyzing user query: {user_query}")

        # Format history using the utility function
        history_str = format_history_summary(history)
        
        # Create prompt for the LLM using YAML instead of JSON
        prompt = f"""You are a chart and visualization specialist. Your primary goal is to create beautiful, interactive charts and graphs in React components. Given the following request, decide which tool to use from the available options.

User request: {user_query}

Here are the actions you performed:
{history_str}

Available tools:
1. edit_file: Create or modify files to generate charts, graphs, and visualizations
   - This is your primary tool for creating graphics in the workspace
   - The tool automatically reads the current file content first, then makes modifications
   - Parameters: target_file (path), instructions, chart_description
   - Example:
     tool: edit_file
     reason: I need to create a bar chart component showing sales data
     params:
       target_file: DynamicWorkspace.tsx
       instructions: Create a bar chart showing monthly sales data
       chart_description: |
         Create a React component that displays a bar chart with:
         - Monthly sales data from January to December
         - Interactive tooltips showing exact values
         - Responsive design with proper styling
         - Use Chart.js or similar library for visualization

2. semantic_search: Search for relevant data or examples when needed
   - Use this only when you need to find specific data or examples for charts
   - Parameters: query (text), namespace (optional), top_k (optional)
   - Example:
     tool: semantic_search
     reason: I need to find invoice data to create a revenue chart
     params:
       query: "monthly revenue invoice data"
       namespace: "example-namespace"
       top_k: 5

3. finish: Complete the task and provide final response
   - No parameters required
   - Example:
     tool: finish
     reason: I have completed the requested task of finding all logger instances
     params: {{}}

Respond with a YAML object containing:
```yaml
tool: one of: edit_file, semantic_search, finish
reason: |
  detailed explanation of why you chose this tool and what you intend to do
  For edit_file: explain what chart/graphic you will create
  For semantic_search: explain what data you need to find
  For finish: explain why the visualization is complete
params:
  # parameters specific to the chosen tool
```

IMPORTANT GUIDELINES:
- Your primary goal is to create charts, graphs, and visualizations in the workspace
- Always target DynamicWorkspace.tsx unless specified otherwise
- Use edit_file to create React components with charts using libraries like Chart.js, Recharts, or D3
- Include sample data if no real data is available
- Make visualizations interactive and responsive
- Only use semantic_search if you need specific data for the charts

If you believe no more actions are needed, use "finish" as the tool and explain why in the reason.
"""
        
        # Call LLM to decide action
        response = call_llm(prompt)

        # Look for YAML structure in the response
        yaml_content = ""
        if "```yaml" in response:
            yaml_blocks = response.split("```yaml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
        elif "```yml" in response:
            yaml_blocks = response.split("```yml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
        elif "```" in response:
            # Try to extract from generic code block
            yaml_blocks = response.split("```")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].strip()
        else:
            # If no code blocks, try to use the entire response
            yaml_content = response.strip()
        
        if yaml_content:
            decision = yaml.safe_load(yaml_content)
            
            # Validate the required fields
            assert "tool" in decision, "Tool name is missing"
            assert "reason" in decision, "Reason is missing"
            
            # For tools other than "finish", params must be present
            if decision["tool"] != "finish":
                assert "params" in decision, "Parameters are missing"
            else:
                decision["params"] = {}
            
            return decision
        else:
            raise ValueError("No YAML object found in response")

#############################################
# Action Classes for Chart Creation
#############################################

class SemanticSearchAction:
    def execute(self, params: Dict[str, Any], working_dir: str = "") -> Dict[str, Any]:
        query = params.get("query")
        if not query:
            raise ValueError("Missing query parameter")
        
        namespace = params.get("namespace", "example-namespace")
        top_k = params.get("top_k", 10)
        category_filter = params.get("category_filter")
        filename_filter = params.get("filename_filter")
        
        logger.info(f"SemanticSearchAction: Searching for '{query}' in namespace '{namespace}'")
        
        # Choose search method based on filters
        if category_filter:
            from utils.semantic_search import search_by_category
            success, results = search_by_category(
                query=query,
                category=category_filter,
                namespace=namespace,
                top_k=top_k
            )
        elif filename_filter:
            from utils.semantic_search import search_by_filename
            success, results = search_by_filename(
                query=query,
                filename=filename_filter,
                namespace=namespace,
                top_k=top_k
            )
        else:
            # Regular semantic search
            success, results = semantic_search(
                query=query,
                namespace=namespace,
                top_k=top_k
            )
        
        # Format results for better readability
        formatted_results = ""
        if success and results:
            formatted_results = format_search_results(results)
        
        return {
                "success": success,
            "results": results,
            "formatted_results": formatted_results,
            "query": query,
            "namespace": namespace,
            "total_results": len(results) if results else 0
        }

# class ListDirAction:
#     def execute(self, params: Dict[str, Any], working_dir: str = "") -> Dict[str, Any]:
#         path = params.get("relative_workspace_path", ".")
        
#         # Ensure path is relative to working directory
#         full_path = os.path.join(working_dir, path) if working_dir else path
        
#         logger.info(f"ListDirAction: Listing directory {full_path}")
        
#         # Call list_dir utility which returns (success, tree_str)
#         success, tree_str = list_dir(full_path)
        
#         return {
#             "success": success,
#             "tree_visualization": tree_str
#         }

# class DeleteFileAction:
#     def execute(self, params: Dict[str, Any], working_dir: str = "") -> Dict[str, Any]:
#         file_path = params.get("target_file")
#         if not file_path:
#             raise ValueError("Missing target_file parameter")
        
#         # Ensure path is relative to working directory
#         full_path = os.path.join(working_dir, file_path) if working_dir else file_path
        
#         logger.info(f"DeleteFileAction: Deleting file {full_path}")
        
#         # Call delete_file utility which returns (success, message)
#         success, message = delete_file(full_path)
        
#         return {
#             "success": success,
#             "message": message
#         }

class EditFileAction:
    def execute(self, params: Dict[str, Any], working_dir: str = "") -> Dict[str, Any]:
        target_file = params.get("target_file")
        instructions = params.get("instructions")
        chart_description = params.get("chart_description", "")
        
        if not target_file:
            raise ValueError("Missing target_file parameter")
        if not instructions:
            raise ValueError("Missing instructions parameter")
        
        # Ensure path is relative to working directory
        full_path = os.path.join(working_dir, target_file) if working_dir else target_file
        
        logger.info(f"EditFileAction: Editing file {full_path}")
        
        # Step 1: Read the file
        file_content, read_success = read_file(full_path)
        if not read_success:
            return {
                "success": False,
                "message": f"Failed to read file: {full_path}",
                "operations": 0
            }
        
        # Step 2: Analyze and plan changes
        file_lines = file_content.split('\n')
        total_lines = len(file_lines)
        
        # Generate a prompt for the LLM to create chart components
        prompt = f"""
You are a React chart specialist. Your goal is to create or modify React components to display charts and visualizations.

CURRENT FILE CONTENT:
{file_content}

USER REQUEST: 
{instructions}

CHART REQUIREMENTS:
{chart_description}

Create a React component that displays the requested chart/visualization. Follow these guidelines:

1. ALWAYS create interactive and responsive charts
2. Use modern chart libraries like Recharts, Chart.js, or similar
3. Include sample data if no real data is provided
4. Make charts visually appealing with proper styling
5. Add tooltips and legends when appropriate
6. Ensure mobile responsiveness

If the file is empty or has minimal content, create a complete new component.
If the file has existing content, modify it to add the requested visualization.

Return a YAML object with your reasoning and edit operations:

```yaml
reasoning: |
  Explain your approach for creating the chart component.
  Describe what type of visualization you're creating and why.
  Explain how you're integrating it with the existing code structure.
  Detail what chart library you're using and why it's appropriate.

operations:
  - start_line: 1
    end_line: 49
    replacement: |
      import React from 'react';
      import { useApp } from '@/contexts/AppContext';
      import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

      const sampleData = [
        { month: 'Jan', sales: 4000, expenses: 2400 },
        { month: 'Feb', sales: 3000, expenses: 1398 },
        { month: 'Mar', sales: 2000, expenses: 9800 },
        { month: 'Apr', sales: 2780, expenses: 3908 },
        { month: 'May', sales: 1890, expenses: 4800 },
        { month: 'Jun', sales: 2390, expenses: 3800 }
      ];

      export function DynamicWorkspace() {{
        const {{ state }} = useApp();
        const {{ workspaceContent }} = state;

        if (workspaceContent === 'expenses-report') {{
          return <ExpensesReport />;
        }}

        return (
          <div className="flex h-full items-center justify-center p-6">
            <div className="w-full max-w-4xl">
              <h2 className="text-2xl font-bold mb-6 text-center">Sales Dashboard</h2>
              <ResponsiveContainer width="100%" height={{400}}>
                <BarChart data={{sampleData}}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="sales" fill="#8884d8" />
                  <Bar dataKey="expenses" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        );
      }}
```

IMPORTANT RULES:
- Always replace the ENTIRE file content for chart components
- Use line 1 to total_lines+1 to replace everything
- Include all necessary imports for chart libraries
- Create complete, functional React components
- Add proper TypeScript types if the file is .tsx
- Ensure the component is responsive and well-styled
"""
        
        # Call LLM to analyze
        response = call_llm(prompt)

        # Look for YAML structure in the response
        yaml_content = ""
        if "```yaml" in response:
            yaml_blocks = response.split("```yaml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
        elif "```yml" in response:
            yaml_blocks = response.split("```yml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
        elif "```" in response:
            # Try to extract from generic code block
            yaml_blocks = response.split("```")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].strip()
        
        if not yaml_content:
            return {
                "success": False,
                "message": "No YAML object found in LLM response",
                "operations": 0
            }
        
        try:
            decision = yaml.safe_load(yaml_content)
            
            # Validate the required fields
            if "reasoning" not in decision:
                raise ValueError("Reasoning is missing")
            if "operations" not in decision:
                raise ValueError("Operations are missing")
            
            # Ensure operations is a list
            if not isinstance(decision["operations"], list):
                raise ValueError("Operations are not a list")
            
            # Validate operations
            for op in decision["operations"]:
                if "start_line" not in op:
                    raise ValueError("start_line is missing")
                if "end_line" not in op:
                    raise ValueError("end_line is missing")
                if "replacement" not in op:
                    raise ValueError("replacement is missing")
                if not (1 <= op["start_line"] <= total_lines + 1):
                    raise ValueError(f"start_line out of range: {op['start_line']}")
                if not (1 <= op["end_line"] <= total_lines + 1):
                    raise ValueError(f"end_line out of range: {op['end_line']}")
                if op["start_line"] > op["end_line"]:
                    raise ValueError(f"start_line > end_line: {op['start_line']} > {op['end_line']}")
                    
        except Exception as e:
            return {
                "success": False,
                "message": f"Error parsing edit operations: {str(e)}",
                "operations": 0
            }
        
        # Step 3: Apply changes
        edit_operations = decision["operations"]
        reasoning = decision.get("reasoning", "")
        
        # Sort edit operations in descending order by start_line
        # This ensures that line numbers remain valid as we edit from bottom to top
        sorted_ops = sorted(edit_operations, key=lambda op: op["start_line"], reverse=True)
        
        # Apply each operation
        successful_ops = 0
        failed_ops = 0
        details = []
        
        for op in sorted_ops:
            success, message = replace_file(
                target_file=full_path,
            start_line=op["start_line"],
            end_line=op["end_line"],
            content=op["replacement"]
        )
    
            details.append({"success": success, "message": message})
            if success:
                successful_ops += 1
            else:
                failed_ops += 1
        
        all_successful = failed_ops == 0
        
        return {
                "success": all_successful,
            "operations": len(sorted_ops),
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "details": details,
            "reasoning": reasoning
        }

class FormatResponseAction:
    def execute(self, history: List[Dict[str, Any]]) -> str:
        # If no history, return a generic message
        if not history:
            return "No actions were performed."
        
        # Generate a summary of actions for the LLM using the utility function
        actions_summary = format_history_summary(history)
        
        # Prompt for the LLM to generate the final response
        prompt = f"""
You are a chart and visualization specialist. You have just created or modified charts/graphs based on the user's request.

Here are the actions you performed:
{actions_summary}

Generate a friendly and informative response that explains:
1. What chart or visualization you created
2. What data it displays and key insights
3. What libraries or technologies were used
4. How the user can interact with or customize the chart

IMPORTANT: 
- Focus on the visual result and what the user can see
- Mention the type of chart (bar chart, line chart, pie chart, etc.)
- Explain any interactive features (tooltips, legends, etc.)
- Be enthusiastic about the visualization created
- Suggest possible improvements or variations
"""
        
        # Call LLM to generate response
        response = call_llm(prompt)
        
        logger.info(f"###### Final Response Generated ######\n{response}\n###### End of Response ######")
        
        return response

#############################################
# Main Coding Agent Orchestrator
#############################################
class CodingAgent:
    def __init__(self, working_dir: str = ""):
        self.working_dir = working_dir
        self.main_agent = MainDecisionAgent()
        self.actions = {
            "edit_file": EditFileAction(),
            "semantic_search": SemanticSearchAction(),
        }
        self.format_response = FormatResponseAction()
        
    def process_request(self, user_query: str, max_iterations: int = 10) -> str:
        """
        Process a user request using the coding agent workflow.
        
        Args:
            user_query: The user's request
            max_iterations: Maximum number of tool calls to prevent infinite loops
            
        Returns:
            Final response string
        """
        logger.info(f"CodingAgent: Processing request: {user_query}")
        
        # Initialize shared state
        shared_state = {
            "user_query": user_query,
            "history": [],
            "working_dir": self.working_dir
        }
        
        # Main processing loop
        for iteration in range(max_iterations):
            logger.info(f"CodingAgent: Iteration {iteration + 1}/{max_iterations}")
            
            try:
                # Get decision from main agent
                decision = self.main_agent.analyze_and_decide(
                    user_query=user_query,
                    history=shared_state["history"]
                )
                
                tool = decision["tool"]
                reason = decision["reason"]
                params = decision.get("params", {})
                
                logger.info(f"CodingAgent: Selected tool: {tool}")
                
                # Add action to history
                action_entry = {
                    "tool": tool,
                    "reason": reason,
                    "params": params,
                    "result": None,
                    "timestamp": datetime.now().isoformat()
                }
                shared_state["history"].append(action_entry)
                
                # Handle finish action
                if tool == "finish":
                    logger.info("CodingAgent: Finishing and generating response")
                    final_response = self.format_response.execute(shared_state["history"])
                    return final_response
                
                # Execute the selected action
                if tool in self.actions:
                    try:
                        result = self.actions[tool].execute(params, self.working_dir)
                        # Update result in history
                        shared_state["history"][-1]["result"] = result
                        logger.info(f"CodingAgent: Action {tool} completed successfully")
                    except Exception as e:
                        error_result = {
                            "success": False,
                            "error": str(e)
                        }
                        shared_state["history"][-1]["result"] = error_result
                        logger.error(f"CodingAgent: Action {tool} failed: {str(e)}")
                else:
                    logger.error(f"CodingAgent: Unknown tool: {tool}")
                    error_result = {
                        "success": False,
                        "error": f"Unknown tool: {tool}"
                    }
                    shared_state["history"][-1]["result"] = error_result
                    
            except Exception as e:
                logger.error(f"CodingAgent: Error in iteration {iteration + 1}: {str(e)}")
                # Add error to history
                error_entry = {
                    "tool": "error",
                    "reason": f"Internal error: {str(e)}",
                    "params": {},
                    "result": {"success": False, "error": str(e)},
                    "timestamp": datetime.now().isoformat()
                }
                shared_state["history"].append(error_entry)
                break
        
        # If we've reached max iterations without finishing
        logger.warning(f"CodingAgent: Reached maximum iterations ({max_iterations})")
        final_response = self.format_response.execute(shared_state["history"])
        return final_response

# Create the main coding agent instance
coding_agent = CodingAgent()

# Example usage function
def run_coding_agent(user_query: str, working_dir: str = "") -> str:
    """
    Convenience function to run the coding agent with a user query.
    
    Args:
        user_query: The user's request
        working_dir: Optional working directory for file operations
        
    Returns:
        Final response from the agent
    """
    agent = CodingAgent(working_dir=working_dir)
    return agent.process_request(user_query)

# Example usage:
# if __name__ == "__main__":
#     response = run_coding_agent("List all Python files in the current directory")
#     print(response)
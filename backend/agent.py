#!/usr/bin/env python3
"""
Invoice Copilot AI Agent - Intelligent Document Processing and Code Report Generation

This module implements a sophisticated AI agent system for processing invoice documents
and generating professional business reports with data visualizations. The system uses
a multi-agent architecture with decision-making, action execution, and observability.

Key Components:
- MainDecisionAgent: Analyzes user requests and decides which tools to use
- Action Classes: Execute specific tasks (file editing, report generation, etc.)
- CodingAgent: Orchestrates the entire workflow
- Handit.ai Integration: Provides full observability and performance tracking

Features:
- Intelligent document processing with Chunkr AI
- Professional report generation with Recharts visualizations
- Real-time data analysis from invoice JSON files
- Multi-step decision making with YAML-based responses
- Comprehensive logging and error handling
- AI observability and performance tracking

Hight level Architecture:
1. User Request → MainDecisionAgent (analyzes and decides)
2. Decision → Action Classes (execute specific tasks)
3. Results → FormatResponseAction (generates final response)
4. Handit.ai tracks all operations for observability

Dependencies:
- yaml: YAML parsing for structured LLM responses
- logging: Comprehensive logging system
- json: JSON data processing
- glob: File pattern matching
- datetime: Timestamp handling
- typing: Type hints for better code quality
- utils.call_llm: LLM communication
- utils.read_file: File reading utilities
- utils.replace_file: File editing utilities
- services.handit_service: AI observability

Author: coderTtxi12
Version: 1.0.0
"""

import os
import yaml  # YAML support for structured LLM responses
import logging
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional

# Import utility functions for file operations and LLM communication
from utils.call_llm import call_llm
from utils.read_file import read_file
from utils.replace_file import replace_file, overwrite_entire_file

# AI Observability, Evaluation, and Self-Improvement with Handit.ai
from services.handit_service import tracker

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

# Configure comprehensive logging with both console and file output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('coding_agent.log')  # File output for debugging
    ]
)

# Reduce noise from HTTP client logging
logging.getLogger("httpx").setLevel(logging.WARNING)

# Create logger instance for this module
logger = logging.getLogger('coding_agent')

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def load_invoice_data() -> Dict[str, Any]:
    """
    Load all invoice JSON files from the processed/ directory.
    
    This function scans the processed/ directory for JSON files containing
    invoice data that has been processed by Chunkr AI. It loads each file
    and returns a dictionary mapping filenames to their invoice data.
    
    Returns:
        Dict[str, Any]: Dictionary where keys are filenames and values are
                       the parsed JSON invoice data. Returns empty dict if
                       no files found or error occurs.
    
    Example:
        >>> data = load_invoice_data()
        >>> print(f"Loaded {len(data)} invoice files")
        Loaded 5 invoice files
        >>> print(data.keys())
        dict_keys(['invoice1.json', 'invoice2.json', 'invoice3.json'])
    
    Note:
        - Files are expected to be in the backend/processed/ directory
        - Only JSON files are processed
        - Invalid JSON files are skipped with error logging
        - Uses UTF-8 encoding for file reading
    """
    try:
        # Get the directory where this script is located (backend/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        processed_dir = os.path.join(current_dir, "processed")
        
        # Find all JSON files in the processed directory
        json_files = glob.glob(os.path.join(processed_dir, "*.json"))
        logger.info(f"Found {len(json_files)} JSON files in {processed_dir}")
        
        invoices = {}
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    invoice_data = json.load(f)
                
                # Use filename as key for easy identification
                file_name = os.path.basename(json_file)
                invoices[file_name] = invoice_data
                logger.info(f"Loaded invoice: {file_name}")
                
            except Exception as e:
                logger.error(f"Error loading {json_file}: {str(e)}")
                continue
        
        logger.info(f"Loaded {len(invoices)} invoice files")
        return invoices
        
    except Exception as e:
        logger.error(f"Error loading invoice data: {str(e)}")
        return {}

def format_history_summary(history: List[Dict[str, Any]], execution_id: str = None) -> str:
    """
    Format the action history into a readable summary for LLM consumption.
    
    This function takes the execution history and formats it into a structured
    text summary that can be used by LLMs to understand what actions have been
    performed. It includes tool names, reasons, parameters, and results.
    
    Args:
        history (List[Dict[str, Any]]): List of action dictionaries containing:
            - tool: Name of the tool used
            - reason: Why the tool was chosen
            - params: Parameters passed to the tool
            - result: Result of the tool execution
            - timestamp: When the action was performed
        execution_id (str, optional): Handit.ai execution ID for tracking
    
    Returns:
        str: Formatted history summary with detailed action information
        
    Example:
        >>> history = [
        ...     {"tool": "edit_file", "reason": "Create chart", "result": {"success": True}}
        ... ]
        >>> summary = format_history_summary(history)
        >>> print(summary)
        Action 1:
        - Tool: edit_file
        - Reason: Create chart
        - Result: Success
        - Operations: 1
    
    Note:
        - Truncates long responses to 200 characters for readability
        - Includes tool-specific details (operations count, request types)
        - Tracks usage with Handit.ai if execution_id provided
        - Handles missing or malformed data gracefully
    """
    if not history:
        return "No previous actions."
    
    history_str = "\n"
    
    for i, action in enumerate(history):
        # Header for all entries - removed timestamp for cleaner output
        history_str += f"Action {i+1}:\n"
        history_str += f"- Tool: {action['tool']}\n"
        history_str += f"- Reason: {action['reason']}\n"
        
        # Add parameters if present
        params = action.get("params", {})
        if params:
            history_str += f"- Parameters:\n"
            for k, v in params.items():
                history_str += f"  - {k}: {v}\n"
        
        # Add detailed result information with tool-specific formatting
        result = action.get("result")
        if result:
            if isinstance(result, dict):
                success = result.get("success", False)
                history_str += f"- Result: {'Success' if success else 'Failed'}\n"
                
                # Add tool-specific details for better context
                if action['tool'] == 'edit_file' and success:
                    operations = result.get("operations", 0)
                    history_str += f"- Operations: {operations}\n"
                    
                    # Include the reasoning if available
                    reasoning = result.get("reasoning", "")
                    if reasoning:
                        history_str += f"- Reasoning: {reasoning}\n"
                elif action['tool'] == 'simple_report' and success:
                    response = result.get("response", "")
                    request_type = result.get("request_type", "")
                    history_str += f"- Request Type: {request_type}\n"
                    if response:
                        # Truncate long responses for readability
                        history_str += f"- Response: {response[:200]}...\n" if len(response) > 200 else f"- Response: {response}\n"
                elif action['tool'] == 'other_request' and success:
                    response = result.get("response", "")
                    request_type = result.get("request_type", "")
                    history_str += f"- Request Type: {request_type}\n"
                    if response:
                        # Truncate long responses for readability
                        history_str += f"- Response: {response[:200]}...\n" if len(response) > 200 else f"- Response: {response}\n"
            else:
                history_str += f"- Result: {result}\n"
        
        # Add separator between actions for better readability
        history_str += "\n" if i < len(history) - 1 else ""

        # Track the LLM usage with Handit.ai for observability
        if execution_id:
            tracker.track_node(
                input=history,
                output=history_str,
                node_name="format_history_summary",
                agent_name="invoice_copilot",
                node_type="tool",
                execution_id=execution_id
            )
    
    return history_str

# =============================================================================
# MAIN DECISION AGENT
# =============================================================================

class MainDecisionAgent:
    """
    Main Decision Agent for Intelligent Tool Selection and Workflow Orchestration.
    
    This class is responsible for analyzing user requests and deciding which actions
    to use based on the request type, current context, and execution history.
    It uses LLM-based decision making with YAML-structured responses for reliable
    parsing and execution.
    
    The agent can choose from several actions:
    - edit_file: Create professional reports with data visualizations
    - simple_report: Answer specific data questions without visualizations
    - other_request: Handle non-report related requests
    - finish: Complete the workflow and generate final response
    
    Attributes:
        None (stateless agent)
    
    Methods:
        analyze_and_decide: Main decision-making method
    
    Example:
        >>> agent = MainDecisionAgent()
        >>> decision = agent.analyze_and_decide(
        ...     user_query="Create a bar chart of expenses",
        ...     execution_id="exec_123",
        ...     history=[],
        ...     working_dir="frontend/src/components"
        ... )
        >>> print(decision["tool"])
        edit_file
    """
    
    def analyze_and_decide(self, user_query: str, execution_id: str, history: List[Dict[str, Any]], working_dir: str = "") -> Dict[str, Any]:
        """
        Analyze user request and decide which action to execute.
        
        This method is the core decision-making engine of the agent. It analyzes
        the user's request, considers the execution history, and decides which
        action is most appropriate to handle the request. The decision is made
        using an LLM with a carefully crafted prompt that ensures consistent
        and reliable tool selection.
        
        Args:
            user_query (str): The user's request or question
            execution_id (str): Handit.ai execution ID for observability tracking
            history (List[Dict[str, Any]]): Previous actions performed in this session
            working_dir (str): Working directory for file operations (default: "")
        
        Returns:
            Dict[str, Any]: Decision dictionary containing:
                - tool: Selected tool/action name (edit_file, simple_report, other_request, finish)
                - reason: Detailed explanation of why this tool was chosen
                - params: Parameters to pass to the selected tool
        
        Raises:
            ValueError: If no YAML object is found in LLM response
            AssertionError: If required fields are missing from decision
        
        Example:
            >>> decision = agent.analyze_and_decide(
            ...     user_query="What's the total revenue?",
            ...     execution_id="exec_123",
            ...     history=[],
            ...     working_dir="frontend/src"
            ... )
            >>> print(decision)
            {
                'tool': 'simple_report',
                'reason': 'User is asking for specific data without needing visualizations',
                'params': {'user_request': "What's the total revenue?"}
            }
        
        Note:
            - Uses YAML format for structured LLM responses
            - Tracks decisions with Handit.ai for observability
            - Handles multiple YAML block formats (yaml, yml, generic)
            - Validates response structure before returning
        """
        logger.info(f"MainDecisionAgent: Analyzing user query: {user_query}")

        # Get the working directory from the params
        working_dir = working_dir
        # Format history using the utility function for LLM consumption
        history_str = format_history_summary(history, execution_id)
        
        # Create comprehensive prompt for the LLM using YAML instead of JSON
        # This ensures structured, parseable responses
        system_prompt = f"""You are a professional report and data visualization specialist. Given the following request, decide which tool to use from the available options.

Here are the actions you performed:
{history_str}

Available tools:
1. edit_file: Create or edit professional reports with data visualizations, if graphs are needed to complete the user request
   - Parameters: target_file, instructions, chart_description
     target_file: DynamicWorkspace.tsx (this file is in the working directory: {working_dir})
     instructions: User request
     chart_description: A detailed description of charts are needed for the report.
   - Example:
     tool: edit_file
     reason: I need to create a professional report with real data, and charts are needed for the report, and insights.
     params:
       target_file: DynamicWorkspace.tsx
       instructions: User request
       chart_description: 
         Professional business report featuring:
         - Expenses trends using LineChart from Recharts
         - Category breakdown using PieChart from Recharts
         - Monthly comparison using BarChart from Recharts
         - Key metrics cards with real numbers
         - Responsive design with professional styling

2. simple_report: ONLY If the user wants to know especific information about the data, the user resquest is simple and graphs are not needed to complete the user request
   - Parameters: user_request
     user_request: User request
   - Example:
     tool: simple_report
     reason: I need to answer just an specific information, and the user request is simple and graphs are not needed
     params:
       user_request: User request
         
3. other_request: If the user request is not related to the report, graphs, statistics data, you can use this tool to do other requests.
   - Parameters: user_request
     user_request: User request
   - Example:
     tool: other_request
     reason: I need to gently tell the user that I can only help with the report, graphs, statistics data, and other requests related to the report, graphs, statistics data.
     params:
       user_request: User request

4. finish: Complete the task and provide final response
   - No parameters required
   - Example:
     tool: finish
     reason: I have successfully completed all the user request.
     params: {{}}

Respond with a YAML object containing:
```yaml
tool: one of: edit_file, simple_report, other_request, finish
reason:
  detailed explanation of why you chose this tool and what you intend to do
  if you chose finish, explain why no more actions are needed
params:
  # parameters specific to the chosen tool
```

If you believe no more actions are needed, use "finish" as the tool and explain why in the reason.
"""
        
        # Call LLM to decide action with comprehensive prompt
        response = call_llm(system_prompt, user_query)

        # Track the LLM usage with Handit.ai for observability
        if execution_id:
            tracker.track_node(
                input={
                    "system_prompt": system_prompt,
                    "user_prompt": user_query
                },
                output=response,
                node_name="main_decision_agent",
                agent_name="invoice_copilot",
                node_type="llm",
                execution_id=execution_id
            )

        # Parse YAML response with multiple format support
        # This handles different ways LLMs might format YAML blocks
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
            # Parse YAML and validate structure
            decision = yaml.safe_load(yaml_content)
            
            # Validate the required fields to ensure response quality
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

# =============================================================================
# ACTION CLASSES FOR CHART CREATION AND REPORT GENERATION
# =============================================================================

# Note: Commented out actions (ListDirAction, DeleteFileAction) are available
# for future use but not currently implemented in the workflow

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

class SimpleReportAction:
    """
    Action class for generating simple text-based reports without visualizations.
    
    This action is used when users ask for specific information about the data
    that doesn't require charts or complex visualizations. It provides direct
    answers to questions about totals, averages, counts, and other data insights.
    
    The action loads invoice data, analyzes it based on the user's request,
    and generates a concise, professional response with actionable insights.
    
    Attributes:
        None (stateless action)
    
    Methods:
        execute: Process the simple report request
    
    Example:
        >>> action = SimpleReportAction()
        >>> result = action.execute(
        ...     params={"user_request": "What's the total revenue?"},
        ...     working_dir="frontend/src",
        ...     execution_id="exec_123"
        ... )
        >>> print(result["response"])
        "Based on the processed invoice data, the total revenue is $15,750.00..."
    
    Supported Request Types:
        - Mathematical calculations (sums, averages, counts)
        - Data filtering and analysis
        - Business insights and trends
        - Specific data point queries
    """
    
    def execute(self, params: Dict[str, Any], working_dir: str = "", execution_id: str = None) -> Dict[str, Any]:
        """
        Execute a simple report request without visualizations.
        
        This method processes user requests that require specific information
        from the invoice data but don't need charts or complex visualizations.
        It loads the invoice data, analyzes it based on the user's request,
        and generates a professional response with insights and recommendations.
        
        Args:
            params (Dict[str, Any]): Parameters containing:
                - user_request (str): The user's specific question or request
            working_dir (str): Working directory (not used for simple reports)
            execution_id (str, optional): Handit.ai execution ID for tracking
        
        Returns:
            Dict[str, Any]: Result dictionary containing:
                - success (bool): Whether the operation was successful
                - response (str): Generated response to the user's request
                - request_type (str): Always "simple_report"
        
        Raises:
            ValueError: If user_request parameter is missing
        
        Example:
            >>> result = action.execute({
            ...     "user_request": "What's the average invoice amount?"
            ... })
            >>> print(result["success"])
            True
            >>> print(result["response"][:50])
            "Based on the processed invoice data, the average..."
        
        Note:
            - Loads real invoice data from processed JSON files
            - Uses LLM for intelligent data analysis and response generation
            - Provides actionable insights and next steps
            - Tracks usage with Handit.ai for observability
            - Handles errors gracefully with informative messages
        """
        user_request = params.get("user_request")
        if not user_request:
            raise ValueError("Missing user_request parameter")
        
        logger.info(f"SimpleReportAction: Processing simple report request: {user_request}")
        
        try:
            # Load invoice data from processed JSON files
            invoice_data = load_invoice_data()
            
            # Check if we have data to work with
            if not invoice_data:
                return {
                    "success": False,
                    "response": "No invoice data found. Please upload some invoice files first.",
                    "request_type": "simple_report"
                }
            
            # Generate a comprehensive prompt for the LLM to handle simple reports
            # This ensures accurate, professional responses with business insights
            system_prompt = f"""
You are a professional report specialist. The user has made a simple request that doesn't require graphs or complex visualizations.
Answer the user's request based on the provided data processed

Provide a clear, concise response to the user's request. 

GUIDELINES:
- For math operations, like sums, averages, etc, be super accurate and precise
- Focus on providing specific information requested
- Use only the real data processed
- Keep the response professional but straightforward
- No graphs or visualizations needed
- Provide actionable insights when possible
- Suggest next steps to the user when possible

Generate a helpful response that directly addresses the user's request.
"""
            

            user_prompt = f"""
User request: {user_request}

Data processed: {json.dumps(invoice_data, indent=2)}
"""


            # Call LLM to generate intelligent response based on real data
            response = call_llm(
                system_prompt, 
                user_prompt
            )
            
            # Track the tool usage with Handit.ai for observability
            if execution_id:
                tracker.track_node(
                    input={
                        "system_prompt": system_prompt,
                        "user_prompt": user_prompt,
                        "invoice_data_count": len(invoice_data),
                    },
                    output=response,
                    node_name="simple_report_action",
                    agent_name="invoice_copilot",
                    node_type="llm",
                    execution_id=execution_id
                )
            
            return {
                "success": True,
                "response": response,
                "request_type": "simple_report"
            }
            
        except Exception as e:
            logger.error(f"SimpleReportAction failed: {str(e)}")
            return {
                "success": False,
                "response": f"Error processing request: {str(e)}",
                "request_type": "simple_report"
            }

class OtherRequestAction:
    """
    Action class for handling requests unrelated to reports or data analysis.
    
    This action is used when users make requests that are outside the scope
    of business reporting and data visualization. It provides polite, professional
    responses that redirect users back to the system's core capabilities.
    
    The action explains the system's specialization and suggests ways to help
    with business reporting and data analysis tasks.
    
    Attributes:
        None (stateless action)
    
    Methods:
        execute: Process the other request and provide helpful redirection
    
    Example:
        >>> action = OtherRequestAction()
        >>> result = action.execute({
        ...     "user_request": "Can you help me write a poem?"
        ... })
        >>> print(result["response"][:50])
        "I specialize in business reporting and data analysis..."
    
    Common Use Cases:
        - General conversation outside business scope
        - Creative requests (poems, stories, etc.)
        - Technical questions unrelated to data analysis
        - Personal requests or casual conversation
    """
    
    def execute(self, params: Dict[str, Any], working_dir: str = "", execution_id: str = None) -> Dict[str, Any]:
        """
        Execute an other request and provide helpful redirection.
        
        This method handles requests that are outside the system's core
        capabilities. It provides polite, professional responses that explain
        the system's specialization and suggest relevant alternatives.
        
        Args:
            params (Dict[str, Any]): Parameters containing:
                - user_request (str): The user's request (outside business scope)
            working_dir (str): Working directory (not used for other requests)
            execution_id (str, optional): Handit.ai execution ID for tracking
        
        Returns:
            Dict[str, Any]: Result dictionary containing:
                - success (bool): Whether the operation was successful
                - response (str): Professional redirection response
                - request_type (str): Always "other_request"
        
        Raises:
            ValueError: If user_request parameter is missing
        
        Example:
            >>> result = action.execute({
            ...     "user_request": "Can you help me with my homework?"
            ... })
            >>> print(result["success"])
            True
            >>> print(result["response"][:50])
            "I specialize in business reporting and data analysis..."
        
        Note:
            - Provides professional, helpful responses
            - Explains system capabilities clearly
            - Suggests relevant alternatives
            - Tracks usage with Handit.ai for observability
            - Maintains positive user experience
        """
        user_request = params.get("user_request")
        if not user_request:
            raise ValueError("Missing user_request parameter")
        
        logger.info(f"OtherRequestAction: Processing other request: {user_request}")
        
        # Generate a professional prompt for the LLM to handle other requests
        # This ensures consistent, helpful responses that redirect appropriately
        system_prompt = f"""
You are a professional report specialist. The user has made a request that is not directly related to reports, graphs, or statistics data.

Please respond politely and professionally, explaining that you specialize in:
- Creating reports and data visualizations
- Analyzing invoice and financial data
- Generating charts and graphs with business insights
- Statistical analysis of business data

Gently redirect the conversation back to how you can help them with business reporting and data analysis tasks.

Be helpful and suggest specific ways you could assist them with business reporting needs.
"""
        
        # Call LLM to generate professional redirection response
        response = call_llm(
            system_prompt,
            user_request
        )
        
        # Track the tool usage with Handit.ai for observability
        if execution_id:
            tracker.track_node(
                input={
                    "system_prompt": system_prompt,
                    "user_prompt": user_request,
                },
                output=response,
                node_name="other_request_action",
                agent_name="invoice_copilot",
                node_type="llm",
                execution_id=execution_id
            )
        
        return {
            "success": True,
            "response": response,
            "request_type": "other_request"
        }

class EditFileAction:
    """
    Action class for creating and editing professional business reports with data visualizations.
    
    This is the most sophisticated action class, responsible for generating complete
    React components with professional charts and visualizations using the Recharts library.
    It processes real invoice data and creates comprehensive business reports with
    interactive charts, key metrics cards, and professional styling.
    
    The action completely replaces the target file (typically DynamicWorkspace.tsx)
    with a new implementation that includes:
    - Multiple chart types (BarChart, LineChart, PieChart, AreaChart)
    - Key metrics cards with real calculated values
    - Responsive design with professional styling
    - Interactive tooltips and legends
    - Real data extracted from processed invoice JSON files
    
    Attributes:
        None (stateless action)
    
    Methods:
        execute: Create or edit professional reports with visualizations
    
    Example:
        >>> action = EditFileAction()
        >>> result = action.execute({
        ...     "target_file": "DynamicWorkspace.tsx",
        ...     "instructions": "Create a bar chart of monthly expenses",
        ...     "chart_description": "Professional expense analysis with trends"
        ... })
        >>> print(result["success"])
        True
        >>> print(result["operations"])
        1
    
    Supported Chart Types:
        - BarChart: For comparing values across categories
        - LineChart: For showing trends over time
        - PieChart: For showing proportions and distributions
        - AreaChart: For cumulative data visualization
        - ResponsiveContainer: For responsive chart sizing
    
    Features:
        - Real data extraction from invoice JSON files
        - Professional business styling
        - Interactive tooltips and legends
        - Responsive design for all screen sizes
        - Key metrics cards with calculated values
        - Multiple chart layouts and configurations
    """
    
    def execute(self, params: Dict[str, Any], working_dir: str = "", execution_id: str = None) -> Dict[str, Any]:
        """
        Execute file editing to create professional business reports with visualizations.
        
        This method is the core of the report generation system. It takes user
        instructions and creates comprehensive React components with professional
        charts and visualizations. The method handles complex path resolution,
        loads real invoice data, generates LLM prompts for chart creation,
        parses YAML responses, and applies file changes with comprehensive
        error handling and observability tracking.
        
        Args:
            params (Dict[str, Any]): Parameters containing:
                - target_file (str): File to edit (typically DynamicWorkspace.tsx)
                - instructions (str): User's request for the report
                - chart_description (str, optional): Detailed chart requirements
                - real_data (str, optional): Pre-loaded invoice data
            working_dir (str): Working directory for file operations
            execution_id (str, optional): Handit.ai execution ID for tracking
        
        Returns:
            Dict[str, Any]: Result dictionary containing:
                - success (bool): Whether all operations were successful
                - operations (int): Number of operations performed
                - successful_operations (int): Number of successful operations
                - failed_operations (int): Number of failed operations
                - details (List[Dict]): Detailed results for each operation
                - reasoning (str): LLM reasoning for the changes
        
        Raises:
            ValueError: If required parameters are missing
            Various exceptions: For file reading, YAML parsing, and file writing errors
        
        Example:
            >>> result = action.execute({
            ...     "target_file": "DynamicWorkspace.tsx",
            ...     "instructions": "Create expense analysis with pie chart",
            ...     "chart_description": "Show expense breakdown by category"
            ... })
            >>> print(result["success"])
            True
            >>> print(result["operations"])
            1
        
        Note:
            - Completely replaces target file content
            - Uses only Recharts library for all visualizations
            - Extracts real data from processed invoice JSON files
            - Calculates actual metrics from invoice data
            - Provides comprehensive error handling and logging
            - Tracks all operations with Handit.ai for observability
            - Supports both complete file overwrite and partial edits
        """
        target_file = params.get("target_file")
        instructions = params.get("instructions")
        chart_description = params.get("chart_description", "")
        
        if not target_file:
            raise ValueError("Missing target_file parameter")
        if not instructions:
            raise ValueError("Missing instructions parameter")
        
        # Handle complex path resolution for frontend files
        # This ensures correct file paths regardless of working directory
        if working_dir and not os.path.isabs(target_file):
            # If working_dir is a relative path to frontend, resolve from project root
            if working_dir.startswith('frontend/'):
                # We're running from backend/, so go up one level to project root
                current_dir = os.getcwd()
                if current_dir.endswith('/backend'):
                    project_root = os.path.dirname(current_dir)
                else:
                    # If not running from backend subdirectory, assume current dir is project root
                    project_root = current_dir
                full_path = os.path.join(project_root, working_dir, target_file)
            else:
                full_path = os.path.join(working_dir, target_file)
        else:
            full_path = target_file
            
        # Normalize the path for consistent handling
        full_path = os.path.abspath(full_path)
        
        logger.info(f"EditFileAction: Resolved path from working_dir='{working_dir}' + target_file='{target_file}' -> '{full_path}'")
        
        logger.info(f"EditFileAction: Editing file {full_path}")
        
        # Read the current file content for context
        file_content, read_success = read_file(full_path)
        if not read_success:
            return {
                "success": False,
                "message": f"Failed to read file: {full_path}",
                "operations": 0
            }
        

        # Get real_data parameter if provided, otherwise load invoice data
        # This ensures we always have real data for chart generation
        real_data = params.get("real_data", "")
        if not real_data:
            invoice_data = load_invoice_data()
            real_data = json.dumps(invoice_data, indent=2)
        
        # Generate comprehensive prompt for the LLM to create professional reports with charts
        # This prompt ensures consistent, high-quality chart generation
        system_prompt = f"""
You are a professional business report specialist. Your goal is to create comprehensive professional reports, data-driven reports with interactive charts using ONLY Recharts library.

MANDATORY: ALWAYS REPLACE THE ENTIRE FILE CONTENT {file_content} - NO PARTIAL EDITS


Create a COMPLETE professional business report React component that REPLACES the entire file. Follow these guidelines:

1. MANDATORY: Replace the ENTIRE file from line 1 to any quantity of lines
2. ONLY use Recharts library for ALL charts (BarChart, LineChart, PieChart, AreaChart, ResponsiveContainer, etc.)
3. NEVER use Chart.js, D3, or any other chart library
4. Use ONLY the PROVIDED DATA - extract real totals, dates, amounts, any data you need from the PROVIDED DATA
5. Parse the invoice JSON data to create meaningful visualizations
6. Include key metrics cards with REAL calculated values from PROVIDED DATA
7. Create multiple professional charts showing different aspects of the data
8. Make all charts interactive with tooltips, legends, and responsive design
9. Use professional styling with proper colors and layout
10. You can include other info inside the same file, other components inside the same file but, don't use external libraries, only what is imported
11. The file MUST ALWAYS start with these exact imports:
   ```typescript
   import React from 'react';
   import {{ useApp }} from '@/contexts/AppContext';
   import {{ 
     BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
     XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
     ResponsiveContainer 
   }} from 'recharts';
   ```

CRITICAL REQUIREMENTS:
- Analize the PROVIDED DATA to accomplish the user request
- Extract REAL values from the provided invoice JSON data
- Calculate totals, averages, what ever you need, and insights from actual invoice data
- Create data arrays from the real invoice information
- NO sample/fake data - only real calculated values

Return a YAML object with COMPLETE file replacement:

```yaml
reasoning: |
  I am completely replacing the entire DynamicWorkspace.tsx file to create a professional business report.
  I will extract real data from the provided invoice JSON files including totals, dates, amounts, and the data I need.
  I will create multiple Recharts visualizations: BarChart for amounts, LineChart for trends, PieChart, any chart for company breakdown.
  I will calculate real metrics like total revenue, average invoice amount, number of invoices, any metric etc.
  The entire file will be replaced with a new implementation using real invoice data.

operations:
  - start_line: 1
    end_line: 50
    replacement: |
      import React from 'react';
      import {{ useApp }} from '@/contexts/AppContext';
      import {{ 
        BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
        XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
        ResponsiveContainer, AreaChart, Area 
      }} from 'recharts';

      // REAL DATA extracted from provided invoice files, each file is a different invoice
      const invoiceData = [
        // Extract and process REAL invoice data here
        // Calculate actual totals, companies, amounts from JSON
      ];

      export function DynamicWorkspace() {{
        const {{ state }} = useApp();
        const {{ workspaceContent }} = state;

        // Calculate REAL metrics from invoice data
        const totalExpenses = 0; // Calculate from real data
        const totalInvoices = 0; // Calculate from real data
        const averageAmount = 0; // Calculate from real data

        return (
          <div className="p-6 space-y-6">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Invoice Analysis Report</h1>
              <p className="text-gray-600 mt-2">Real data insights from processed invoices</p>
            </div>
            
            {{/* Key Metrics Cards with REAL values */}}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-700">Total Expenses</h3>
                <p className="text-3xl font-bold text-blue-600">${{totalExpenses.toFixed(2)}}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-700">Total Invoices</h3>
                <p className="text-3xl font-bold text-green-600">{{totalInvoices}}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-700">Average Amount</h3>
                <p className="text-3xl font-bold text-purple-600">${{averageAmount.toFixed(2)}}</p>
              </div>
            </div>
            
            {{/* Charts using Recharts with REAL data, include all charts you need */}}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Invoice Amounts</h3>
                <ResponsiveContainer width="100%" height={{350}}>
                  <BarChart data={{invoiceData}}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="invoice" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="amount" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Company Distribution</h3>
                <ResponsiveContainer width="100%" height={{350}}>
                  <PieChart>
                    <Pie
                      data={{invoiceData}}
                      dataKey="amount"
                      nameKey="company"
                      cx="50%"
                      cy="50%"
                      outerRadius={{80}}
                      fill="#8884d8"
                      label
                    >
                      {{invoiceData.map((entry, index) => (
                        <Cell key={{`cell-${{index}}`}} fill={{`#${{(index * 123456).toString(16).slice(0, 6)}}`}} />
                      ))}}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        );
      }}
```
      import React from 'react';
      import {{ useApp }} from '@/contexts/AppContext';
      import {{ 
        BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
        XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
        ResponsiveContainer, AreaChart, Area 
      }} from 'recharts';

      // REAL DATA extracted from provided invoice files, each file is a different invoice
      const invoiceData = [
        // Extract and process REAL invoice data here
        // Calculate actual totals, companies, amounts from JSON
      ];

      export function DynamicWorkspace() {{
        const {{ state }} = useApp();
        const {{ workspaceContent }} = state;

        // Calculate REAL metrics from invoice data
        const totalExpenses = 0; // Calculate from real data
        const totalInvoices = 0; // Calculate from real data
        const averageAmount = 0; // Calculate from real data

        return (
          <div className="p-6 space-y-6">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900">Invoice Analysis Report</h1>
              <p className="text-gray-600 mt-2">Real data insights from processed invoices</p>
            </div>
            
            {{/* Key Metrics Cards with REAL values */}}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-700">Total Expenses</h3>
                <p className="text-3xl font-bold text-blue-600">${{totalExpenses.toFixed(2)}}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-700">Total Invoices</h3>
                <p className="text-3xl font-bold text-green-600">{{totalInvoices}}</p>
              </div>
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold text-gray-700">Average Amount</h3>
                <p className="text-3xl font-bold text-purple-600">${{averageAmount.toFixed(2)}}</p>
              </div>
            </div>
            
            {{/* This is an example, you can create your own designs using recharts, and create any quantity of charts you need */}}
            {{/* Charts using Recharts with REAL data, include all charts you need */}}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Invoice Amounts</h3>
                <ResponsiveContainer width="100%" height={{350}}>
                  <BarChart data={{invoiceData}}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="invoice" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="amount" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-lg font-semibold mb-4">Company Distribution</h3>
                <ResponsiveContainer width="100%" height={{350}}>
                  <PieChart>
                    <Pie
                      data={{invoiceData}}
                      dataKey="amount"
                      nameKey="company"
                      cx="50%"
                      cy="50%"
                      outerRadius={{80}}
                      fill="#8884d8"
                      label
                    >
                      {{invoiceData.map((entry, index) => (
                        <Cell key={{`cell-${{index}}`}} fill={{`#${{(index * 123456).toString(16).slice(0, 6)}}`}} />
                      ))}}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {{/* You can add tables, descriptions, insights, etc., whatever you need, but only in the same language, and dont use external libraries, only what is imported */}}
        );
      }}
```

MANDATORY RULES:
- ALWAYS replace the entire file (start_line: 1, end_line: 200 or more lines as needed)
- Use ONLY real data extracted from the provided invoice JSON
- Calculate actual metrics from the invoice data
- NO sample/fake data whatsoever
- Create meaningful visualizations based on real invoice information
- The end_line should be a specific number (like 200, 300, etc.) not "any quantity"
"""
        

        user_prompt = f"""

        USER REQUEST: 
        {instructions}

        REPORT REQUIREMENTS:
        {chart_description}

        PROVIDED DATA:
        {real_data}
"""

        # Call LLM to analyze and generate chart code
        response = call_llm(
            system_prompt,
            user_prompt
        )
        logger.info(f"EditFileAction: LLM response length: {len(response)}")

        # Parse YAML response with comprehensive format support
        # This handles different ways LLMs might format YAML blocks
        yaml_content = ""
        if "```yaml" in response:
            yaml_blocks = response.split("```yaml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
                logger.info("EditFileAction: Found ```yaml block")
        elif "```yml" in response:
            yaml_blocks = response.split("```yml")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].split("```")[0].strip()
                logger.info("EditFileAction: Found ```yml block")
        elif "```" in response:
            # Try to extract from generic code block
            yaml_blocks = response.split("```")
            if len(yaml_blocks) > 1:
                yaml_content = yaml_blocks[1].strip()
                logger.info("EditFileAction: Found generic ``` block")
        else:
            # If no code blocks, try to use the entire response
            yaml_content = response.strip()
            logger.info("EditFileAction: Using entire response as YAML")
        
        logger.info(f"EditFileAction: YAML content length: {len(yaml_content)}")
        
        if not yaml_content:
            logger.error("EditFileAction: No YAML content found")
            return {
                "success": False,
                "message": "No YAML object found in LLM response",
                "operations": 0
            }
        
        try:
            # Parse YAML and validate structure
            decision = yaml.safe_load(yaml_content)
            logger.info(f"EditFileAction: YAML parsed successfully, keys: {list(decision.keys()) if decision else 'None'}")
            
            # Validate the required fields to ensure response quality
            if "reasoning" not in decision:
                logger.error("EditFileAction: Missing 'reasoning' in YAML")
                raise ValueError("Reasoning is missing")
            if "operations" not in decision:
                logger.error("EditFileAction: Missing 'operations' in YAML")
                raise ValueError("Operations are missing")
            
            # Ensure operations is a list for proper processing
            if not isinstance(decision["operations"], list):
                logger.error(f"EditFileAction: Operations is not a list: {type(decision['operations'])}")
                raise ValueError("Operations are not a list")
            
            logger.info(f"EditFileAction: Found {len(decision['operations'])} operations")
            
            # Validate each operation for required fields
            for i, op in enumerate(decision["operations"]):
                logger.info(f"EditFileAction: Operation {i+1} - start_line: {op.get('start_line', 'MISSING')}, end_line: {op.get('end_line', 'MISSING')}, replacement_length: {len(op.get('replacement', ''))}")
                if "start_line" not in op:
                    raise ValueError("start_line is missing")
                if "end_line" not in op:
                    raise ValueError("end_line is missing")
                if "replacement" not in op:
                    raise ValueError("replacement is missing")
                    
        except Exception as e:
            logger.error(f"EditFileAction: YAML parsing error: {str(e)}")
            return {
                "success": False,
                "message": f"Error parsing edit operations: {str(e)}",
                "operations": 0
            }
        
        # Apply changes with comprehensive error handling
        edit_operations = decision["operations"]
        reasoning = decision.get("reasoning", "")
        
        # Sort edit operations in descending order by start_line
        # This ensures that line numbers remain valid as we edit from bottom to top
        sorted_ops = sorted(edit_operations, key=lambda op: op["start_line"], reverse=True)
        
        # Apply each operation with detailed tracking
        successful_ops = 0
        failed_ops = 0
        details = []
        
        for i, op in enumerate(sorted_ops):
            logger.info(f"EditFileAction: Processing operation {i+1}: start_line={op['start_line']}, end_line={op['end_line']}")
            
            # Check if this is a complete file overwrite for better reliability
            is_complete_overwrite = (op["start_line"] == 1 and op["end_line"] >= 5)
            logger.info(f"EditFileAction: Is complete overwrite: {is_complete_overwrite}")
            
            if is_complete_overwrite:
                # Use complete file overwrite for better reliability
                logger.info(f"EditFileAction: Performing complete file overwrite: {full_path}")
                success, message = overwrite_entire_file(full_path, op["replacement"])
                logger.info(f"EditFileAction: Overwrite result - success: {success}, message: {message}")
            else:
                # Use line-by-line replacement for partial edits
                logger.info(f"EditFileAction: Performing partial edit: {full_path}")
                success, message = replace_file(
                    target_file=full_path,
                    start_line=op["start_line"],
                    end_line=op["end_line"],
                    content=op["replacement"]
                )
                logger.info(f"EditFileAction: Partial edit result - success: {success}, message: {message}")
    
            details.append({"success": success, "message": message})
            if success:
                successful_ops += 1
            else:
                failed_ops += 1
        
        all_successful = failed_ops == 0
        
        # Track the tool usage with Handit.ai for comprehensive observability
        if execution_id:
            tracker.track_node(
                input={
                    "target_file": target_file,
                    "chart_description": chart_description,
                    "operations_count": len(sorted_ops),
                    "successful_operations": successful_ops,
                    "failed_operations": failed_ops,
                    "system_prompt": system_prompt,
                    "user_prompt": user_prompt
                },
                output={
                    "success": all_successful,
                    "operations": len(sorted_ops),
                    "successful_operations": successful_ops,
                    "failed_operations": failed_ops,
                    "reasoning": reasoning, 
                    "llm_response": response
                },
                node_name="edit_file_action",
                agent_name="invoice_copilot",
                node_type="llm",
                execution_id=execution_id
            )
        
        return {
                "success": all_successful,
            "operations": len(sorted_ops),
            "successful_operations": successful_ops,
            "failed_operations": failed_ops,
            "details": details,
            "reasoning": reasoning
        }

class FormatResponseAction:
    """
    Action class for generating final user responses from execution history.
    
    This action is responsible for creating professional, informative responses
    that summarize what actions were performed and provide helpful next steps
    to the user. It takes the execution history and generates a coherent
    narrative that explains the workflow and results.
    
    The action uses LLM-based response generation to ensure professional,
    contextually appropriate responses that maintain a positive user experience.
    
    Attributes:
        None (stateless action)
    
    Methods:
        execute: Generate final response from execution history
    
    Example:
        >>> action = FormatResponseAction()
        >>> history = [
        ...     {"tool": "edit_file", "reason": "Create chart", "result": {"success": True}}
        ... ]
        >>> response = action.execute(history, "Create expense report", "exec_123")
        >>> print(response[:50])
        "I've successfully created a professional expense report..."
    
    Response Features:
        - Summarizes all actions performed
        - Explains the results clearly
        - Provides helpful next steps
        - Maintains professional tone
        - Addresses user's original request
    """
    
    def execute(self, history: List[Dict[str, Any]], user_query: str, execution_id: str = None) -> str:
        """
        Generate a final response summarizing the execution history.
        
        This method takes the complete execution history and generates a
        professional response that explains what was accomplished, addresses
        the user's original request, and provides helpful next steps.
        
        Args:
            history (List[Dict[str, Any]]): Complete execution history with all actions
            user_query (str): Original user request for context
            execution_id (str, optional): Handit.ai execution ID for tracking
        
        Returns:
            str: Professional response summarizing the workflow and results
        
        Example:
            >>> history = [
            ...     {"tool": "edit_file", "reason": "Create chart", "result": {"success": True}}
            ... ]
            >>> response = action.execute(history, "Show me expense trends")
            >>> print(response)
            "I've successfully created a professional expense analysis report..."
        
        Note:
            - Uses LLM for intelligent response generation
            - Maintains professional tone throughout
            - Provides actionable next steps
            - Tracks usage with Handit.ai for observability
            - Handles empty history gracefully
        """
        # If no history, return a generic message
        if not history:
            return "No actions were performed."
        
        # Generate a summary of actions for the LLM using the utility function
        actions_summary = format_history_summary(history, execution_id)
        
        # Prompt for the LLM to generate the final response
        system_prompt = f"""
You are a professional report and data visualization specialist. You have just performed a series of actions based on the 
user's request. Summarize what you did in a clear, helpful response to the user.

Here are the actions you performed:
{actions_summary}

Generate a professional and informative response that explains:
1. What actions were taken
2. Respond briefly to the user request
3. Any next steps the user might want to take

IMPORTANT: 
- Write as if you are directly speaking to the user
"""
        
        # Call LLM to generate professional response
        response = call_llm(system_prompt, user_query)


        
        logger.info(f"###### Final Response Generated ######\n{response}\n###### End of Response ######")
        

      # Track the llm usage with Handit.ai
        if execution_id:
            tracker.track_node(
                input={
                    "system_prompt": system_prompt,
                    "user_prompt": user_query
                },
                output=response,
                node_name="format_response_action",
                agent_name="invoice_copilot",
                node_type="llm",
                execution_id=execution_id
            )

        return response

# =============================================================================
# MAIN CODING AGENT ORCHESTRATOR
# =============================================================================

class CodingAgent:
    """
    Main Coding Agent Orchestrator for Intelligent Document Processing and Code Report Generation.
    
    This is the primary orchestrator class that manages the entire AI agent workflow.
    It coordinates between the decision agent, action classes, and response formatting
    to provide a seamless user experience for invoice processing and report generation.
    
    The agent implements a sophisticated multi-step workflow:
    1. User Request → MainDecisionAgent (analyzes and decides)
    2. Decision → Action Classes (execute specific tasks)
    3. Results → FormatResponseAction (generates final response)
    4. Handit.ai tracks all operations for observability
    
    The agent supports multiple action types:
    - edit_file: Create professional reports with data visualizations
    - simple_report: Answer specific data questions without visualizations
    - other_request: Handle non-report related requests
    - finish: Complete the workflow and generate final response
    
    Attributes:
        working_dir (str): Working directory for file operations
        main_agent (MainDecisionAgent): Decision-making agent
        actions (Dict): Mapping of tool names to action classes
        format_response (FormatResponseAction): Response formatting action
    
    Methods:
        __init__: Initialize the agent with working directory
        process_request: Main workflow orchestration method
    
    Example:
        >>> agent = CodingAgent(working_dir="frontend/src/components")
        >>> response = agent.process_request("Create a bar chart of expenses")
        >>> print(response[:50])
        "I've successfully created a professional expense analysis..."
    
    Features:
        - Multi-step decision making with YAML-based responses
        - Comprehensive error handling and logging
        - AI observability with Handit.ai integration
        - Support for multiple action types
        - Professional response generation
        - Infinite loop prevention with max iterations
    """
    
    def __init__(self, working_dir: str = ""):
        """
        Initialize the Coding Agent with working directory and action mappings.
        
        Args:
            working_dir (str): Working directory for file operations (default: "")
        
        Note:
            - Initializes all action classes for tool execution
            - Sets up Handit.ai integration for observability
            - Configures decision agent for intelligent tool selection
        """
        self.working_dir = working_dir
        self.main_agent = MainDecisionAgent()
        self.actions = {
            "edit_file": EditFileAction(),
            "simple_report": SimpleReportAction(),
            "other_request": OtherRequestAction(),
        }
        self.format_response = FormatResponseAction()
        
    def process_request(self, user_query: str, max_iterations: int = 3) -> str:
        """
        Process a user request using the complete AI agent workflow.
        
        This is the main entry point for the coding agent. It orchestrates
        the entire workflow from user request to final response, including
        decision making, action execution, error handling, and observability
        tracking with Handit.ai.
        
        The method implements a sophisticated loop that:
        1. Analyzes the user request with the decision agent
        2. Executes the selected action with appropriate parameters
        3. Tracks all operations for observability
        4. Handles errors gracefully with informative messages
        5. Prevents infinite loops with maximum iteration limits
        6. Generates professional final responses
        
        Args:
            user_query (str): The user's request or question
            max_iterations (int): Maximum number of tool calls to prevent infinite loops (default: 10)
        
        Returns:
            str: Final response summarizing the workflow and results
        
        Example:
            >>> agent = CodingAgent(working_dir="frontend/src/components")
            >>> response = agent.process_request("Create expense analysis with pie chart")
            >>> print(response)
            "I've successfully created a professional expense analysis report..."
        
        Note:
            - Starts and ends Handit.ai tracing for complete observability
            - Handles multiple action types with appropriate workflows
            - Provides comprehensive error handling and logging
            - Maintains execution history for context
            - Supports both simple and complex multi-step workflows
            - Prevents infinite loops with iteration limits
        """
        logger.info(f"CodingAgent: Processing request: {user_query}")
        
        # Start Handit.ai tracing for complete observability
        tracing_response = tracker.start_tracing(agent_name="invoice_copilot")
        execution_id = tracing_response.get("executionId")
        logger.info(f"Handit.ai tracing started with execution_id: {execution_id}")
        
        # Initialize shared state for the workflow
        shared_state = {
            "user_query": user_query,
            "history": [],
            "working_dir": self.working_dir,
            "execution_id": execution_id
        }
        
        # Main processing loop with iteration limits
        for iteration in range(max_iterations):
            logger.info(f"CodingAgent: Iteration {iteration + 1}/{max_iterations}")
            
            try:
                # Get decision from main agent with comprehensive context
                decision = self.main_agent.analyze_and_decide(
                    user_query=user_query,
                    execution_id=execution_id,
                    history=shared_state["history"],
                    working_dir=self.working_dir
                )
                
                tool = decision["tool"]
                reason = decision["reason"]
                params = decision.get("params", {})
                
                logger.info(f"CodingAgent: Selected tool: {tool}")
                
                # Add action to history for context and observability
                action_entry = {
                    "tool": tool,
                    "reason": reason,
                    "params": params,
                    "result": None,
                    "timestamp": datetime.now().isoformat()
                }
                shared_state["history"].append(action_entry)
                
                # Handle finish action - complete the workflow
                if tool == "finish":
                    logger.info("CodingAgent: Finishing and generating response")
                    final_response = self.format_response.execute(shared_state["history"], user_query, execution_id)
                    
                    # End Handit.ai tracing
                    try:
                        tracker.end_tracing(execution_id=execution_id, agent_name="invoice_copilot")
                        logger.info(f"Handit.ai tracing ended for execution_id: {execution_id}")
                    except Exception as e:
                        logger.error(f"Error ending Handit.ai tracing: {str(e)}")
                    
                    return final_response
                
                # Execute the selected action with comprehensive error handling
                if tool in self.actions:
                    try:
                        result = self.actions[tool].execute(params, self.working_dir, execution_id)
                        # Update result in history for context
                        shared_state["history"][-1]["result"] = result
                        logger.info(f"CodingAgent: Action {tool} completed successfully")
                        
                        # For simple_report and other_request, finish immediately after execution
                        # These actions provide direct responses and don't need further processing
                        if tool in ["simple_report", "other_request"]:
                            logger.info(f"CodingAgent: {tool} completed, finishing with direct response")
                            tracker.end_tracing(execution_id=execution_id, agent_name="invoice_copilot")
                            logger.info(f"Handit.ai tracing ended for execution_id: {execution_id}")
                            # Return the response directly from the action result
                            if result.get("success") and "response" in result:
                                return result["response"]
                            else:
                                return self.format_response.execute(shared_state["history"], user_query, execution_id)
                        
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
                # Add error to history for context and debugging
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
        # This prevents infinite loops and provides graceful degradation
        logger.warning(f"CodingAgent: Reached maximum iterations ({max_iterations})")
        final_response = self.format_response.execute(shared_state["history"], user_query, execution_id)
        
        # End Handit.ai tracing
        try:
            tracker.end_tracing(execution_id=execution_id, agent_name="invoice_copilot")
            logger.info(f"Handit.ai tracing ended for execution_id: {execution_id}")
        except Exception as e:
            logger.error(f"Error ending Handit.ai tracing: {str(e)}")
        
        return final_response

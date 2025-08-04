#!/usr/bin/env python3
"""
Test script for the simplified chart-focused coding agent.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chart_agent():
    """Test the chart-focused agent."""
    try:
        from agent import CodingAgent
        
        print("🎨 Testing Chart-Focused Coding Agent")
        print("=" * 50)
        
        # Initialize agent with workspace directory
        workspace_dir = "frontend/src/components/workspace"
        agent = CodingAgent(working_dir=workspace_dir)
        
        # Test chart creation requests
        test_requests = [
            "Create a bar chart showing monthly sales data",
            "Generate a pie chart for expense categories", 
            "Make a line chart showing revenue trends over time",
            "Create a dashboard with multiple charts showing business metrics"
        ]
        
        for i, request in enumerate(test_requests, 1):
            print(f"\n📊 Test {i}: {request}")
            print("-" * 40)
            
            try:
                response = agent.process_request(request, max_iterations=3)
                print("✅ Response:")
                print(response[:500] + "..." if len(response) > 500 else response)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
            
            print("\n" + "="*50)
        
        print("\n🎉 Chart agent testing complete!")
        
    except ImportError as e:
        print(f"❌ Could not import agent: {str(e)}")
        print("Make sure all dependencies are installed")

def show_agent_capabilities():
    """Show what the simplified agent can do."""
    print("\n🎨 Simplified Chart Agent Capabilities")
    print("=" * 50)
    
    capabilities = [
        "🔧 Primary Tool: edit_file",
        "   - Automatically reads current file content",
        "   - Creates/modifies React components with charts",
        "   - Uses Recharts, Chart.js, or similar libraries",
        "   - Includes sample data when needed",
        "",
        "🔍 Secondary Tool: semantic_search", 
        "   - Only used when specific data is needed",
        "   - Searches for relevant invoice/business data",
        "   - Helps find examples for chart creation",
        "",
        "🎯 Chart Types Supported:",
        "   - Bar charts, line charts, pie charts",
        "   - Area charts, scatter plots, dashboards",
        "   - Interactive tooltips and legends",
        "   - Responsive and mobile-friendly designs",
        "",
        "📁 Target Files:",
        "   - Primarily: DynamicWorkspace.tsx",
        "   - Can work with any React component file",
        "   - Creates complete functional components"
    ]
    
    for item in capabilities:
        print(f"  {item}")
    
    print("\n💡 Example Requests:")
    examples = [
        '"Create a bar chart showing quarterly revenue"',
        '"Make a pie chart for expense breakdown by category"', 
        '"Generate a line chart tracking monthly growth"',
        '"Build a dashboard with sales metrics"',
        '"Add an interactive chart showing invoice data"'
    ]
    
    for example in examples:
        print(f"  • {example}")

if __name__ == "__main__":
    print("🚀 Chart Agent Testing Suite")
    print("=" * 60)
    
    show_agent_capabilities()
    
    # Check if user wants to run tests
    try:
        user_input = input("\n❓ Run chart creation tests? (y/n): ").lower().strip()
        if user_input in ['y', 'yes']:
            test_chart_agent()
        else:
            print("👋 Skipping tests. Use the agent in your chat interface!")
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
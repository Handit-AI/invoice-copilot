#!/usr/bin/env python3
"""
Debug the complete agent workflow to find why DynamicWorkspace.tsx isn't being edited.
"""

import os
import sys
import json
from datetime import datetime

def debug_path_resolution():
    """Debug path resolution from backend to frontend."""
    print("🔍 DEBUGGING PATH RESOLUTION")
    print("=" * 50)
    
    # Current setup
    current_dir = os.getcwd()
    workspace_dir = "frontend/src/components/workspace"
    target_file = "DynamicWorkspace.tsx"
    
    print(f"📁 Current working directory: {current_dir}")
    print(f"🎯 Workspace directory: {workspace_dir}")
    print(f"📄 Target file: {target_file}")
    
    # Test the exact resolution logic from agent.py
    if workspace_dir and not os.path.isabs(target_file):
        if workspace_dir.startswith('frontend/'):
            if current_dir.endswith('/backend'):
                project_root = os.path.dirname(current_dir)
            else:
                project_root = current_dir
            full_path = os.path.join(project_root, workspace_dir, target_file)
        else:
            full_path = os.path.join(workspace_dir, target_file)
    else:
        full_path = target_file
    
    full_path = os.path.abspath(full_path)
    
    print(f"🔗 Resolved full path: {full_path}")
    print(f"📂 File exists: {os.path.exists(full_path)}")
    
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            print(f"✅ Successfully read {len(content)} characters")
            print("📖 First 100 characters:")
            print(f"'{content[:100]}...'")
            return full_path, True
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return full_path, False
    else:
        print("❌ File does not exist at resolved path")
        
        # Show what's actually in the directories
        dirs_to_check = [
            os.path.dirname(full_path),
            os.path.join(project_root, "frontend"),
            os.path.join(project_root, "frontend", "src"),
            os.path.join(project_root, "frontend", "src", "components"),
            os.path.join(project_root, "frontend", "src", "components", "workspace")
        ]
        
        for dir_path in dirs_to_check:
            if os.path.exists(dir_path):
                print(f"📋 Contents of {dir_path}:")
                try:
                    for item in os.listdir(dir_path):
                        print(f"  - {item}")
                except Exception as e:
                    print(f"  Error listing: {e}")
            else:
                print(f"❌ Directory does not exist: {dir_path}")
        
        return full_path, False

def debug_agent_imports():
    """Debug agent imports."""
    print("\n🔍 DEBUGGING AGENT IMPORTS")
    print("=" * 50)
    
    try:
        print("📦 Importing agent...")
        from agent import CodingAgent
        print("✅ Agent imported successfully")
        
        print("🤖 Creating agent instance...")
        agent = CodingAgent(working_dir="frontend/src/components/workspace")
        print("✅ Agent instance created successfully")
        
        print("🔧 Available actions:")
        for action_name in agent.actions.keys():
            print(f"  - {action_name}")
        
        return agent, True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, False

def debug_semantic_search():
    """Debug semantic search functionality."""
    print("\n🔍 DEBUGGING SEMANTIC SEARCH")
    print("=" * 50)
    
    try:
        from utils.semantic_search import semantic_search
        print("✅ Semantic search imported")
        
        # Test a simple search
        print("🔍 Testing semantic search...")
        success, results = semantic_search("invoice data test", namespace="", top_k=3)
        
        print(f"📊 Search success: {success}")
        print(f"📋 Results count: {len(results) if results else 0}")
        
        if results:
            print("📄 First result preview:")
            print(f"  {results[0]}")
        
        return success
        
    except Exception as e:
        print(f"❌ Semantic search error: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_edit_action():
    """Debug the edit file action."""
    print("\n🔍 DEBUGGING EDIT FILE ACTION")
    print("=" * 50)
    
    try:
        from agent import EditFileAction
        print("✅ EditFileAction imported")
        
        edit_action = EditFileAction()
        
        # Test parameters
        params = {
            "target_file": "DynamicWorkspace.tsx",
            "instructions": "Add a simple comment for testing",
            "chart_description": "Add comment: // AI Agent Test",
            "real_data": "No real data for this test"
        }
        
        workspace_dir = "frontend/src/components/workspace"
        
        print(f"🔧 Testing edit action with params: {params}")
        print(f"📁 Working directory: {workspace_dir}")
        
        result = edit_action.execute(params, workspace_dir)
        
        print(f"📊 Edit result: {json.dumps(result, indent=2)}")
        
        return result.get("success", False)
        
    except Exception as e:
        print(f"❌ Edit action error: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_main_agent():
    """Debug the main decision agent."""
    print("\n🔍 DEBUGGING MAIN DECISION AGENT")
    print("=" * 50)
    
    try:
        from agent import MainDecisionAgent
        print("✅ MainDecisionAgent imported")
        
        main_agent = MainDecisionAgent()
        
        # Test a simple decision
        user_query = "Create a simple bar chart"
        history = []
        
        print(f"💭 Testing decision for query: '{user_query}'")
        
        decision = main_agent.analyze_and_decide(user_query, history)
        
        print(f"🎯 Decision result: {json.dumps(decision, indent=2)}")
        
        return decision
        
    except Exception as e:
        print(f"❌ Main agent error: {e}")
        import traceback
        traceback.print_exc()
        return None

def run_full_debug():
    """Run complete debugging workflow."""
    print("🚀 COMPLETE AGENT DEBUGGING")
    print("=" * 60)
    print(f"⏰ Started at: {datetime.now()}")
    print()
    
    # Step 1: Path resolution
    target_path, path_ok = debug_path_resolution()
    
    # Step 2: Agent imports
    agent, import_ok = debug_agent_imports()
    
    # Step 3: Semantic search
    search_ok = debug_semantic_search()
    
    # Step 4: Edit action
    edit_ok = debug_edit_action()
    
    # Step 5: Main agent
    decision = debug_main_agent()
    
    # Summary
    print("\n" + "=" * 60)
    print("🏁 DEBUGGING SUMMARY")
    print("=" * 60)
    print(f"📂 Path Resolution: {'✅ OK' if path_ok else '❌ FAILED'}")
    print(f"🤖 Agent Import: {'✅ OK' if import_ok else '❌ FAILED'}")
    print(f"🔍 Semantic Search: {'✅ OK' if search_ok else '❌ FAILED'}")
    print(f"✏️ Edit Action: {'✅ OK' if edit_ok else '❌ FAILED'}")
    print(f"🧠 Main Agent: {'✅ OK' if decision else '❌ FAILED'}")
    
    if all([path_ok, import_ok, search_ok, edit_ok, decision]):
        print("\n🎉 ALL COMPONENTS WORKING!")
        print("💡 The issue might be in the frontend-backend communication.")
    else:
        print("\n⚠️ SOME COMPONENTS FAILING!")
        print("💡 Fix the failing components above.")
    
    print(f"\n⏰ Completed at: {datetime.now()}")

if __name__ == "__main__":
    run_full_debug()
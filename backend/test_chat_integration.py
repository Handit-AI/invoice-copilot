#!/usr/bin/env python3
"""
Test script for chat integration with the coding agent.
This script demonstrates how the chat endpoint works with the agent.
"""

import os
import sys
import requests
import json

# Backend URL
BACKEND_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test that the backend is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {str(e)}")
        return False

def test_chat_endpoint(message: str, workspace_dir: str = "frontend/src/components/workspace"):
    """Test the chat endpoint with a message."""
    try:
        print(f"\n📤 Sending message: '{message}'")
        print(f"📁 Workspace directory: {workspace_dir}")
        
        payload = {
            "message": message,
            "workspace_dir": workspace_dir,
            "max_iterations": 5
        }
        
        response = requests.post(
            f"{BACKEND_URL}/api/chat/message",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat response received")
            print(f"Success: {data.get('success', False)}")
            print(f"Response: {data.get('response', 'No response')[:200]}...")
            if data.get('error'):
                print(f"Error: {data.get('error')}")
            return data
        else:
            print(f"❌ Chat request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling chat endpoint: {str(e)}")
        return None

def run_test_suite():
    """Run a series of tests to verify the integration."""
    
    print("🚀 Testing Chat Integration with Coding Agent")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n🔍 Test 1: Backend Health Check")
    if not test_health_endpoint():
        print("❌ Backend is not running. Start it with: python main.py")
        return
    
    # Test 2: Simple file listing
    print("\n🔍 Test 2: List Workspace Files")
    test_chat_endpoint("List all files in the workspace directory")
    
    # Test 3: Read a specific file
    print("\n🔍 Test 3: Read Specific File")
    test_chat_endpoint("Read the DynamicWorkspace.tsx file")
    
    # Test 4: Search for patterns
    print("\n🔍 Test 4: Search Code Patterns")
    test_chat_endpoint("Search for all React components that use useState")
    
    # Test 5: Edit request
    print("\n🔍 Test 5: Simple Edit Request")
    test_chat_endpoint("Add a comment to the top of DynamicWorkspace.tsx explaining what it does")
    
    print("\n🎉 Integration testing complete!")
    print("\n💡 Tips for using the chat:")
    print("  - Ask to 'list files' to see what's available")
    print("  - Ask to 'read [filename]' to view file content")
    print("  - Ask to 'search for [pattern]' to find code")
    print("  - Ask to 'edit [filename] to [description]' to modify files")
    print("  - Ask to 'create a component' to generate new code")

def interactive_chat():
    """Interactive chat session for testing."""
    print("\n💬 Interactive Chat Mode")
    print("Type your messages (or 'quit' to exit):")
    print("-" * 40)
    
    while True:
        try:
            message = input("\n🧑 You: ").strip()
            if message.lower() in ['quit', 'exit', 'q']:
                break
            if not message:
                continue
                
            print("🤖 Assistant: Processing...")
            result = test_chat_endpoint(message)
            
            if result and result.get('success'):
                print(f"🤖 Assistant: {result.get('response', 'No response')}")
            else:
                print("🤖 Assistant: Sorry, I encountered an error.")
                
        except KeyboardInterrupt:
            break
    
    print("\n👋 Chat session ended.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Test chat integration with coding agent')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive chat mode')
    parser.add_argument('--message', '-m', type=str,
                       help='Send a single message')
    
    args = parser.parse_args()
    
    if args.message:
        # Single message mode
        print("🚀 Single Message Test")
        print("=" * 30)
        if test_health_endpoint():
            test_chat_endpoint(args.message)
    elif args.interactive:
        # Interactive mode
        if test_health_endpoint():
            interactive_chat()
        else:
            print("❌ Backend not available for interactive mode")
    else:
        # Full test suite
        run_test_suite()
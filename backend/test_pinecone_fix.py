#!/usr/bin/env python3
"""
Test the fixed Pinecone semantic search.
"""

import os
from utils.semantic_search import semantic_search

def test_semantic_search():
    """Test the semantic search functionality."""
    print("🔍 TESTING FIXED SEMANTIC SEARCH")
    print("=" * 40)
    
    # Check environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "invoice-copilot")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"🔑 Pinecone API Key: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"📊 Index Name: {index_name}")
    print(f"🤖 OpenAI API Key: {'✅ Set' if openai_key else '❌ Not set'}")
    
    if not api_key:
        print("❌ Please set PINECONE_API_KEY environment variable")
        return False
    
    if not openai_key:
        print("❌ Please set OPENAI_API_KEY environment variable")
        return False
    
    # Test semantic search
    print(f"\n🔍 Testing semantic search...")
    
    test_query = "invoice expenses data"
    print(f"📝 Query: '{test_query}'")
    
    try:
        success, results = semantic_search(
            query=test_query,
            namespace="",  # No namespace
            top_k=5
        )
        
        print(f"✅ Search completed: {success}")
        print(f"📋 Results found: {len(results) if results else 0}")
        
        if results:
            print("\n📄 Sample results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. ID: {result.get('id', 'N/A')}")
                print(f"     Score: {result.get('score', 0.0):.4f}")
                metadata = result.get('metadata', {})
                if metadata:
                    print(f"     Metadata: {metadata}")
                print()
        
        return success
        
    except Exception as e:
        print(f"❌ Error during semantic search: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_with_fixed_search():
    """Test the agent with the fixed semantic search."""
    print("\n🤖 TESTING AGENT WITH FIXED SEARCH")
    print("=" * 40)
    
    try:
        from agent import CodingAgent
        
        agent = CodingAgent(working_dir="frontend/src/components/workspace")
        
        # Test a simple request that should trigger semantic search
        simple_request = "Create a chart showing revenue data"
        print(f"📝 Request: '{simple_request}'")
        
        # Just test the first decision
        decision = agent.main_agent.analyze_and_decide(simple_request, [])
        
        print(f"🎯 Decision: {decision.get('tool', 'NONE')}")
        print(f"💭 Reason: {decision.get('reason', 'NO REASON')[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 PINECONE FIX TEST")
    print("=" * 50)
    
    # Test 1: Semantic search
    search_ok = test_semantic_search()
    
    # Test 2: Agent decision making
    agent_ok = test_agent_with_fixed_search()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    print(f"🔍 Semantic Search: {'✅ OK' if search_ok else '❌ FAILED'}")
    print(f"🤖 Agent Integration: {'✅ OK' if agent_ok else '❌ FAILED'}")
    
    if search_ok and agent_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("💡 The semantic search should now work correctly.")
    else:
        print("\n⚠️ SOME TESTS FAILED!")
        print("💡 Check the error messages above and environment variables.")
        
    print("\n📋 Next steps:")
    print("1. Make sure your environment variables are set:")
    print("   export PINECONE_API_KEY='your-key'")
    print("   export OPENAI_API_KEY='your-key'")
    print("   export PINECONE_INDEX_NAME='invoice-copilot'")
    print("2. Test the full agent workflow")
    print("3. Try the frontend chat integration")
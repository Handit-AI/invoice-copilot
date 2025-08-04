#!/usr/bin/env python3
"""
Test script for semantic search functionality.
This script demonstrates how to use the semantic search tool with the coding agent.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import CodingAgent

def test_semantic_search():
    """Test semantic search functionality with various queries."""
    
    # Initialize the coding agent
    agent = CodingAgent()
    
    print("🔍 Testing Semantic Search Tool")
    print("=" * 50)
    
    # Test cases
    test_queries = [
        {
            "query": "Find documents about invoice processing and payments",
            "description": "Basic semantic search for invoice-related content"
        },
        {
            "query": "Search for 'historical monuments and structures' in category 'history'",
            "description": "Category-filtered search"
        },
        {
            "query": "Look for payment information in invoice_001.pdf",
            "description": "File-specific search"
        },
        {
            "query": "Find all documents containing billing and tax information",
            "description": "Multiple keyword semantic search"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n📋 Test {i}: {test['description']}")
        print(f"Query: {test['query']}")
        print("-" * 30)
        
        try:
            # Process the query with the agent
            response = agent.process_request(test['query'], max_iterations=5)
            print("✅ Response:")
            print(response)
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
        
        print("\n" + "="*50)

def test_direct_semantic_search():
    """Test semantic search functions directly."""
    
    print("\n🔧 Testing Direct Semantic Search Functions")
    print("=" * 50)
    
    try:
        from utils.semantic_search import semantic_search, format_search_results
        
        # Test basic search
        print("\n📍 Basic Search Test:")
        success, results = semantic_search(
            query="Famous historical structures and monuments",
            namespace="example-namespace",
            top_k=5
        )
        
        if success:
            print(f"✅ Found {len(results)} results")
            formatted = format_search_results(results)
            print(formatted)
        else:
            print("❌ Search failed")
            
    except ImportError as e:
        print(f"❌ Import error: {str(e)}")
        print("Make sure Pinecone is installed: pip install pinecone-client")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def show_usage_examples():
    """Show usage examples for the semantic search tool."""
    
    print("\n📚 Usage Examples")
    print("=" * 50)
    
    examples = [
        {
            "title": "Basic Semantic Search",
            "code": '''
# Using the agent
agent = CodingAgent()
response = agent.process_request("Find documents about machine learning")

# Direct function call
from utils.semantic_search import semantic_search
success, results = semantic_search("machine learning algorithms", top_k=5)
'''
        },
        {
            "title": "Category-Filtered Search",
            "code": '''
# Using the agent with natural language
response = agent.process_request("Search for 'payment processing' in finance category")

# Direct function call
from utils.semantic_search import search_by_category
success, results = search_by_category("payment processing", "finance", top_k=3)
'''
        },
        {
            "title": "File-Specific Search",
            "code": '''
# Using the agent
response = agent.process_request("Find invoice total in invoice_001.pdf")

# Direct function call
from utils.semantic_search import search_by_filename
success, results = search_by_filename("invoice total", "invoice_001.pdf")
'''
        }
    ]
    
    for example in examples:
        print(f"\n🔹 {example['title']}:")
        print(example['code'])

if __name__ == "__main__":
    print("🚀 Semantic Search Testing Suite")
    print("=" * 60)
    
    # Show environment info
    print(f"📂 Working Directory: {os.getcwd()}")
    print(f"🐍 Python Path: {sys.executable}")
    
    # Check environment variables
    api_key = os.getenv("PINECONE_API_KEY")
    index_name = os.getenv("PINECONE_INDEX_NAME", "invoice-copilot")
    
    print(f"🔑 Pinecone API Key: {'✅ Set' if api_key else '❌ Not Set'}")
    print(f"📊 Index Name: {index_name}")
    
    if not api_key:
        print("\n⚠️  Warning: PINECONE_API_KEY environment variable not set!")
        print("   Set it with: export PINECONE_API_KEY='your-api-key'")
    
    # Run tests
    test_semantic_search()
    test_direct_semantic_search()
    show_usage_examples()
    
    print("\n🎉 Testing Complete!")
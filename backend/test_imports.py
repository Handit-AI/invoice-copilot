#!/usr/bin/env python3
"""
Test script to verify all imports work correctly.
"""

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing Agent Imports")
    print("=" * 30)
    
    try:
        print("📦 Testing YAML import...")
        import yaml
        print("✅ YAML imported successfully")
    except ImportError as e:
        print(f"❌ YAML import failed: {e}")
        return False
    
    try:
        print("📦 Testing utils imports...")
        from utils.call_llm import call_llm
        print("✅ call_llm imported")
        
        from utils.read_file import read_file
        print("✅ read_file imported")
        
        from utils.replace_file import replace_file
        print("✅ replace_file imported")
        
        from utils.semantic_search import semantic_search, format_search_results
        print("✅ semantic_search imported")
        
    except ImportError as e:
        print(f"❌ Utils import failed: {e}")
        return False
    
    try:
        print("🤖 Testing CodingAgent import...")
        from agent import CodingAgent
        print("✅ CodingAgent imported successfully")
        
        # Test creating an instance
        agent = CodingAgent(working_dir="test")
        print("✅ CodingAgent instance created")
        
    except ImportError as e:
        print(f"❌ CodingAgent import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ CodingAgent creation failed: {e}")
        return False
    
    print("\n🎉 All imports successful!")
    return True

def test_main_import():
    """Test that main.py can import the agent."""
    print("\n🔗 Testing main.py integration...")
    try:
        # Simulate what main.py does
        from agent import CodingAgent
        agent_available = True
        print("✅ main.py can import CodingAgent")
        return True
    except ImportError as e:
        print(f"❌ main.py import would fail: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Import Testing Suite")
    print("=" * 40)
    
    success1 = test_imports()
    success2 = test_main_import()
    
    if success1 and success2:
        print("\n🎊 All tests passed! Ready to start the backend.")
        print("\n📋 Next steps:")
        print("  1. python main.py")
        print("  2. Test chat integration")
    else:
        print("\n❌ Some imports failed. Check the error messages above.")
        print("\n💡 Make sure to install dependencies:")
        print("  python install_dependencies.py")
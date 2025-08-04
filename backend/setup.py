#!/usr/bin/env python3
"""
Setup script for FastAPI backend with virtual environment
"""
import subprocess
import sys
import os

def create_venv():
    """Create virtual environment"""
    print("📦 Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the pip command for the current platform"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "pip")
    else:  # Linux/Mac
        return os.path.join("venv", "bin", "pip")

def install_dependencies():
    """Install dependencies in virtual environment"""
    print("📥 Installing dependencies...")
    pip_command = get_pip_command()
    
    try:
        subprocess.check_call([pip_command, "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def show_instructions():
    """Show instructions to activate venv and run server"""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    
    if os.name == 'nt':  # Windows
        print("To activate the virtual environment:")
        print("  venv\\Scripts\\activate")
        print("\nTo run the server:")
        print("  python main.py")
        print("\nOr run directly:")
        print("  venv\\Scripts\\python main.py")
    else:  # Linux/Mac
        print("To activate the virtual environment:")
        print("  source venv/bin/activate")
        print("\nTo run the server:")
        print("  python main.py")
        print("\nOr run directly:")
        print("  venv/bin/python main.py")
    
    print("\n🌐 Server will be available at: http://localhost:8000")
    print("🏥 Health endpoint: http://localhost:8000/health")
    print("📚 API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    print("🚀 Setting up FastAPI backend with virtual environment...")
    
    if create_venv() and install_dependencies():
        show_instructions()
    else:
        print("❌ Setup failed. Please check the errors above.")
        sys.exit(1)
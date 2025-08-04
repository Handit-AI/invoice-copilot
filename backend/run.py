#!/usr/bin/env python3
"""
Run script for FastAPI backend using virtual environment
"""
import subprocess
import sys
import os

def get_python_command():
    """Get the python command for the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join("venv", "Scripts", "python")
    else:  # Linux/Mac
        return os.path.join("venv", "bin", "python")

def run_server():
    """Run the FastAPI server using virtual environment"""
    python_command = get_python_command()
    
    if not os.path.exists(python_command):
        print("❌ Virtual environment not found!")
        print("Please run: python3 setup.py")
        sys.exit(1)
    
    print("🚀 Starting FastAPI server...")
    print("📍 Server: http://localhost:8000")
    print("🏥 Health: http://localhost:8000/health")
    print("📚 Docs: http://localhost:8000/docs")
    print("\n💡 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([python_command, "main.py"])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

if __name__ == "__main__":
    run_server()
#!/usr/bin/env python3
"""
Run the invoice-copilot backend with proper environment setup.
This script activates the virtual environment and starts the server.
"""

import subprocess
import sys
import os
from pathlib import Path

def get_python_command():
    """Get the appropriate Python command for the virtual environment."""
    if os.name == 'nt':  # Windows
        return ".venv\\Scripts\\python.exe"
    else:  # Unix/Linux/macOS
        return ".venv/bin/python"

def check_virtual_environment():
    """Check if virtual environment exists and has required packages."""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("   Run: python install_dependencies.py")
        return False
    
    python_cmd = get_python_command()
    
    # Test if we can import yaml (the missing dependency)
    result = subprocess.run([python_cmd, "-c", "import yaml"], capture_output=True)
    if result.returncode != 0:
        print("❌ Missing dependencies!")
        print("   Run: python install_dependencies.py")
        return False
    
    print("✅ Virtual environment ready")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    python_cmd = get_python_command()
    
    print("🚀 Starting FastAPI backend...")
    print("   Server will be available at: http://localhost:8000")
    print("   Health check: http://localhost:8000/health")
    print("   Chat endpoint: http://localhost:8000/api/chat/message")
    print("   Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the main.py file with the virtual environment Python
        subprocess.run([python_cmd, "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Backend stopped by user")
        return True
    
    return True

def main():
    """Main execution function."""
    print("🤖 Invoice Copilot Backend Runner")
    print("=" * 40)
    
    # Change to backend directory if not already there
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"📁 Working directory: {backend_dir.absolute()}")
    
    # Check virtual environment
    if not check_virtual_environment():
        sys.exit(1)
    
    # Start the backend
    if not start_backend():
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Install dependencies for the invoice-copilot backend.
This script handles virtual environment setup and dependency installation.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    print(f"   Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success!")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    
    print("✅ Python version is compatible")
    return True

def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist."""
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    print("🔄 Creating virtual environment...")
    return run_command([sys.executable, "-m", "venv", ".venv"], "Creating virtual environment")

def get_pip_command():
    """Get the appropriate pip command for the current OS."""
    if os.name == 'nt':  # Windows
        return [".venv\\Scripts\\python.exe", "-m", "pip"]
    else:  # Unix/Linux/macOS
        return [".venv/bin/python", "-m", "pip"]

def install_dependencies():
    """Install dependencies from requirements.txt."""
    pip_cmd = get_pip_command()
    
    # Upgrade pip first
    upgrade_success = run_command(
        pip_cmd + ["install", "--upgrade", "pip"],
        "Upgrading pip"
    )
    
    if not upgrade_success:
        print("⚠️ Could not upgrade pip, continuing anyway...")
    
    # Install requirements
    return run_command(
        pip_cmd + ["install", "-r", "requirements.txt"],
        "Installing dependencies from requirements.txt"
    )

def verify_installation():
    """Verify that key modules can be imported."""
    pip_cmd = get_pip_command()
    
    test_imports = [
        "import fastapi",
        "import uvicorn", 
        "import yaml",
        "import pinecone",
        "import openai"
    ]
    
    print("🔍 Verifying installation...")
    
    for import_statement in test_imports:
        module_name = import_statement.split()[1]
        test_cmd = pip_cmd[:-2] + ["-c", import_statement]  # Remove "pip" from command
        
        result = subprocess.run(test_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {module_name}")
        else:
            print(f"   ❌ {module_name} - {result.stderr.strip()}")

def main():
    """Main installation process."""
    print("🚀 Invoice Copilot Backend Setup")
    print("=" * 40)
    
    # Change to backend directory if not already there
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    print(f"📁 Working directory: {backend_dir.absolute()}")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to create virtual environment")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        print("\n💡 Troubleshooting tips:")
        print("   - Make sure you have internet connection")
        print("   - Try running: pip install --upgrade pip")
        print("   - Check if any dependencies have conflicts")
        sys.exit(1)
    
    # Verify installation
    verify_installation()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("   1. Activate virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("      .venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS  
        print("      source .venv/bin/activate")
    
    print("   2. Set environment variables (optional):")
    print("      export PINECONE_API_KEY='your-api-key'")
    print("      export OPENAI_API_KEY='your-api-key'")
    print("   3. Start the backend:")
    print("      python main.py")
    
    print("\n🔗 Test the setup:")
    print("   curl http://localhost:8000/health")

if __name__ == "__main__":
    main()
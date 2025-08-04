#!/usr/bin/env python3
"""
Script to update requirements.txt from current environment
"""
import subprocess
import sys

def update_requirements():
    """Generate requirements.txt from current environment"""
    print("📦 Updating requirements.txt from current environment...")
    
    try:
        # Get all installed packages
        result = subprocess.run([sys.executable, "-m", "pip", "freeze"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            # Write to requirements.txt
            with open("requirements.txt", "w") as f:
                f.write(result.stdout)
            print("✅ requirements.txt updated successfully!")
            print(f"📋 Found {len(result.stdout.strip().split())} packages")
        else:
            print("❌ Failed to get installed packages")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_requirements() 
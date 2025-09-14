#!/usr/bin/env python3
"""
Install dependencies and test the backend
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main function."""
    print("🚀 Installing dependencies and testing backend...")
    print("=" * 50)
    
    # Uninstall problematic packages
    print("🧹 Cleaning up problematic packages...")
    run_command("pip uninstall -y langchain langchain-openai langchain-community", "Uninstalling LangChain packages")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies")
        return False
    
    # Test imports
    print("🧪 Testing imports...")
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import openai
        import qdrant_client
        print("✅ All core imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test backend import
    print("🧪 Testing backend import...")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from backend.main import app
        print("✅ Backend import successful")
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        return False
    
    print("=" * 50)
    print("🎉 All tests passed! Backend should work now.")
    print("\nNext steps:")
    print("1. Start Qdrant: python start_qdrant.py")
    print("2. Run backend: python run_backend.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


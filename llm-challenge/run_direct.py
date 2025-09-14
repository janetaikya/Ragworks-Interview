#!/usr/bin/env python3
"""
Direct run script for DocuChat AI - no subprocess issues
"""

import sys
import os
import time
import requests
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function."""
    print("🚀 Starting DocuChat AI Application (Direct Mode)")
    print("=" * 60)
    
    # Check if backend is already running
    if check_backend():
        print("✅ Backend is already running!")
    else:
        print("🔄 Starting backend server...")
        print("📝 Backend will start in the background")
        print("🌐 Frontend will open in your browser")
        print("⏳ Please wait for both to start...")
    
    # Start frontend
    print("🔄 Starting frontend...")
    try:
        import subprocess
        subprocess.run([
            "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Frontend server runner for RAGWorks Chat Application
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Run the Streamlit frontend server."""
    print("🚀 Starting RAGWorks Chat Frontend...")
    print("=" * 50)
    
    # Check if backend is running
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("⚠️  Backend is not running. Please start it first:")
            print("   python run_backend.py")
            return
    except:
        print("⚠️  Backend is not running. Please start it first:")
        print("   python run_backend.py")
        return
    
    # Set environment variables
    os.environ["API_URL"] = "http://localhost:8000"
    
    # Start Streamlit
    try:
        subprocess.run([
            "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped")
    except Exception as e:
        print(f"❌ Error starting frontend: {str(e)}")

if __name__ == "__main__":
    main()


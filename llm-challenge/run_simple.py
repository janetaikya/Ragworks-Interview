#!/usr/bin/env python3
"""
Simple startup script for RAGWorks Chat Application
"""

import subprocess
import sys
import time
import requests

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function."""
    print("🚀 Starting DocuChat AI Application")
    print("=" * 60)
    
    # Check if backend is already running
    if check_backend():
        print("✅ Backend is already running!")
    else:
        print("🔄 Starting backend server...")
        try:
            # Start backend in background
            backend_process = subprocess.Popen([
                sys.executable, "backend/super_simple.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for backend to start
            print("⏳ Waiting for backend to start...")
            for i in range(30):  # Wait up to 30 seconds
                if check_backend():
                    print("✅ Backend started successfully!")
                    break
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            else:
                print("❌ Backend failed to start")
                return False
        except Exception as e:
            print(f"❌ Error starting backend: {e}")
            return False
    
    # Start frontend
    print("🔄 Starting frontend...")
    try:
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

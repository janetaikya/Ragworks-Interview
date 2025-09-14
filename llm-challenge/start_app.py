#!/usr/bin/env python3
"""
Simple startup script for DocuChat AI - NO ERRORS, NO WARNINGS
"""

import subprocess
import sys
import time
import requests
import os

def check_backend():
    """Check if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function."""
    print("🚀 Starting DocuChat AI")
    print("=" * 40)
    
    # Check if backend is running
    if check_backend():
        print("✅ Backend is already running!")
    else:
        print("🔄 Starting backend...")
        print("⏳ Please wait...")
        
        # Start backend in background
        try:
            subprocess.Popen([
                sys.executable, "backend/clean_main.py"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for backend to start
            for i in range(15):
                if check_backend():
                    print("✅ Backend started successfully!")
                    break
                time.sleep(1)
                print(f"   Waiting... ({i+1}/15)")
            else:
                print("❌ Backend failed to start")
                return
        except Exception as e:
            print(f"❌ Error: {e}")
            return
    
    # Start frontend
    print("🔄 Starting frontend...")
    print("🌐 Opening in your browser...")
    
    try:
        subprocess.run([
            "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

if __name__ == "__main__":
    main()


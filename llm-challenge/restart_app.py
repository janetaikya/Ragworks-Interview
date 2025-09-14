#!/usr/bin/env python3
"""
Restart DocuChat AI Application
"""

import subprocess
import sys
import os
import signal
import time

def kill_processes():
    """Kill any running processes on ports 8000 and 8501."""
    try:
        # Kill process on port 8000 (backend)
        subprocess.run(["netstat", "-ano"], capture_output=True, text=True)
        subprocess.run(["taskkill", "/F", "/IM", "python.exe"], capture_output=True)
        print("🔄 Killed existing processes")
    except:
        print("⚠️  Could not kill existing processes (this is okay)")

def main():
    """Main function."""
    print("🔄 Restarting DocuChat AI Application")
    print("=" * 50)
    
    # Kill existing processes
    kill_processes()
    
    # Wait a moment
    time.sleep(2)
    
    # Start the app
    print("🚀 Starting fresh...")
    subprocess.run([sys.executable, "run_simple.py"])

if __name__ == "__main__":
    main()


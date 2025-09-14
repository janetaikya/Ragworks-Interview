import os
import sys
import time
import subprocess
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return its output."""
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        stdout, stderr = process.communicate(timeout=10)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Process timed out"
    except Exception as e:
        return -1, "", str(e)

def main():
    # First, kill any existing processes
    print("Stopping existing processes...")
    if os.name == 'nt':  # Windows
        run_command('taskkill /f /im python.exe 2>nul')
        run_command('taskkill /f /im streamlit.exe 2>nul')
    else:
        run_command('pkill -f "python"')
        run_command('pkill -f "streamlit"')
    
    time.sleep(2)
    
    # Start backend
    print("\nStarting backend server...")
    backend_process = subprocess.Popen(
        [sys.executable, "backend/minimal.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give backend time to start
    time.sleep(2)
    
    # Start frontend
    print("\nStarting frontend...")
    frontend_process = subprocess.Popen(
        ["streamlit", "run", "frontend/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("\nBoth services started!")
    print("Frontend URL: http://localhost:8501")
    print("Backend URL: http://localhost:8000")
    print("\nPress Ctrl+C to stop both services")
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend_process.kill()
        frontend_process.kill()

if __name__ == "__main__":
    main()
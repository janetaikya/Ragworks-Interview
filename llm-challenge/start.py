#!/usr/bin/env python3
"""
Startup script for the DocuChat AI application
"""
import os
import sys
import time
import signal
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info >= (3, 12):
        print("⚠️ Python 3.12 may have compatibility issues. Consider using Python 3.9-3.11")
    return True

def check_environment():
    """Check if all required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env
    
    required_vars = {
        "SECRET_KEY": "JWT secret key",
        "GROQ_API_KEY": "GROQ API key for chat responses",
    }
    
    # Verify all required variables are present
    missing = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({description})")
    
    if missing:
        print("❌ Missing required environment variables:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    print("✅ Environment variables loaded")
    return True

def check_database():
    """Check if database exists and is accessible."""
    try:
        import sqlite3
        conn = sqlite3.connect("chat_app.db")
        conn.execute("SELECT 1")
        conn.close()
        print("✅ Database check passed")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def is_port_in_use(port):
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def wait_for_service(url, timeout=30):
    """Wait for a service to become available."""
    import requests
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
        print(f"Waiting for service at {url}... ({int(time.time() - start_time)}s)")
    return False

def main():
    print("\n=== DocuChat AI System Check ===\n")
    
    # Check Python version
    if not check_python_version():
        return
    
    # Check environment variables
    if not check_environment():
        return
    
    # Check database
    if not check_database():
        return
    
    # Kill any existing processes
    if sys.platform == 'win32':
        os.system('taskkill /f /im python.exe 2>nul')
        os.system('taskkill /f /im streamlit.exe 2>nul')
    else:
        os.system('pkill -f "python"')
        os.system('pkill -f "streamlit"')
    
    time.sleep(2)
    
    # Check if ports are available
    if is_port_in_use(8000):
        print("❌ Port 8000 is already in use")
        return
    if is_port_in_use(8501):
        print("❌ Port 8501 is already in use")
        return
    
    print("\n=== Starting Services ===\n")
    
    # Start backend
    print("Starting backend server...")
    backend_cmd = [sys.executable, "backend/clean_main.py"]
    backend_process = subprocess.Popen(
        backend_cmd,
        env={**os.environ, "PYTHONPATH": str(Path.cwd())},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for backend
    if not wait_for_service("http://localhost:8000/health"):
        print("❌ Backend failed to start")
        backend_process.kill()
        return
    
    print("✅ Backend started successfully")
    
    # Start frontend
    print("\nStarting frontend...")
    frontend_cmd = ["streamlit", "run", "frontend/app.py"]
    frontend_process = subprocess.Popen(
        frontend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for frontend
    if not wait_for_service("http://localhost:8501"):
        print("❌ Frontend failed to start")
        backend_process.kill()
        frontend_process.kill()
        return
    
    print("✅ Frontend started successfully")
    
    print("\n=== System is Ready! ===")
    print("\nYou can now access:")
    print("- Frontend: http://localhost:8501")
    print("- Backend API: http://localhost:8000")
    print("\nPress Ctrl+C to stop all services\n")
    
    def signal_handler(signum, frame):
        print("\nShutting down services...")
        backend_process.kill()
        frontend_process.kill()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down services...")
        backend_process.kill()
        frontend_process.kill()

if __name__ == "__main__":
    main()
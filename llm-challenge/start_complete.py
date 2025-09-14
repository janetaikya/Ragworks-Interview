import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def print_status(message, success=True):
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def check_api_key():
    from dotenv import load_dotenv
    load_dotenv()
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        print_status("GROQ API key not found!", False)
        return False
    print_status("GROQ API key found")
    return True

def check_database():
    try:
        from backend.app.db import get_db
        from sqlalchemy import text
        db = next(get_db())
        db.execute(text("SELECT 1"))
        print_status("Database connection successful")
        return True
    except Exception as e:
        print_status(f"Database error: {str(e)}", False)
        return False

def start_backend():
    try:
        # Kill any existing Python processes more selectively
        if os.name == 'nt':  # Windows
            os.system('taskkill /f /im python.exe /fi "WINDOWTITLE eq run_backend.py" 2>nul')
        else:  # Linux/Mac
            os.system('pkill -f "python run_backend.py"')
        
        time.sleep(2)
        
        # Start backend with output capture
        backend_process = subprocess.Popen(
            [sys.executable, "run_backend.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(5)  # Give backend time to start
        
        # Check if backend is running
        try:
            response = requests.get("http://localhost:8000/health")
            if response.status_code == 200:
                print_status("Backend started successfully")
                return True
            else:
                print_status("Backend health check failed", False)
                return False
        except requests.exceptions.ConnectionError:
            print_status("Could not connect to backend", False)
            return False
            
    except Exception as e:
        print_status(f"Error starting backend: {str(e)}", False)
        return False

def start_frontend():
    try:
        # Start frontend
        frontend_cmd = ["streamlit", "run", "frontend/app.py"]
        frontend_process = subprocess.Popen(frontend_cmd)
        time.sleep(5)  # Give frontend time to start
        
        print_status("Frontend started")
        return True
    except Exception as e:
        print_status(f"Error starting frontend: {str(e)}", False)
        return False

def main():
    print("\n=== DocuChat AI System Check ===\n")
    
    # First kill any existing processes
    if os.name == 'nt':  # Windows
        os.system('taskkill /f /im python.exe /fi "WINDOWTITLE eq run_backend.py" 2>nul')
        os.system('taskkill /f /im streamlit.exe 2>nul')
    else:  # Linux/Mac
        os.system('pkill -f "python run_backend.py"')
        os.system('pkill -f "streamlit run"')
    
    time.sleep(2)
    
    # Check environment
    if not check_api_key():
        print("\n❌ System check failed: Missing API key")
        return
        
    if not check_database():
        print("\n❌ System check failed: Database error")
        return
    
    print("\n=== Starting Services ===\n")
    
    # Start backend
    if not start_backend():
        print("\n❌ System check failed: Backend error")
        return
        
    # Start frontend
    if not start_frontend():
        print("\n❌ System check failed: Frontend error")
        return
        
    print("\n=== System Successfully Started ===")
    print("\nYou can now access:")
    print("- Frontend: http://localhost:8501")
    print("- Backend API: http://localhost:8000")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down services...")
        if os.name == 'nt':  # Windows
            os.system('taskkill /f /im python.exe')
        else:  # Linux/Mac
            os.system('pkill -f "python run_backend.py"')
            os.system('pkill -f "streamlit run"')

if __name__ == "__main__":
    main()
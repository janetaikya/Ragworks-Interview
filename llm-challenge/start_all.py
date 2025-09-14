import subprocess
import sys
import time

# Start Qdrant (if needed)
def start_qdrant():
    try:
        subprocess.run(["docker", "start", "qdrant-ragworks"], check=True)
    except Exception:
        subprocess.run([
            "docker", "run", "-d", "--name", "qdrant-ragworks", "-p", "6333:6333", "qdrant/qdrant"
        ], check=True)
    print("Qdrant started or already running.")

# Start backend
backend = subprocess.Popen([sys.executable, "run_backend.py"])
time.sleep(5)  # Wait for backend to start

# Start frontend
frontend = subprocess.Popen([sys.executable, "run_frontend.py"])

print("Both backend and frontend are running!")
print("Frontend: http://localhost:8501\nBackend: http://localhost:8000\nSwagger: http://localhost:8000/docs")

# Wait for both to finish
try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    print("Shutting down...")
    backend.terminate()
    frontend.terminate()

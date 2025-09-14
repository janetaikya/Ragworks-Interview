#!/usr/bin/env python3
"""
Qdrant startup script for RAGWorks Chat Application
"""

import subprocess
import time
import requests
import sys

def check_qdrant_running():
    """Check if Qdrant is already running."""
    try:
        response = requests.get("http://localhost:6333/collections", timeout=5)
        return response.status_code == 200
    except:
        return False

def start_qdrant():
    """Start Qdrant using Docker."""
    print("🚀 Starting Qdrant vector database...")
    
    if check_qdrant_running():
        print("✅ Qdrant is already running!")
        return True
    
    try:
        # Start Qdrant container
        process = subprocess.Popen([
            "docker", "run", "-d",
            "--name", "qdrant-ragworks",
            "-p", "6333:6333",
            "qdrant/qdrant"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("✅ Qdrant container started successfully!")
            
            # Wait for Qdrant to be ready
            print("⏳ Waiting for Qdrant to be ready...")
            for i in range(30):  # Wait up to 30 seconds
                if check_qdrant_running():
                    print("✅ Qdrant is ready!")
                    return True
                time.sleep(1)
                print(f"   Waiting... ({i+1}/30)")
            
            print("⚠️  Qdrant started but may not be ready yet")
            return True
        else:
            print(f"❌ Failed to start Qdrant: {stderr.decode()}")
            return False
            
    except FileNotFoundError:
        print("❌ Docker not found. Please install Docker first.")
        print("   Visit: https://docs.docker.com/get-docker/")
        return False
    except Exception as e:
        print(f"❌ Error starting Qdrant: {str(e)}")
        return False

def stop_qdrant():
    """Stop Qdrant container."""
    print("🛑 Stopping Qdrant...")
    try:
        subprocess.run(["docker", "stop", "qdrant-ragworks"], check=True)
        subprocess.run(["docker", "rm", "qdrant-ragworks"], check=True)
        print("✅ Qdrant stopped successfully!")
        return True
    except subprocess.CalledProcessError:
        print("⚠️  Qdrant container not found or already stopped")
        return True
    except Exception as e:
        print(f"❌ Error stopping Qdrant: {str(e)}")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "stop":
        stop_qdrant()
    else:
        start_qdrant()

if __name__ == "__main__":
    main()


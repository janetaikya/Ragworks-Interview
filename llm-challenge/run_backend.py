#!/usr/bin/env python3
"""
Backend server runner for RAGWorks Chat Application
"""

import os
import sys
import uvicorn
from pathlib import Path





# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run the FastAPI backend server."""
    print("🚀 Starting RAGWorks Chat Backend...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. Please run setup.py first.")
        return
    
    # Check if Qdrant is running
    try:
        import requests
        response = requests.get("http://localhost:6333/collections", timeout=5)
        if response.status_code != 200:
            print("⚠️  Qdrant is not running. Please start it first:")
            print("   docker run -p 6333:6333 qdrant/qdrant")
            return
    except:
        print("⚠️  Qdrant is not running. Please start it first:")
        print("   docker run -p 6333:6333 qdrant/qdrant")
        return
    
    # Start the server (use backend.app.main:app for full features)
    try:
        uvicorn.run(
            "backend.app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Backend server stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {str(e)}")

if __name__ == "__main__":
    main()

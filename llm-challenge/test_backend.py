#!/usr/bin/env python3
"""
Test script for the backend
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test all imports."""
    print("🧪 Testing imports...")
    
    try:
        # Test basic imports
        import fastapi
        import uvicorn
        import sqlalchemy
        import openai
        import qdrant_client
        print("✅ Basic imports successful")
        
        # Test config
        from config import DATABASE_URL, OPENAI_API_KEY
        print("✅ Config import successful")
        
        # Test database
        from backend.app.db import engine
        from backend.app.models import Base
        print("✅ Database imports successful")
        
        # Test backend modules
        from backend.app import auth, rag, routes
        print("✅ Backend module imports successful")
        
        # Test main app
        from backend.main import app
        print("✅ Main app import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database connection."""
    print("🧪 Testing database...")
    
    try:
        from backend.app.db import engine
        from backend.app.models import Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing RAGWorks Backend...")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return False
    
    # Test database
    if not test_database():
        print("❌ Database tests failed")
        return False
    
    print("=" * 50)
    print("🎉 All tests passed! Backend is ready to run.")
    print("\nTo start the backend:")
    print("python run_backend.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


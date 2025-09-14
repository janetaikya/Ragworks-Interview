#!/usr/bin/env python3
"""
Test script to verify DocuChat AI is working
"""

import requests
import time
import sys

def test_backend():
    """Test if backend is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print("❌ Backend not responding properly")
            return False
    except:
        print("❌ Backend is not running")
        return False

def test_registration():
    """Test user registration."""
    try:
        data = {
            "email": "test@example.com",
            "password": "test123",
            "full_name": "Test User"
        }
        response = requests.post("http://localhost:8000/auth/register", json=data)
        if response.status_code == 200:
            print("✅ Registration works")
            return True
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False

def test_login():
    """Test user login."""
    try:
        data = {
            "username": "test@example.com",
            "password": "test123"
        }
        response = requests.post("http://localhost:8000/auth/login", json=data)
        if response.status_code == 200:
            print("✅ Login works")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing DocuChat AI Application")
    print("=" * 40)
    
    # Test backend
    if not test_backend():
        print("\n❌ Backend is not running. Please run: python run_simple.py")
        return False
    
    # Test registration
    if not test_registration():
        print("\n❌ Registration test failed")
        return False
    
    # Test login
    if not test_login():
        print("\n❌ Login test failed")
        return False
    
    print("\n🎉 All tests passed! Your app is working perfectly!")
    print("\n🌐 Open your browser to: http://localhost:8501")
    print("📧 Login with: test@example.com / test123")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


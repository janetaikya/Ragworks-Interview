#!/usr/bin/env python3
"""
View users in the database
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.app.db import SessionLocal
from backend.app.models import User, Conversation, Message, Document

def view_users():
    """View all users in the database."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        
        print("👥 Users in Database:")
        print("=" * 50)
        
        if not users:
            print("No users found in the database.")
            return
        
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.full_name}")
            print(f"Active: {user.is_active}")
            print(f"Verified: {user.is_verified}")
            print(f"Created: {user.created_at}")
            print("-" * 30)
        
        print(f"\nTotal users: {len(users)}")
        
    except Exception as e:
        print(f"Error viewing users: {e}")
    finally:
        db.close()

def view_conversations():
    """View all conversations."""
    db = SessionLocal()
    try:
        conversations = db.query(Conversation).all()
        
        print("\n💬 Conversations in Database:")
        print("=" * 50)
        
        if not conversations:
            print("No conversations found.")
            return
        
        for conv in conversations:
            print(f"ID: {conv.id}")
            print(f"Title: {conv.title}")
            print(f"User ID: {conv.user_id}")
            print(f"Created: {conv.created_at}")
            print("-" * 30)
        
        print(f"\nTotal conversations: {len(conversations)}")
        
    except Exception as e:
        print(f"Error viewing conversations: {e}")
    finally:
        db.close()

def view_documents():
    """View all documents."""
    db = SessionLocal()
    try:
        documents = db.query(Document).all()
        
        print("\n📄 Documents in Database:")
        print("=" * 50)
        
        if not documents:
            print("No documents found.")
            return
        
        for doc in documents:
            print(f"ID: {doc.id}")
            print(f"Title: {doc.title}")
            print(f"Type: {doc.file_type}")
            print(f"User ID: {doc.user_id}")
            print(f"Processed: {doc.is_processed}")
            print(f"Chunks: {doc.chunk_count}")
            print(f"Created: {doc.created_at}")
            print("-" * 30)
        
        print(f"\nTotal documents: {len(documents)}")
        
    except Exception as e:
        print(f"Error viewing documents: {e}")
    finally:
        db.close()

def main():
    """Main function."""
    print("🔍 RAGWorks Database Viewer")
    print("=" * 50)
    
    try:
        view_users()
        view_conversations()
        view_documents()
        
        print("\n✅ Database viewer completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


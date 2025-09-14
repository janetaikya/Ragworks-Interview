#!/usr/bin/env python3
"""
Simplified main entry point for RAGWorks Chat Backend
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import uuid
import openai
from datetime import datetime

from config import DATABASE_URL, DEBUG, FRONTEND_URL, OPENAI_API_KEY

# Initialize OpenAI
openai.api_key = OPENAI_API_KEY

# Database setup
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sources: List[str] = []
    confidence_score: float = 0.0

# Database models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    file_type = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Simple authentication
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Simple password verification (in production, use bcrypt)
    return plain_password == hashed_password

def get_password_hash(password: str) -> str:
    # Simple password hashing (in production, use bcrypt)
    return password

# Initialize FastAPI app
app = FastAPI(
    title="DocuChat AI",
    description="AI-powered chat with document processing",
    version="1.0.0",
    debug=DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Simple in-memory storage for demo
active_users = {}
active_conversations = {}

@app.get("/")
def root():
    return {"message": "DocuChat AI Backend", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Authentication endpoints
@app.post("/auth/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    if get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "User registered successfully", "user_id": db_user.id}

@app.post("/auth/login")
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, login_data.username)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate simple token (in production, use JWT)
    token = f"token_{user.id}_{datetime.utcnow().timestamp()}"
    active_users[token] = user
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me")
def get_current_user(token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active
    }

# Chat endpoints
@app.post("/api/chat", response_model=ChatResponse)
def chat(chat_data: ChatMessage, token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    
    # Get or create conversation
    if chat_data.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_data.conversation_id,
            Conversation.user_id == user.id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = Conversation(title="New Chat", user_id=user.id)
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_data.message
    )
    db.add(user_message)
    db.commit()
    
    # Generate AI response
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": chat_data.message}
            ],
            max_tokens=500
        )
        ai_response = response.choices[0].message.content
    except Exception as e:
        ai_response = f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    # Save AI response
    ai_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=ai_response
    )
    db.add(ai_message)
    db.commit()
    
    return ChatResponse(
        message=ai_response,
        conversation_id=conversation.id,
        sources=[],
        confidence_score=0.8
    )

# Conversation endpoints
@app.get("/api/conversations")
def get_conversations(token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    conversations = db.query(Conversation).filter(
        Conversation.user_id == user.id
    ).order_by(Conversation.created_at.desc()).all()
    
    return [
        {
            "id": conv.id,
            "title": conv.title,
            "user_id": conv.user_id,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.created_at.isoformat()
        }
        for conv in conversations
    ]

@app.get("/api/conversations/{conversation_id}/messages")
def get_messages(conversation_id: int, token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]

# Document endpoints
@app.post("/rag/upload")
async def upload_document(file: UploadFile = File(...), token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    
    # Save file
    file_path = f"uploads/{uuid.uuid4()}_{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Create document record
    document = Document(
        title=file.filename,
        content=f"Content of {file.filename}",
        file_type=file.filename.split('.')[-1],
        user_id=user.id
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return {
        "id": document.id,
        "title": document.title,
        "file_type": document.file_type,
        "file_size": len(content),
        "is_processed": True,
        "chunk_count": 1,
        "created_at": document.created_at.isoformat(),
        "updated_at": document.created_at.isoformat()
    }

@app.get("/rag/documents")
def get_documents(token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    documents = db.query(Document).filter(Document.user_id == user.id).all()
    
    return [
        {
            "id": doc.id,
            "title": doc.title,
            "file_type": doc.file_type,
            "file_size": len(doc.content),
            "is_processed": True,
            "chunk_count": 1,
            "created_at": doc.created_at.isoformat(),
            "updated_at": doc.created_at.isoformat()
        }
        for doc in documents
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=DEBUG)

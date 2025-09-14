#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from typing import List, Optional
import uuid
import requests
from datetime import datetime
from config import GEMINI_API_KEY, DATABASE_URL

# ---------------- Database ----------------
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

Base.metadata.create_all(bind=engine)

# ---------------- FastAPI App ----------------
app = FastAPI(
    title="DocuChat AI",
    description="AI-powered chat with document processing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501", "http://localhost:8502", "http://127.0.0.1:8502"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ---------------- Utilities ----------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

active_users = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def call_gemini_api(prompt: str) -> str:
    url = "https://api.gemini.example/v1/chat/completions"  # Replace with actual
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "gemini-1.0", "messages":[{"role":"system","content":"You are helpful AI."},{"role":"user","content":prompt}],"max_tokens":500}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    return f"Error: {response.status_code}"

# ---------------- Routers ----------------

# Import routers
from backend.app import rag, auth, routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(routes.router, prefix="/api", tags=["API"])
app.include_router(rag.router, prefix="/rag", tags=["RAG & Documents"])

# ---------------- Health ----------------
@app.get("/")
def root(): return {"message": "DocuChat AI Backend", "status": "running"}

@app.get("/health")
def health_check(): 
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if engine else "disconnected",
        "api_keys": {
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY"))
        }
    }

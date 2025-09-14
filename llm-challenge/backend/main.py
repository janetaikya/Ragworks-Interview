#!/usr/bin/env python3
"""
Main entry point for RAGWorks Chat Backend
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine

from config import DATABASE_URL, DEBUG, FRONTEND_URL
from backend.app.db import engine
from backend.app.models import Base
from backend.app import auth, rag, routes

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="RAGWorks Chat Application",
    description="A real-world chat application with RAG, LLM integration, and document processing",
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

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(routes.router, prefix="/api", tags=["Chat & Conversations"])
app.include_router(rag.router, prefix="/rag", tags=["RAG & Documents"])

# Mount static files for uploads
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {
        "message": "Welcome to RAGWorks Chat Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "healthy",
        "service": "ragworks-chat-backend",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=DEBUG)


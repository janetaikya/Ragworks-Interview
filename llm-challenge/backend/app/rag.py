def search_documents(query, user_id):
    """Search for relevant documents for the given query"""
    import sys
    from backend.app.main import get_db
    from sqlalchemy.orm import Session
    from backend.app.models import Document
    
    try:
        # Get database session
        db = next(get_db())
        
        # Get all documents for the user
        documents = db.query(Document).filter(Document.user_id == user_id).all()
        
        if not documents:
            print("[DEBUG] No documents found for user", file=sys.stderr)
            return []
            
        # For now, return all documents (we'll implement proper search later)
        results = []
        for doc in documents:
            results.append({
                "content": doc.content,
                "metadata": {
                    "vector_id": str(doc.id),
                    "title": doc.title,
                    "file_type": doc.file_type
                },
                "score": 1.0  # Placeholder score
            })
            
        print(f"[DEBUG] Found {len(results)} documents", file=sys.stderr)
        return results
        
    except Exception as e:
        print(f"[ERROR] Error in search_documents: {str(e)}", file=sys.stderr)
        return []  # Return empty list on error
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import uuid
import os
from datetime import datetime
from backend.app.main import get_db, active_users, Document  # Import shared objects
import requests
from config import GROQ_API_KEY, GROQ_MODEL
# --- Groq LLM integration ---
def generate_response(prompt, context_docs, conversation_history):
    """Generate a response using Groq API with fallback handling"""
    import sys
    
    if not GROQ_API_KEY:
        print("[ERROR] GROQ_API_KEY not set", file=sys.stderr)
        return "I apologize, but I'm not configured properly. Please contact support."
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Enhanced system prompt
    system_prompt = """You are a helpful AI assistant specialized in analyzing documents and providing accurate information.
If you find relevant information in the context, use it to answer the question.
If you don't find relevant information, say so clearly and provide a general response.
Always be clear, concise, and accurate."""

    # Process context documents
    context_text = ""
    if context_docs:
        context_pieces = []
        for doc in context_docs:
            if isinstance(doc, dict) and "content" in doc:
                context_pieces.append(doc["content"])
        context_text = "\n\nContext:\n" + "\n---\n".join(context_pieces)

    # Prepare conversation messages
    messages = [
        {"role": "system", "content": system_prompt + context_text},
    ]
    
    # Add conversation history
    if conversation_history:
        for msg in conversation_history[-5:]:  # Only use last 5 messages for context
            if isinstance(msg, dict) and "role" in msg and "content" in msg:
                messages.append({"role": msg["role"], "content": msg["content"]})

    # Add current prompt
    messages.append({"role": "user", "content": prompt})

    # Prepare API request
    payload = {
        "model": GROQ_MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        print(f"[DEBUG] Sending request to Groq API with payload: {payload}", file=sys.stderr)
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            response_json = response.json()
            if "choices" in response_json and response_json["choices"]:
                return response_json["choices"][0]["message"]["content"]
            else:
                print(f"[ERROR] Unexpected Groq API response structure: {response_json}", file=sys.stderr)
                return "I encountered an error processing your request. Please try again."
        else:
            print(f"[ERROR] Groq API error: {response.status_code} - {response.text}", file=sys.stderr)
            return f"I'm having trouble generating a response (Error {response.status_code}). Please try again in a moment."
            
    except Exception as e:
        print(f"[ERROR] Exception in generate_response: {str(e)}", file=sys.stderr)
        return "I encountered an error while processing your request. Please try again."

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), token: str = None, db: Session = Depends(get_db)):
    if not token or token not in active_users:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = active_users[token]
    
    # Save file
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
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

@router.get("/documents")
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

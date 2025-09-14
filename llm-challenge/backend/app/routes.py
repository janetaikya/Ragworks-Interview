from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.db import get_db
from backend.app.models import User, Conversation, Message, Document
from backend.app.schemas import (
    ConversationCreate, ConversationResponse, MessageCreate, MessageResponse,
    ChatRequest, ChatResponse
)
from backend.app.auth import get_current_active_user
from backend.app.rag import search_documents, generate_response

router = APIRouter()

@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    db_conversation = Conversation(
        title=conversation.title,
        user_id=current_user.id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    return conversations

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation

@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all messages in a conversation."""
    # Verify conversation belongs to user
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    return messages

@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response with enhanced error handling."""
    import sys
    
    # Log request details
    print(f"[DEBUG] === New Chat Request ===", file=sys.stderr)
    print(f"[DEBUG] User: {current_user.email}", file=sys.stderr)
    print(f"[DEBUG] Message: {chat_request.message}", file=sys.stderr)
    print(f"[DEBUG] Conversation ID: {chat_request.conversation_id}", file=sys.stderr)
    
    # Validate request data
    if not hasattr(chat_request, 'message') or not chat_request.message:
        raise HTTPException(status_code=400, detail="Message field is required")
    
    if not isinstance(chat_request.message, str):
        raise HTTPException(status_code=400, detail="Message must be a string")
        
    if len(chat_request.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    try:
        # Validate message
        if not chat_request.message or not isinstance(chat_request.message, str):
            raise HTTPException(status_code=400, detail="Message must be a non-empty string")

        # Validate conversation_id if provided
        if chat_request.conversation_id is not None:
            try:
                conv_id = int(chat_request.conversation_id)
                conversation = db.query(Conversation).filter(
                    Conversation.id == conv_id,
                    Conversation.user_id == current_user.id
                ).first()
                if not conversation:
                    raise HTTPException(status_code=404, detail="Conversation not found")
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="conversation_id must be a valid integer or null")
        else:
            # Create new conversation
            conversation = Conversation(
                title="New Chat",
                user_id=current_user.id
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=chat_request.message
        )
        db.add(user_message)
        db.commit()
        # Search for relevant documents
        context_docs = search_documents(chat_request.message, current_user.id)
        # Get conversation history
        conversation_history = []
        messages = db.query(Message).filter(
            Message.conversation_id == conversation.id
        ).order_by(Message.created_at.desc()).limit(10).all()
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(messages)
        ]
        # Generate AI response
        ai_response = generate_response(
            chat_request.message, 
            context_docs, 
            conversation_history
        )
        # Calculate confidence score
        confidence_score = max([doc["score"] for doc in context_docs]) if context_docs else 0.0
        # Prepare sources
        sources = [doc["metadata"].get("vector_id", "") for doc in context_docs]
        # Save AI response
        ai_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            sources=",".join(sources),
            confidence_score=confidence_score
        )
        db.add(ai_message)
        db.commit()
        return ChatResponse(
            message=ai_response,
            conversation_id=conversation.id,
            sources=sources,
            confidence_score=confidence_score
        )
    except Exception as e:
        print(f"[ERROR] /api/chat: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete all messages in the conversation
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    # Delete the conversation
    db.delete(conversation)
    db.commit()
    
    return {"message": "Conversation deleted successfully"}

@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}
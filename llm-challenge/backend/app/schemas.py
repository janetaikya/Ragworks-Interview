from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Conversation Schemas
class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class ConversationResponse(ConversationBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Message Schemas
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    conversation_id: int

class MessageResponse(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime
    sources: Optional[str] = None
    confidence_score: Optional[float] = None

    class Config:
        from_attributes = True

# Document Schemas
class DocumentBase(BaseModel):
    title: str

class DocumentCreate(DocumentBase):
    file_type: str

class DocumentResponse(DocumentBase):
    id: int
    content: str
    file_path: str
    file_type: str
    file_size: int
    user_id: int
    is_processed: bool
    chunk_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Chat Schemas
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    
    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Message must not be empty')
        return v.strip()
        
    @validator('conversation_id')
    def conversation_id_must_be_valid(cls, v):
        if v is not None and not isinstance(v, int):
            raise ValueError('Conversation ID must be an integer or null')
        return v

class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    sources: Optional[List[str]] = None
    confidence_score: Optional[float] = None

# RAG Schemas
class RAGQuery(BaseModel):
    query: str
    conversation_id: Optional[int] = None
    top_k: Optional[int] = 5

class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    confidence_score: float

# Email Schemas
class EmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    message: str

class EmailResponse(BaseModel):
    message: str
    success: bool


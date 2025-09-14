from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "development-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str
    password: str

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# In-memory user store for testing
USERS = {
    "test@example.com": {
        "email": "test@example.com",
        "password": "test123",
        "full_name": "Test User"
    }
}

def create_access_token(data: dict):
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "api_keys": {
            "groq": bool(os.getenv("GROQ_API_KEY"))
        }
    }

@app.post("/auth/login")
def login(user_data: UserLogin):
    """Login endpoint"""
    user = USERS.get(user_data.username)
    if not user or user["password"] != user_data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user info"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401)
        user = USERS.get(email)
        if not user:
            raise HTTPException(status_code=401)
        return {
            "email": user["email"],
            "full_name": user["full_name"]
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401)

@app.post("/auth/register")
def register(user_data: UserLogin):
    """Register new user"""
    if user_data.username in USERS:
        raise HTTPException(status_code=400, detail="User already exists")
    
    USERS[user_data.username] = {
        "email": user_data.username,
        "password": user_data.password,
        "full_name": user_data.username.split("@")[0]
    }
    
    return {"message": "User registered successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
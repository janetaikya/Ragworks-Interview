# 🚀 Quick Start Guide

## Prerequisites
- Python 3.8+
- Docker (for Qdrant)
- OpenAI API key

## 1. Setup (One-time)
```bash
# Install dependencies and setup database
python setup.py

# Start Qdrant vector database
python start_qdrant.py
```

## 2. Configure API Keys
Edit `.env` file and add your OpenAI API key:
```bash
OPENAI_API_KEY=your-openai-api-key-here
```

## 3. Run the Application

**Terminal 1 - Backend:**
```bash
python run_backend.py
```

**Terminal 2 - Frontend:**
```bash
python run_frontend.py
```

## 4. Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 5. First Steps
1. Register a new account
2. Upload documents (PDF, Word, PowerPoint, etc.)
3. Start chatting with your AI assistant!

## Stop Everything
```bash
# Stop Qdrant
python start_qdrant.py stop

# Stop backend/frontend with Ctrl+C
```

## Troubleshooting
- Make sure Qdrant is running: `docker ps`
- Check API keys in `.env` file
- View logs in terminal output


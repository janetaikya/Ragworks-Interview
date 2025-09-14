# RAGWorks Chat Application

A real-world chat application that demonstrates advanced capabilities with LLMs, RAG (Retrieval-Augmented Generation), and modern frameworks. This application combines multiple document types, intelligent chat responses, and email integration for a complete user experience.

## 🚀 Features

### Core Features
- **Multi-format Document Processing**: PDF, Word, PowerPoint, HTML, Markdown, and plain text
- **Advanced RAG System**: Qdrant vector database with intelligent document chunking
- **Real-time Chat Interface**: Modern Streamlit UI with conversation management
- **JWT Authentication**: Secure user registration and login
- **SQLite Database**: Lightweight, file-based database for all data storage
- **Email Integration**: Automatic notifications and summaries

### Advanced Features
- **Multiple LLM Support**: OpenAI GPT-4 and Anthropic Claude integration
- **Document Analytics**: Track usage, document types, and conversation metrics
- **Source Attribution**: Show which documents were used for each response
- **Confidence Scoring**: Display AI response confidence levels
- **Conversation History**: Save and manage multiple chat sessions
- **File Management**: Upload, view, and delete documents

## 🛠️ Tech Stack

- **Frontend**: Streamlit with custom CSS and modern UI components
- **Backend**: FastAPI with async support and automatic API documentation
- **Database**: SQLite with SQLAlchemy ORM
- **Vector Database**: Qdrant for document embeddings and similarity search
- **LLM Integration**: OpenAI GPT-4 and Anthropic Claude
- **Authentication**: JWT tokens with bcrypt password hashing
- **Email**: FastAPI-Mail with HTML templates
- **Document Processing**: PyPDF2, python-docx, python-pptx, BeautifulSoup

## 📋 Prerequisites

- Python 3.8 or higher
- Docker (for Qdrant vector database)
- OpenAI API key
- Email credentials (optional, for notifications)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd llm-challenge

# Run the setup script
python setup.py
```

### 2. Configure Environment

Edit the `.env` file with your API keys:

```bash
# Required
OPENAI_API_KEY=your-openai-api-key-here

# Optional
ANTHROPIC_API_KEY=your-anthropic-api-key-here
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

### 3. Start Qdrant (Vector Database)

```bash
# Start Qdrant using Docker
docker run -p 6333:6333 qdrant/qdrant
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
python run_backend.py
```

**Terminal 2 - Frontend:**
```bash
python run_frontend.py
```

### 5. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📖 Usage Guide

### 1. User Registration and Login
- Register a new account with email and password
- Login to access the chat interface
- User data is stored securely in SQLite database

### 2. Document Upload
- Navigate to the "Documents" tab
- Upload files in supported formats (PDF, Word, PowerPoint, HTML, Markdown, TXT)
- Documents are automatically processed and chunked for RAG
- View processing status and document metadata

### 3. Chat Interface
- Start a new conversation or continue existing ones
- Ask questions about your uploaded documents
- AI responses include source attribution and confidence scores
- View conversation history and manage multiple chats

### 4. Analytics
- Track your usage statistics
- View document type distribution
- Monitor conversation activity

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | SQLite database path | `sqlite:///./chat_app.db` |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` |
| `QDRANT_URL` | Qdrant server URL | `http://localhost:6333` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `TOP_K_RESULTS` | Number of relevant chunks | `5` |
| `SIMILARITY_THRESHOLD` | Similarity threshold | `0.7` |

### RAG Configuration

The RAG system can be customized by modifying these parameters in `config.py`:

- **Chunk Size**: Size of document chunks (default: 1000 characters)
- **Chunk Overlap**: Overlap between chunks (default: 200 characters)
- **Top K Results**: Number of relevant chunks to retrieve (default: 5)
- **Similarity Threshold**: Minimum similarity score for chunks (default: 0.7)

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app/
│   ├── main.py          # FastAPI application
│   ├── auth.py          # JWT authentication
│   ├── rag.py           # RAG and document processing
│   ├── routes.py        # Chat and conversation APIs
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── db.py            # Database configuration
│   └── email_service.py # Email functionality
```

### Frontend Structure
```
frontend/
└── app.py               # Streamlit application
```

### Database Schema
- **Users**: User accounts and authentication
- **Conversations**: Chat sessions
- **Messages**: Individual chat messages
- **Documents**: Uploaded files and metadata
- **DocumentChunks**: Processed document chunks for RAG

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- CORS protection
- Input validation with Pydantic
- File type and size restrictions
- SQL injection prevention with SQLAlchemy

## 📧 Email Integration

The application includes comprehensive email functionality:

- **Welcome emails** for new users
- **Document processing notifications**
- **Chat summaries** (can be scheduled)
- **Error notifications**

Configure email settings in the `.env` file:

```bash
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@gmail.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
```

## 🧪 Testing

### Manual Testing
1. Register a new user account
2. Upload various document types
3. Start conversations and ask questions
4. Verify RAG responses include source attribution
5. Test document management features

### API Testing
Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints directly.

## 🚀 Deployment

### Local Development
The application is designed to run locally with minimal setup. All dependencies are managed through `requirements.txt`.

### Production Considerations
- Use a production database (PostgreSQL) instead of SQLite
- Set up proper environment variable management
- Configure reverse proxy (nginx)
- Set up SSL certificates
- Use production email service
- Configure proper logging

## 🐛 Troubleshooting

### Common Issues

1. **Qdrant Connection Error**
   - Ensure Qdrant is running: `docker run -p 6333:6333 qdrant/qdrant`
   - Check if port 6333 is available

2. **OpenAI API Error**
   - Verify your API key in `.env` file
   - Check API key permissions and billing

3. **Database Error**
   - Run `python setup.py` to initialize database
   - Check file permissions for SQLite database

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path configuration

### Logs
- Backend logs are displayed in the terminal
- Frontend logs are in Streamlit's interface
- Database logs can be enabled by setting `echo=True` in `db.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Anthropic for Claude API
- Qdrant for vector database
- Streamlit for the frontend framework
- FastAPI for the backend framework
- LangChain for RAG implementation

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`

---

**Happy Chatting! 🤖💬**
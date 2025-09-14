import streamlit as st
import requests
import json
import time
from datetime import datetime
from streamlit_chat import message
from streamlit_option_menu import option_menu
import os

if "auth_action" not in st.session_state:
    st.session_state.auth_action = "Login" 
if "user_token" not in st.session_state:
    st.session_state.user_token = None

if "conversations" not in st.session_state:
    st.session_state.conversations = []

st.cache_data.clear()
st.cache_resource.clear()


# Configuration and Environment Setup
from dotenv import load_dotenv
load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
MAX_RETRIES = 5
RETRY_DELAY = 2

def check_api_health(show_success=True):
    """Check API health with retries"""
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(f"{API_URL}/health", timeout=5)
            if response.status_code == 200:
                if show_success:
                    st.success(f"✅ Connected to API at {API_URL}")
                api_status = response.json()
                if not os.getenv("GROQ_API_KEY"):
                    st.warning("⚠️ GROQ API key not configured. Chat responses may not work.")
                return True
            else:
                if attempt == MAX_RETRIES - 1:
                    st.error(f"❌ API returned status {response.status_code}")
        except requests.exceptions.ConnectionError:
            if attempt == MAX_RETRIES - 1:
                st.error(f"❌ Cannot connect to API at {API_URL}. Is the backend running?")
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                st.error(f"❌ API Error: {str(e)}")
        time.sleep(RETRY_DELAY)
    return False

# Check API health at startup
api_healthy = check_api_health()

# Page configuration
st.set_page_config(
    page_title="DocuChat AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 600;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #2c3e50;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .document-card {
        border: 1px solid #e1e5e9;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .stButton > button {
        background-color: #667eea;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #5a6fd8;
    }
    .stTextInput > div > div > input {
        border-radius: 6px;
        border: 1px solid #e1e5e9;
    }
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid #e1e5e9;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    if "token" not in st.session_state:
        st.session_state.token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
    if "conversations" not in st.session_state:
        st.session_state.conversations = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents" not in st.session_state:
        st.session_state.documents = []

init_session_state()

# API helper functions
def make_api_request(endpoint, method="GET", data=None, files=None, headers=None):
    """Make API request with enhanced error handling and validation."""
    try:
        # Initialize headers
        if headers is None:
            headers = {}
            
        # Validate required parameters
        if not endpoint:
            st.error("API endpoint is required")
            return None
            
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            st.error(f"Unsupported HTTP method: {method}")
            return None
        
        # Use token from either session state
        token = st.session_state.get("token") or st.session_state.get("user_token")
        
        # Add Bearer token for authenticated endpoints
        if token:
            headers["Authorization"] = f"Bearer {token}"
            
        # Ensure proper Content-Type
        if method in ["POST", "PUT", "PATCH"] and not files:
            headers["Content-Type"] = "application/json"
            
        # For legacy endpoints that require token as query param
        if ("/rag/upload" in endpoint or "/rag/documents" in endpoint) and token:
            if "?" in endpoint:
                endpoint += f"&token={token}"
            else:
                endpoint += f"?token={token}"
        # Prepare request URL
        url = f"{API_URL}{endpoint}"
        
        # Log request details for debugging
        print(f"Making {method} request to {url}")
        print(f"Headers: {headers}")
        if data:
            print(f"Data: {data}")
            
        # Make the request with appropriate method
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, headers=headers)
            else:
                # Ensure data is properly formatted for JSON
                if isinstance(data, dict):
                    response = requests.post(url, json=data, headers=headers)
                else:
                    response = requests.post(url, data=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        # Check response status and handle errors
        if response.status_code == 400:
            error_msg = response.json().get('detail', 'Bad Request - Please check your input')
            st.error(f"Error 400: {error_msg}")
        elif response.status_code == 401:
            st.error("Authentication failed - Please log in again")
            # Clear token to force re-login
            st.session_state.token = None
            st.session_state.user_token = None
        elif response.status_code == 404:
            st.error("Resource not found - Please refresh and try again")
        elif response.status_code >= 500:
            st.error("Server error - Please try again later")
            
        return response
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the server. Please check if the backend is running.")
        return None
    except Exception as e:
        st.error(f"API request failed: {str(e)}")
        return None

def load_conversations():
    """Load user conversations."""
    response = make_api_request("/api/conversations")
    if response and response.status_code == 200:
        st.session_state.conversations = response.json()
    else:
        st.session_state.conversations = []

def load_documents():
    """Load user documents."""
    response = make_api_request("/rag/documents")
    if response and response.status_code == 200:
        st.session_state.documents = response.json()
    else:
        st.session_state.documents = []

def load_messages(conversation_id):
    """Load messages for a conversation."""
    response = make_api_request(f"/api/conversations/{conversation_id}/messages")
    if response and response.status_code == 200:
        st.session_state.messages = response.json()
    else:
        st.session_state.messages = []

# Authentication functions
def login_user(email, password):
    """Login user."""
    data = {"username": email, "password": password}  # Backend expects 'username' for the email field
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json=data,
            headers={"Content-Type": "application/json"}  # Explicitly set content type
        )
        
        if response.status_code == 200:
            token_data = response.json()
            st.session_state.token = token_data["access_token"]
            st.session_state.user_token = token_data["access_token"]  # Store token in both places for compatibility
            
            # Get user info
            user_response = make_api_request("/auth/me")
            if user_response and user_response.status_code == 200:
                st.session_state.user_info = user_response.json()
                st.success("Login successful!")
                load_conversations()
                load_documents()
                st.rerun()
                return True
            else:
                st.error("Failed to get user information")
                return False
        else:
            try:
                error_data = response.json()
                error_message = error_data.get('detail', str(response.text))
            except:
                error_message = str(response.text)
            st.error(f"Login failed: {error_message}")
            return False
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return False

def register_user(email, password, full_name):
    """Register new user."""
    data = {"email": email, "password": password, "full_name": full_name}
    response = make_api_request("/auth/register", method="POST", data=data)
    
    if response and response.status_code == 200:
        st.success("Registration successful! Logging you in...")
        # Automatically log in after registration
        return login_user(email, password)
    else:
        if response:
            st.error(f"Registration failed: {response.text}")
        return False

def logout_user():
    """Logout user."""
    st.session_state.token = None
    st.session_state.user_info = None
    st.session_state.conversation_id = None
    st.session_state.conversations = []
    st.session_state.messages = []
    st.session_state.documents = []

# Main app
def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 DocuChat AI</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        if not st.session_state.token:
            # Authentication section
            st.header("🔐 Authentication")
            auth_tab = st.selectbox("Choose Action", ["Login", "Register"])
            if auth_tab == "Login":
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="your@email.com")
                    password = st.text_input("Password", type="password")
                    login_btn = st.form_submit_button("Login", use_container_width=True)
                    if login_btn:
                        if email and password:
                            login_user(email, password)
                        else:
                            st.error("Please fill in all fields")
            else:  # Register
                with st.form("register_form"):
                    email = st.text_input("Email", placeholder="your@email.com")
                    password = st.text_input("Password", type="password")
                    full_name = st.text_input("Full Name", placeholder="Your Full Name")
                    register_btn = st.form_submit_button("Register", use_container_width=True)
                    if register_btn:
                        if email and password and full_name:
                            register_user(email, password, full_name)
                        else:
                            st.error("Please fill in all fields")
        else:
            # User info and navigation
            user_info = st.session_state.user_info
            if user_info and 'full_name' in user_info:
                st.header(f"👋 Welcome, {user_info['full_name']}")
            else:
                st.header("👋 Welcome!")
                st.warning("User info not loaded. Please log out and log in again if you see this message.")
            if st.button("Logout", use_container_width=True):
                logout_user()
                st.rerun()
            st.markdown("---")
            # Navigation
            selected_page = option_menu(
                menu_title="Navigation",
                options=["💬 Chat", "📁 Documents", "📊 Analytics"],
                icons=["chat", "folder", "graph-up"],
                menu_icon="list",
                default_index=0,
            )
            st.session_state.selected_page = selected_page
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content
    if not st.session_state.token:
        # Clean and simple landing page
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px; margin: 2rem 0;">
            <h1 style="font-size: 4rem; font-weight: 800; margin-bottom: 1.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                🤖 DocuChat AI
            </h1>
            <p style="font-size: 1.5rem; margin-bottom: 3rem; opacity: 0.95; font-weight: 300;">
                Chat with your documents using AI
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Simple features
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1rem 0;">
                <h2 style="font-size: 3rem; margin: 0;">📄</h2>
                <h3 style="color: #2c3e50; margin: 1rem 0;">Upload</h3>
                <p style="color: #7f8c8d;">Upload any document</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1rem 0;">
                <h2 style="font-size: 3rem; margin: 0;">💬</h2>
                <h3 style="color: #2c3e50; margin: 1rem 0;">Chat</h3>
                <p style="color: #7f8c8d;">Ask questions about your docs</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="text-align: center; padding: 2rem; background: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin: 1rem 0;">
                <h2 style="font-size: 3rem; margin: 0;">⚡</h2>
                <h3 style="color: #2c3e50; margin: 1rem 0;">Fast</h3>
                <p style="color: #7f8c8d;">Get instant answers</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Main application
        if st.session_state.selected_page == "💬 Chat":
            chat_interface()
        elif st.session_state.selected_page == "📁 Documents":
            documents_interface()
        elif st.session_state.selected_page == "📊 Analytics":
            analytics_interface()

def chat_interface():
    """Chat interface."""
    st.header("💬 Chat Interface")
    
    # Conversation management
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.conversations:
            conversation_titles = [f"{conv['title']} ({conv['id']})" for conv in st.session_state.conversations]
            selected_conv = st.selectbox("Select Conversation", conversation_titles, key="conv_selector")
            
            if selected_conv:
                conv_id = int(selected_conv.split("(")[-1].split(")")[0])
                if conv_id != st.session_state.conversation_id:
                    st.session_state.conversation_id = conv_id
                    load_messages(conv_id)
        else:
            st.info("No conversations yet. Start a new one below!")
    
    with col2:
        if st.button("New Chat", use_container_width=True):
            st.session_state.conversation_id = None
            st.session_state.messages = []
            st.rerun()
    
    with col3:
        if st.session_state.conversation_id and st.button("Delete Chat", use_container_width=True):
            response = make_api_request(f"/api/conversations/{st.session_state.conversation_id}", method="DELETE")
            if response and response.status_code == 200:
                st.success("Conversation deleted!")
                load_conversations()
                st.session_state.conversation_id = None
                st.session_state.messages = []
                st.rerun()
    
    # Chat messages
    st.markdown("### Messages")
    
    if st.session_state.messages:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key=f"user_{msg['id']}")
            else:
                message(msg["content"], is_user=False, key=f"assistant_{msg['id']}")
                
                # Show sources and confidence if available
                if msg.get("sources"):
                    with st.expander("📚 Sources"):
                        st.write(msg["sources"])
                
                if msg.get("confidence_score"):
                    st.caption(f"Confidence: {msg['confidence_score']:.2f}")
    else:
        st.info("No messages yet. Start a conversation below!")
    
    # Message input
    st.markdown("---")
    
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Your message", height=100, placeholder="Ask me anything about your documents...")
        st.session_state.last_message = user_input  # Save message in session state
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            send_btn = st.form_submit_button("Send", use_container_width=True)
        
        with col2:
            if st.form_submit_button("Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        if send_btn and user_input:
            try:
                # Clean and validate input
                msg_text = user_input.strip()
                if not msg_text:
                    st.error("Please enter a message")
                    return

                # Handle conversation ID
                conv_id = None
                if hasattr(st.session_state, 'conversation_id') and st.session_state.conversation_id:
                    try:
                        conv_id = int(st.session_state.conversation_id)
                    except (ValueError, TypeError):
                        conv_id = None

                # Prepare request data
                data = {
                    "message": msg_text,
                    "conversation_id": conv_id
                }

                # Get authentication token
                token = st.session_state.get("token") or st.session_state.get("user_token")
                if not token:
                    st.error("Please log in again")
                    return

                with st.spinner("🤖 AI is thinking..."):
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                    # Make the API request
                    response = make_api_request(
                        endpoint="/api/chat",
                        method="POST",
                        data=data,
                        headers=headers
                    )

                if response and response.status_code == 200:
                    chat_response = response.json()
                    # Update conversation ID if new conversation was created
                    if not st.session_state.conversation_id:
                        st.session_state.conversation_id = chat_response["conversation_id"]
                    # Reload messages
                    load_messages(st.session_state.conversation_id)
                    load_conversations()
                    st.rerun()
                else:
                    error_message = "Unknown error"
                    if response:
                        try:
                            error_data = response.json()
                            error_message = error_data.get('detail', str(response.text))
                        except Exception:
                            error_message = str(response.text)
                    st.error(f"Chat error: {error_message}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.error("Please try again or contact support if the problem persists")

def documents_interface():
    """Documents management interface."""
    st.header("📁 Document Management")
    
    # Upload section
    st.subheader("Upload Documents")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "pdf", "docx", "pptx", "html", "md"],
        help="Supported formats: TXT, PDF, Word, PowerPoint, HTML, Markdown"
    )
    
    if uploaded_file is not None:
        if st.button("Upload Document"):
            with st.spinner("Uploading and processing document..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                response = make_api_request("/rag/upload", method="POST", files=files)
            
            if response and response.status_code == 200:
                st.success("Document uploaded and processed successfully!")
                load_documents()
                st.rerun()
            else:
                if response is not None:
                    st.error(f"Upload failed: {response.status_code} {response.text}")
                else:
                    st.error("Failed to connect to the server. Please try again.")
    
    # Documents list
    st.subheader("Your Documents")
    
    if st.session_state.documents:
        for doc in st.session_state.documents:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="document-card">
                        <h4>{doc['title']}</h4>
                        <p><strong>Type:</strong> {doc['file_type'].upper()}</p>
                        <p><strong>Size:</strong> {doc['file_size']} bytes</p>
                        <p><strong>Status:</strong> {'✅ Processed' if doc['is_processed'] else '⏳ Processing'}</p>
                        <p><strong>Chunks:</strong> {doc['chunk_count']}</p>
                        <p><strong>Uploaded:</strong> {doc['created_at'][:10]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if st.button("View", key=f"view_{doc['id']}"):
                        st.write(doc['content'][:500] + "..." if len(doc['content']) > 500 else doc['content'])
                
                with col3:
                    if st.button("Delete", key=f"delete_{doc['id']}"):
                        response = make_api_request(f"/rag/documents/{doc['id']}", method="DELETE")
                        if response and response.status_code == 200:
                            st.success("Document deleted!")
                            load_documents()
                            st.rerun()
                        else:
                            if response:
                                st.error(f"Delete failed: {response.text}")
    else:
        st.info("No documents uploaded yet. Upload your first document above!")

def analytics_interface():
    """Analytics interface."""
    st.header("📊 Analytics Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Conversations</p>
        </div>
        """.format(len(st.session_state.conversations)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Documents</p>
        </div>
        """.format(len(st.session_state.documents)), unsafe_allow_html=True)
    
    with col3:
        total_messages = sum(len(conv.get('messages', [])) for conv in st.session_state.conversations)
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Messages</p>
        </div>
        """.format(total_messages), unsafe_allow_html=True)
    
    with col4:
        processed_docs = sum(1 for doc in st.session_state.documents if doc['is_processed'])
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Processed</p>
        </div>
        """.format(processed_docs), unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Document types distribution
    if st.session_state.documents:
        st.subheader("Document Types")
        doc_types = {}
        for doc in st.session_state.documents:
            doc_type = doc['file_type'].upper()
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        
        if doc_types:
            st.bar_chart(doc_types)
        else:
            st.info("No documents uploaded yet.")
    
    # Recent activity
    st.subheader("Recent Activity")
    if st.session_state.conversations:
        recent_convs = sorted(st.session_state.conversations, key=lambda x: x['updated_at'], reverse=True)[:5]
        for conv in recent_convs:
            st.write(f"📝 **{conv['title']}** - {conv['updated_at'][:10]}")
    else:
        st.info("No conversations yet.")

if __name__ == "__main__":
    main()

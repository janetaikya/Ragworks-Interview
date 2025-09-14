from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Optional
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM, MAIL_PORT, 
    MAIL_SERVER, MAIL_TLS, MAIL_SSL
)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_TLS=MAIL_TLS,
    MAIL_SSL=MAIL_SSL,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fastmail = FastMail(conf)

async def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """Send an email to the specified recipient."""
    try:
        message = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=body,
            subtype="html" if html_body else "plain"
        )
        
        if html_body:
            message.html = html_body
        
        await fastmail.send_message(message)
        return True
    
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

async def send_welcome_email(to_email: str, user_name: str) -> bool:
    """Send welcome email to new user."""
    subject = "Welcome to RAGWorks Chat!"
    
    html_body = f"""
    <html>
    <body>
        <h2>Welcome to RAGWorks Chat, {user_name}!</h2>
        <p>Thank you for registering with our AI-powered chat application.</p>
        <p>You can now:</p>
        <ul>
            <li>Upload documents in various formats (PDF, Word, PowerPoint, etc.)</li>
            <li>Chat with our AI assistant powered by GPT-4</li>
            <li>Get intelligent responses based on your uploaded documents</li>
            <li>Manage your conversations and document library</li>
        </ul>
        <p>Get started by logging in and uploading your first document!</p>
        <br>
        <p>Best regards,<br>The RAGWorks Team</p>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, "", html_body)

async def send_document_processed_email(
    to_email: str, 
    user_name: str, 
    document_title: str
) -> bool:
    """Send email notification when document is processed."""
    subject = f"Document '{document_title}' has been processed!"
    
    html_body = f"""
    <html>
    <body>
        <h2>Document Processing Complete</h2>
        <p>Hello {user_name},</p>
        <p>Your document '<strong>{document_title}</strong>' has been successfully processed and is now available for chat queries.</p>
        <p>You can now ask questions about this document and get intelligent responses based on its content.</p>
        <br>
        <p>Happy chatting!</p>
        <p>Best regards,<br>The RAGWorks Team</p>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, "", html_body)

async def send_chat_summary_email(
    to_email: str,
    user_name: str,
    conversation_title: str,
    message_count: int
) -> bool:
    """Send periodic chat summary email."""
    subject = f"Chat Summary: {conversation_title}"
    
    html_body = f"""
    <html>
    <body>
        <h2>Chat Summary</h2>
        <p>Hello {user_name},</p>
        <p>Here's a summary of your recent chat activity:</p>
        <ul>
            <li><strong>Conversation:</strong> {conversation_title}</li>
            <li><strong>Messages exchanged:</strong> {message_count}</li>
        </ul>
        <p>Continue your conversation or start a new one anytime!</p>
        <br>
        <p>Best regards,<br>The RAGWorks Team</p>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, "", html_body)

async def send_error_notification_email(
    to_email: str,
    user_name: str,
    error_type: str,
    error_message: str
) -> bool:
    """Send error notification email."""
    subject = "RAGWorks Chat - Error Notification"
    
    html_body = f"""
    <html>
    <body>
        <h2>Error Notification</h2>
        <p>Hello {user_name},</p>
        <p>We encountered an issue while processing your request:</p>
        <ul>
            <li><strong>Error Type:</strong> {error_type}</li>
            <li><strong>Error Message:</strong> {error_message}</li>
        </ul>
        <p>Please try again or contact support if the issue persists.</p>
        <br>
        <p>Best regards,<br>The RAGWorks Team</p>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, "", html_body)


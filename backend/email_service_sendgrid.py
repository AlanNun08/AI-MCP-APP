import os
import random
import string
import requests
import json
from datetime import datetime, timedelta
from typing import Optional
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        # Load from environment variables - try SendGrid first, then fallback to Mailjet
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        self.mailjet_api_key = os.environ.get('MAILJET_API_KEY')
        self.mailjet_secret_key = os.environ.get('MAILJET_SECRET_KEY')
        self.sender_email = os.environ.get('SENDER_EMAIL')
        
        # Determine which service to use
        if self.sendgrid_api_key:
            self.service = 'sendgrid'
            self.initialized = True
            logger.info(f"EmailService initialized with SendGrid - Sender: {self.sender_email}")
        elif self.mailjet_api_key and self.mailjet_secret_key:
            self.service = 'mailjet'
            self.initialized = True
            logger.info(f"EmailService initialized with Mailjet - Sender: {self.sender_email}")
        else:
            self.service = None
            self.initialized = False
            logger.error("No email service configured - missing API keys")
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    async def send_password_reset_email(self, to_email: str, first_name: str, reset_code: str) -> bool:
        """Send password reset email using available service"""
        if not self.initialized:
            logger.error("Email service not initialized")
            return False
            
        if self.service == 'sendgrid':
            return await self._send_sendgrid_email(to_email, first_name, reset_code, 'reset')
        elif self.service == 'mailjet':
            return await self._send_mailjet_email(to_email, first_name, reset_code, 'reset')
        else:
            logger.error("No email service available")
            return False
    
    async def send_verification_email(self, to_email: str, first_name: str, verification_code: str) -> bool:
        """Send verification email using available service"""
        if not self.initialized:
            logger.error("Email service not initialized")
            return False
            
        if self.service == 'sendgrid':
            return await self._send_sendgrid_email(to_email, first_name, verification_code, 'verify')
        elif self.service == 'mailjet':
            return await self._send_mailjet_email(to_email, first_name, verification_code, 'verify')
        else:
            logger.error("No email service available")
            return False
    
    async def _send_sendgrid_email(self, to_email: str, first_name: str, code: str, email_type: str) -> bool:
        """Send email using SendGrid API"""
        try:
            if email_type == 'reset':
                subject = "Reset Your AI Chef Password"
                content = f"""
                <h2>Password Reset</h2>
                <p>Hi {first_name},</p>
                <p>Your password reset code is: <strong>{code}</strong></p>
                <p>This code will expire in 10 minutes.</p>
                """
            else:  # verify
                subject = "Verify Your AI Chef Account"
                content = f"""
                <h2>Email Verification</h2>
                <p>Hi {first_name},</p>
                <p>Your verification code is: <strong>{code}</strong></p>
                <p>This code will expire in 5 minutes.</p>
                """
            
            data = {
                "personalizations": [
                    {
                        "to": [{"email": to_email, "name": first_name}],
                        "subject": subject
                    }
                ],
                "from": {"email": self.sender_email, "name": "AI Chef App"},
                "content": [{"type": "text/html", "value": content}]
            }
            
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 202:
                logger.info(f"✅ SendGrid email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"❌ SendGrid failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ SendGrid error: {str(e)}")
            return False
    
    async def _send_mailjet_email(self, to_email: str, first_name: str, code: str, email_type: str) -> bool:
        """Send email using Mailjet API (fallback)"""
        try:
            if email_type == 'reset':
                subject = "Reset Your AI Chef Password"
                html_content = f"""
                <h2>Password Reset</h2>
                <p>Hi {first_name},</p>
                <p>Your password reset code is: <strong>{code}</strong></p>
                <p>This code will expire in 10 minutes.</p>
                """
            else:  # verify
                subject = "Verify Your AI Chef Account"
                html_content = f"""
                <h2>Email Verification</h2>
                <p>Hi {first_name},</p>
                <p>Your verification code is: <strong>{code}</strong></p>
                <p>This code will expire in 5 minutes.</p>
                """
            
            data = {
                "Messages": [{
                    "From": {"Email": self.sender_email, "Name": "AI Chef App"},
                    "To": [{"Email": to_email, "Name": first_name}],
                    "Subject": subject,
                    "HTMLPart": html_content
                }]
            }
            
            auth = (self.mailjet_api_key, self.mailjet_secret_key)
            headers = {"Content-Type": "application/json"}
            
            response = requests.post(
                "https://api.mailjet.com/v3.1/send",
                auth=auth,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Mailjet email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"❌ Mailjet failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mailjet error: {str(e)}")
            return False

# Create global email service instance
email_service = EmailService()
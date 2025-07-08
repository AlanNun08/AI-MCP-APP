import os
import random
import string
from datetime import datetime, timedelta
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = os.getenv('MAILJET_API_KEY')
        self.secret_key = os.getenv('MAILJET_SECRET_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.test_mode = True  # Always use test mode for now
        self.last_verification_code = None  # Store for testing
        
        if not all([self.api_key, self.secret_key, self.sender_email]) and not self.test_mode:
            raise ValueError("Missing Mailjet configuration. Please check your environment variables.")
        
        if not self.test_mode:
            try:
                from mailjet_rest import Client
                self.mailjet = Client(auth=(self.api_key, self.secret_key), version='v3.1')
            except ImportError:
                logger.warning("mailjet_rest not installed, running in test mode")
                self.test_mode = True
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join(random.choices(string.digits, k=6))
    
    async def send_verification_email(self, to_email: str, first_name: str, verification_code: str) -> bool:
        """Send verification email with 6-digit code"""
        self.last_verification_code = verification_code  # Store for testing
        
        if self.test_mode:
            logger.info(f"TEST MODE: Would send verification code {verification_code} to {to_email}")
            print(f"🧪 TEST EMAIL: Verification code {verification_code} for {to_email}")
            return True
            
        try:
            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": self.sender_email,
                            "Name": "AI Chef App"
                        },
                        "To": [
                            {
                                "Email": to_email,
                                "Name": first_name
                            }
                        ],
                        "Subject": "Verify Your AI Chef Account",
                        "TextPart": f"""
Hi {first_name},

Welcome to AI Chef! Please verify your email address to complete your registration.

Your verification code is: {verification_code}

This code will expire in 5 minutes.

If you didn't create this account, please ignore this email.

Best regards,
AI Chef Team
                        """,
                        "HTMLPart": f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: #10b981; margin-bottom: 10px;">👨‍🍳 AI Chef</h1>
        <h2 style="color: #374151; margin-top: 0;">Verify Your Account</h2>
    </div>
    
    <div style="background-color: #f9fafb; border-radius: 12px; padding: 25px; margin: 20px 0;">
        <p style="color: #374151; font-size: 16px; margin-bottom: 20px;">Hi {first_name},</p>
        
        <p style="color: #374151; font-size: 16px; margin-bottom: 20px;">
            Welcome to AI Chef! Please verify your email address to complete your registration.
        </p>
        
        <div style="text-align: center; margin: 30px 0;">
            <div style="background-color: #10b981; color: white; font-size: 32px; font-weight: bold; padding: 20px; border-radius: 8px; letter-spacing: 8px; font-family: monospace;">
                {verification_code}
            </div>
        </div>
        
        <p style="color: #6b7280; font-size: 14px; text-align: center; margin-top: 20px;">
            This code will expire in 5 minutes.
        </p>
    </div>
    
    <div style="border-top: 1px solid #e5e7eb; padding-top: 20px; margin-top: 30px;">
        <p style="color: #6b7280; font-size: 12px; text-align: center;">
            If you didn't create this account, please ignore this email.
        </p>
        <p style="color: #6b7280; font-size: 12px; text-align: center;">
            Best regards,<br>AI Chef Team
        </p>
    </div>
</body>
</html>
                        """
                    }
                ]
            }
            
            # Send email using Mailjet
            result = self.mailjet.send.create(data=data)
            
            if result.status_code == 200:
                logger.info(f"Verification email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status: {result.status_code}, Error: {result.json()}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False

# Create global email service instance
email_service = EmailService()
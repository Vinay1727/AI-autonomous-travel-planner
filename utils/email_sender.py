# Email sender utility for OTP verification

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import random
import string

load_dotenv()

class EmailSender:
    def __init__(self):
        self.smtp_host = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_PORT', 587))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        if not self.email_user or not self.email_password:
            raise ValueError("Email credentials not found in environment variables")
    
    def generate_otp(self, length=6):
        """Generate a random OTP"""
        return ''.join(random.choices(string.digits, k=length))
    
    def send_otp_email(self, to_email, otp, user_name="User"):
        """Send OTP verification email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = "Premium AI Travel - Verify Your Email"
            message["From"] = f"Premium AI Travel <{self.email_user}>"
            message["To"] = to_email
            
            # HTML email template
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Inter', Arial, sans-serif;
                        background-color: #f5f5f5;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 40px auto;
                        background: linear-gradient(135deg, #1a1a2e 0%, #141423 100%);
                        border-radius: 20px;
                        overflow: hidden;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    }}
                    .header {{
                        background: linear-gradient(135deg, rgba(212, 175, 55, 0.2), rgba(212, 175, 55, 0.1));
                        padding: 40px;
                        text-align: center;
                        border-bottom: 2px solid rgba(212, 175, 55, 0.3);
                    }}
                    .logo {{
                        font-size: 2.5rem;
                        color: #d4af37;
                        margin-bottom: 10px;
                    }}
                    .header h1 {{
                        color: #d4af37;
                        font-size: 28px;
                        margin: 10px 0;
                    }}
                    .content {{
                        padding: 40px;
                        color: #ffffff;
                    }}
                    .greeting {{
                        font-size: 18px;
                        margin-bottom: 20px;
                        color: rgba(255, 255, 255, 0.9);
                    }}
                    .otp-box {{
                        background: rgba(212, 175, 55, 0.1);
                        border: 2px solid rgba(212, 175, 55, 0.3);
                        border-radius: 15px;
                        padding: 30px;
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .otp-label {{
                        color: rgba(255, 255, 255, 0.7);
                        font-size: 14px;
                        text-transform: uppercase;
                        letter-spacing: 1px;
                        margin-bottom: 15px;
                    }}
                    .otp-code {{
                        font-size: 48px;
                        font-weight: bold;
                        color: #d4af37;
                        letter-spacing: 10px;
                        font-family: 'Courier New', monospace;
                    }}
                    .note {{
                        color: rgba(255, 255, 255, 0.6);
                        font-size: 14px;
                        line-height: 1.6;
                        margin-top: 20px;
                    }}
                    .footer {{
                        background: rgba(0, 0, 0, 0.3);
                        padding: 30px;
                        text-align: center;
                        color: rgba(255, 255, 255, 0.5);
                        font-size: 13px;
                    }}
                    .footer-link {{
                        color: #d4af37;
                        text-decoration: none;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                        <div class="header">
                        <div class="logo">✈️</div>
                        <h1>Premium AI Travel</h1>
                        <p style="color: rgba(255, 255, 255, 0.7); margin: 0;">Premium AI Travel Planning</p>
                    </div>
                    
                    <div class="content">
                        <p class="greeting">Hello {user_name},</p>
                        <p style="color: rgba(255, 255, 255, 0.8); line-height: 1.6;">
                            Thank you for joining Premium AI Travel! To complete your registration and start planning your dream journeys,
                            please verify your email address using the OTP code below:
                        </p>
                        
                        <div class="otp-box">
                            <div class="otp-label">Your Verification Code</div>
                            <div class="otp-code">{otp}</div>
                        </div>
                        
                        <p class="note">
                            ⏰ This code will expire in <strong>10 minutes</strong>.<br>
                            🔒 For security reasons, please do not share this code with anyone.<br>
                            ❓ If you didn't request this code, please ignore this email.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p style="margin: 0 0 10px 0;">
                            Need help? Contact us at <a href="mailto:support@travelplanner.ai" class="footer-link">support@travelplanner.ai</a>
                        </p>
                        <p style="margin: 0; font-size: 12px;">
                            © 2024 Premium AI Travel. All rights reserved.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Attach HTML part
            part = MIMEText(html, "html")
            message.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to_email, message.as_string())
            
            print(f"✅ OTP email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def send_welcome_email(self, to_email, user_name):
        """Send welcome email after successful registration"""
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = "Welcome to Premium AI Travel! 🎉"
            message["From"] = f"Premium AI Travel <{self.email_user}>"
            message["To"] = to_email
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 40px;">
                    <h1 style="color: #d4af37;">Welcome to Premium AI Travel, {user_name}! ✈️</h1>
                    <p>Your account has been successfully verified. Start exploring premium travel destinations!</p>
                    <a href="http://localhost:8000" style="display: inline-block; background: #d4af37; color: black; padding: 12px 30px; text-decoration: none; border-radius: 8px; margin-top: 20px;">Start Planning</a>
                </div>
            </body>
            </html>
            """
            
            part = MIMEText(html, "html")
            message.attach(part)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to_email, message.as_string())
            
            print(f"✅ Welcome email sent to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send welcome email: {e}")
            return False

# Singleton instance
email_sender = EmailSender()

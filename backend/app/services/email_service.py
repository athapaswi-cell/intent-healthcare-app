import os
import sys
import io
from typing import Optional
from dotenv import load_dotenv

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

# Email configuration
EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'sendgrid').lower()
USE_MOCK_EMAIL = os.getenv('USE_MOCK_EMAIL', 'true').lower() == 'true'

# SendGrid configuration
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', os.getenv('FROM_EMAIL', ''))

# SMTP configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', '')
FROM_NAME = os.getenv('FROM_NAME', 'Healthcare Platform')

def send_email_sendgrid(to_email: str, subject: str, html_content: str, text_content: str = '') -> bool:
    """Send email using SendGrid API"""
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        if not SENDGRID_API_KEY:
            print("[ERROR] SendGrid API key not configured")
            return False
        
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL or FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content,
            plain_text_content=text_content
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"[SUCCESS] Email sent via SendGrid. Status: {response.status_code}")
        print(f"  To: {to_email}")
        print(f"  From: {SENDGRID_FROM_EMAIL or FROM_EMAIL}")
        print(f"  Subject: {subject}")
        
        return response.status_code in [200, 202]
    except Exception as e:
        print(f"[ERROR] SendGrid email failed: {str(e)}")
        return False

def send_email_smtp(to_email: str, subject: str, html_content: str, text_content: str = '') -> bool:
    """Send email using SMTP"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        if not SMTP_USERNAME or not SMTP_PASSWORD:
            print("[ERROR] SMTP credentials not configured")
            return False
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{FROM_NAME} <{FROM_EMAIL}>"
        msg['To'] = to_email
        
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        print(f"[SUCCESS] Email sent via SMTP")
        print(f"  To: {to_email}")
        print(f"  From: {FROM_EMAIL}")
        print(f"  Subject: {subject}")
        
        return True
    except Exception as e:
        print(f"[ERROR] SMTP email failed: {str(e)}")
        return False

def send_email(to_email: str, subject: str, html_content: str, text_content: str = '') -> bool:
    """Send email using configured provider"""
    if USE_MOCK_EMAIL:
        print(f"[MOCK] Email would be sent to: {to_email}")
        print(f"  Subject: {subject}")
        print(f"  (Mock mode - no actual email sent)")
        return True
    
    if EMAIL_PROVIDER == 'sendgrid':
        return send_email_sendgrid(to_email, subject, html_content, text_content)
    elif EMAIL_PROVIDER == 'smtp':
        return send_email_smtp(to_email, subject, html_content, text_content)
    else:
        print(f"[ERROR] Unknown email provider: {EMAIL_PROVIDER}")
        return False

def send_registration_email(to_email: str, username: str, full_name: str, role: str) -> bool:
    """Send registration welcome email"""
    subject = "Registration Successful - Welcome to Healthcare Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #6366f1; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Healthcare Platform!</h1>
            </div>
            <div class="content">
                <p>Hello {full_name},</p>
                <p>Thank you for registering with our Healthcare Platform. Your account has been successfully created!</p>
                <p><strong>Account Details:</strong></p>
                <ul>
                    <li>Username: {username}</li>
                    <li>Email: {to_email}</li>
                    <li>Role: {role.capitalize()}</li>
                </ul>
                <p>You can now log in and start using all the features of our platform.</p>
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
                <p>Best regards,<br>Healthcare Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Healthcare Platform!
    
    Hello {full_name},
    
    Thank you for registering with our Healthcare Platform. Your account has been successfully created!
    
    Account Details:
    - Username: {username}
    - Email: {to_email}
    - Role: {role.capitalize()}
    
    You can now log in and start using all the features of our platform.
    
    If you have any questions, please don't hesitate to contact our support team.
    
    Best regards,
    Healthcare Platform Team
    """
    
    return send_email(to_email, subject, html_content, text_content)

def send_appointment_confirmation_email(
    to_email: str, 
    patient_name: str, 
    doctor_name: str, 
    appointment_date: str, 
    appointment_time: str,
    hospital_name: str = "",
    appointment_type: str = ""
) -> bool:
    """Send appointment confirmation email"""
    subject = "Appointment Confirmed - Healthcare Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .info-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981; }}
            .info-row {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Appointment Confirmed!</h1>
            </div>
            <div class="content">
                <p>Hello {patient_name},</p>
                <p>Your appointment has been successfully confirmed.</p>
                <div class="info-box">
                    <div class="info-row"><span class="label">Doctor:</span> {doctor_name}</div>
                    <div class="info-row"><span class="label">Date:</span> {appointment_date}</div>
                    <div class="info-row"><span class="label">Time:</span> {appointment_time}</div>
                    {f'<div class="info-row"><span class="label">Hospital:</span> {hospital_name}</div>' if hospital_name else ''}
                    {f'<div class="info-row"><span class="label">Type:</span> {appointment_type}</div>' if appointment_type else ''}
                </div>
                <p>Please arrive 15 minutes before your scheduled time.</p>
                <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
                <p>Best regards,<br>Healthcare Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Appointment Confirmed - Healthcare Platform
    
    Hello {patient_name},
    
    Your appointment has been successfully confirmed.
    
    Appointment Details:
    - Doctor: {doctor_name}
    - Date: {appointment_date}
    - Time: {appointment_time}
    {f'- Hospital: {hospital_name}' if hospital_name else ''}
    {f'- Type: {appointment_type}' if appointment_type else ''}
    
    Please arrive 15 minutes before your scheduled time.
    
    If you need to reschedule or cancel, please contact us at least 24 hours in advance.
    
    Best regards,
    Healthcare Platform Team
    """
    
    return send_email(to_email, subject, html_content, text_content)

def send_appointment_reminder_email(
    to_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    hospital_name: str = ""
) -> bool:
    """Send appointment reminder email"""
    subject = "Appointment Reminder - Healthcare Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .info-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
            .info-row {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Appointment Reminder</h1>
            </div>
            <div class="content">
                <p>Hello {patient_name},</p>
                <p>This is a friendly reminder about your upcoming appointment.</p>
                <div class="info-box">
                    <div class="info-row"><span class="label">Doctor:</span> {doctor_name}</div>
                    <div class="info-row"><span class="label">Date:</span> {appointment_date}</div>
                    <div class="info-row"><span class="label">Time:</span> {appointment_time}</div>
                    {f'<div class="info-row"><span class="label">Hospital:</span> {hospital_name}</div>' if hospital_name else ''}
                </div>
                <p>Please remember to arrive 15 minutes before your scheduled time.</p>
                <p>If you need to reschedule or cancel, please contact us as soon as possible.</p>
                <p>Best regards,<br>Healthcare Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Appointment Reminder - Healthcare Platform
    
    Hello {patient_name},
    
    This is a friendly reminder about your upcoming appointment.
    
    Appointment Details:
    - Doctor: {doctor_name}
    - Date: {appointment_date}
    - Time: {appointment_time}
    {f'- Hospital: {hospital_name}' if hospital_name else ''}
    
    Please remember to arrive 15 minutes before your scheduled time.
    
    If you need to reschedule or cancel, please contact us as soon as possible.
    
    Best regards,
    Healthcare Platform Team
    """
    
    return send_email(to_email, subject, html_content, text_content)

def send_password_reset_email(to_email: str, username: str, reset_token: str, reset_url: str = "") -> bool:
    """Send password reset email"""
    subject = "Password Reset Request - Healthcare Platform"
    
    if not reset_url:
        reset_url = f"http://localhost:5173/reset-password?token={reset_token}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .warning {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 15px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello {username},</p>
                <p>We received a request to reset your password for your Healthcare Platform account.</p>
                <p>Click the button below to reset your password:</p>
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </div>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #6366f1;">{reset_url}</p>
                <div class="warning">
                    <strong>Security Notice:</strong> This link will expire in 1 hour. If you didn't request this reset, please ignore this email.
                </div>
                <p>Best regards,<br>Healthcare Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset Request - Healthcare Platform
    
    Hello {username},
    
    We received a request to reset your password for your Healthcare Platform account.
    
    Click the link below to reset your password:
    {reset_url}
    
    Security Notice: This link will expire in 1 hour. If you didn't request this reset, please ignore this email.
    
    Best regards,
    Healthcare Platform Team
    """
    
    return send_email(to_email, subject, html_content, text_content)

def send_notification_email(
    to_email: str,
    recipient_name: str,
    title: str,
    message: str,
    notification_type: str = "info"
) -> bool:
    """Send general notification email"""
    colors = {
        "info": ("#3b82f6", "#2563eb"),
        "success": ("#10b981", "#059669"),
        "warning": ("#f59e0b", "#d97706"),
        "error": ("#ef4444", "#dc2626")
    }
    
    color, dark_color = colors.get(notification_type, colors["info"])
    
    subject = f"{title} - Healthcare Platform"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, {color} 0%, {dark_color} 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{title}</h1>
            </div>
            <div class="content">
                <p>Hello {recipient_name},</p>
                <p>{message}</p>
                <p>Best regards,<br>Healthcare Platform Team</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    {title} - Healthcare Platform
    
    Hello {recipient_name},
    
    {message}
    
    Best regards,
    Healthcare Platform Team
    """
    
    return send_email(to_email, subject, html_content, text_content)


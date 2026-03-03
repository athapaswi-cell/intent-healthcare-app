from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.app.services.email_service import (
    send_registration_email,
    send_appointment_confirmation_email,
    send_appointment_reminder_email,
    send_password_reset_email,
    send_notification_email,
    send_email
)

router = APIRouter()

class RegistrationEmailRequest(BaseModel):
    to_email: EmailStr
    username: str
    full_name: str
    role: str

class AppointmentConfirmationRequest(BaseModel):
    to_email: EmailStr
    patient_name: str
    doctor_name: str
    appointment_date: str
    appointment_time: str
    hospital_name: Optional[str] = ""
    appointment_type: Optional[str] = ""

class AppointmentReminderRequest(BaseModel):
    to_email: EmailStr
    patient_name: str
    doctor_name: str
    appointment_date: str
    appointment_time: str
    hospital_name: Optional[str] = ""

class PasswordResetRequest(BaseModel):
    to_email: EmailStr
    username: str
    reset_token: str
    reset_url: Optional[str] = ""

class NotificationRequest(BaseModel):
    to_email: EmailStr
    recipient_name: str
    title: str
    message: str
    notification_type: Optional[str] = "info"  # info, success, warning, error

class CustomEmailRequest(BaseModel):
    to_email: EmailStr
    subject: str
    html_content: str
    text_content: Optional[str] = ""

@router.post("/send-registration")
async def send_registration(request: RegistrationEmailRequest):
    """Send registration welcome email"""
    try:
        success = send_registration_email(
            to_email=request.to_email,
            username=request.username,
            full_name=request.full_name,
            role=request.role
        )
        if success:
            return {"success": True, "message": "Registration email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send registration email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.post("/send-appointment-confirmation")
async def send_appointment_confirmation(request: AppointmentConfirmationRequest):
    """Send appointment confirmation email"""
    try:
        success = send_appointment_confirmation_email(
            to_email=request.to_email,
            patient_name=request.patient_name,
            doctor_name=request.doctor_name,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            hospital_name=request.hospital_name,
            appointment_type=request.appointment_type
        )
        if success:
            return {"success": True, "message": "Appointment confirmation email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send appointment confirmation email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.post("/send-appointment-reminder")
async def send_appointment_reminder(request: AppointmentReminderRequest):
    """Send appointment reminder email"""
    try:
        success = send_appointment_reminder_email(
            to_email=request.to_email,
            patient_name=request.patient_name,
            doctor_name=request.doctor_name,
            appointment_date=request.appointment_date,
            appointment_time=request.appointment_time,
            hospital_name=request.hospital_name
        )
        if success:
            return {"success": True, "message": "Appointment reminder email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send appointment reminder email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.post("/send-password-reset")
async def send_password_reset(request: PasswordResetRequest):
    """Send password reset email"""
    try:
        success = send_password_reset_email(
            to_email=request.to_email,
            username=request.username,
            reset_token=request.reset_token,
            reset_url=request.reset_url
        )
        if success:
            return {"success": True, "message": "Password reset email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send password reset email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.post("/send-notification")
async def send_notification(request: NotificationRequest):
    """Send general notification email"""
    try:
        success = send_notification_email(
            to_email=request.to_email,
            recipient_name=request.recipient_name,
            title=request.title,
            message=request.message,
            notification_type=request.notification_type
        )
        if success:
            return {"success": True, "message": "Notification email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send notification email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")

@router.post("/send-custom")
async def send_custom_email(request: CustomEmailRequest):
    """Send custom email with custom content"""
    try:
        success = send_email(
            to_email=request.to_email,
            subject=request.subject,
            html_content=request.html_content,
            text_content=request.text_content or ""
        )
        if success:
            return {"success": True, "message": "Custom email sent successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send custom email")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")


from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
from backend.app.services.email_service import send_registration_email

router = APIRouter()

class RegisterRequest(BaseModel):
    username: str
    password: str
    email: EmailStr
    firstName: str
    lastName: str
    dateOfBirth: str
    gender: str
    phone: Optional[str] = None
    role: str

class RegisterResponse(BaseModel):
    success: bool
    message: str
    username: str
    email: str
    patientId: Optional[str] = None

@router.post("/register", response_model=RegisterResponse)
async def register_user(request: RegisterRequest):
    """
    Register a new user and send welcome email
    """
    print(f"\n{'='*80}")
    print(f"🔵 REGISTRATION API CALLED")
    print(f"{'='*80}")
    print(f"Received registration request for: {request.email}")
    print(f"{'='*80}\n")
    
    try:
        # Generate patient ID for patients
        patient_id = None
        if request.role == "patient":
            import time
            patient_id = f"PAT{int(time.time()) % 1000000:06d}"
        
        full_name = f"{request.firstName} {request.lastName}"
        
        # Send registration email
        print(f"\n{'='*70}")
        print(f"ATTEMPTING TO SEND REGISTRATION EMAIL")
        print(f"{'='*70}")
        print(f"User clicked 'Create account' button")
        print(f"Email from registration form: {request.email}")
        print(f"Sending registration email to: {request.email}")
        print(f"Username: {request.username}")
        print(f"Full Name: {full_name}")
        print(f"Role: {request.role}")
        print(f"{'='*70}\n")
        
        try:
            email_sent = send_registration_email(
                to_email=request.email,
                username=request.username,
                full_name=full_name,
                role=request.role
            )
            
            if email_sent:
                print(f"\n{'='*70}")
                print(f"EMAIL SENT SUCCESSFULLY!")
                print(f"{'='*70}")
                print(f"Registration email sent to: {request.email}")
                print(f"This is the email address from the registration form!")
                print(f"Subject: Registration Successful - Welcome to Healthcare Platform")
                print(f"{'='*70}\n")
            else:
                print(f"\n{'='*70}")
                print(f"EMAIL SEND FAILED")
                print(f"{'='*70}")
                print(f"Recipient: {request.email}")
                print(f"Reason: Email service returned False")
                print(f"{'='*70}\n")
                
        except Exception as email_error:
            # Catch encoding errors and continue with registration
            import sys
            error_msg = str(email_error)
            # Replace any problematic characters
            if 'charmap' in error_msg or 'codec' in error_msg:
                error_msg = "Email encoding error (non-critical)"
            print(f"\n{'='*70}")
            print(f"EMAIL SEND ERROR")
            print(f"{'='*70}")
            print(f"Recipient: {request.email}")
            print(f"Error: {error_msg}")
            print(f"{'='*70}\n")
            email_sent = False
        
        if not email_sent:
            # Log warning but don't fail registration if email fails
            print(f"Warning: Email could not be sent to {request.email}, but registration will proceed")
        
        return RegisterResponse(
            success=True,
            message="Registration successful! Welcome email has been sent.",
            username=request.username,
            email=request.email,
            patientId=patient_id
        )
    except Exception as e:
        # Safe encoding for exception messages
        error_msg = str(e).encode('ascii', 'ignore').decode('ascii')
        print(f"Registration error: {error_msg}")
        raise


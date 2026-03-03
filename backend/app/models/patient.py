from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime

class Patient(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str  # M, F, Other
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: List[str] = []
    medical_history: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: List[str] = []
    medical_history: List[str] = []

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[List[str]] = None
    medical_history: Optional[List[str]] = None



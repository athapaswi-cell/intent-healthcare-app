from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class Doctor(BaseModel):
    id: Optional[str] = None
    first_name: str
    last_name: str
    specialization: str
    qualification: str
    license_number: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hospital_id: Optional[str] = None
    department: Optional[str] = None
    experience_years: Optional[int] = None
    languages: List[str] = []
    consultation_fee: Optional[float] = None
    availability: Optional[str] = None  # Available, Busy, On Leave
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DoctorCreate(BaseModel):
    first_name: str
    last_name: str
    specialization: str
    qualification: str
    license_number: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    hospital_id: Optional[str] = None
    department: Optional[str] = None
    experience_years: Optional[int] = None
    languages: List[str] = []
    consultation_fee: Optional[float] = None
    availability: Optional[str] = "Available"

class DoctorUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    specialization: Optional[str] = None
    phone: Optional[str] = None
    hospital_id: Optional[str] = None
    department: Optional[str] = None
    experience_years: Optional[int] = None
    languages: Optional[List[str]] = None
    consultation_fee: Optional[float] = None
    availability: Optional[str] = None



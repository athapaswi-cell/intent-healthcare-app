from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class Hospital(BaseModel):
    id: Optional[str] = None
    name: str
    address: str
    city: str
    state: str
    zip_code: Optional[str] = None
    country: Optional[str] = "USA"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_phone: Optional[str] = None
    hospital_type: Optional[str] = None  # General, Specialty, Clinic, etc.
    total_beds: Optional[int] = None
    icu_beds: Optional[int] = None
    specialties: List[str] = []
    facilities: List[str] = []  # ICU, Emergency, Lab, Pharmacy, etc.
    operating_hours: Optional[str] = None
    website: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class HospitalCreate(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: Optional[str] = None
    country: Optional[str] = "USA"
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_phone: Optional[str] = None
    hospital_type: Optional[str] = None
    total_beds: Optional[int] = None
    icu_beds: Optional[int] = None
    specialties: List[str] = []
    facilities: List[str] = []
    operating_hours: Optional[str] = None
    website: Optional[str] = None

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    emergency_phone: Optional[str] = None
    hospital_type: Optional[str] = None
    total_beds: Optional[int] = None
    icu_beds: Optional[int] = None
    specialties: Optional[List[str]] = None
    facilities: Optional[List[str]] = None
    operating_hours: Optional[str] = None
    website: Optional[str] = None



"""
Data service for managing Doctors, Hospitals, and Patients
In production, this would connect to a database
"""
from typing import List, Optional, Dict
from datetime import datetime
import uuid

# In-memory storage (replace with database in production)
PATIENTS_DB: Dict[str, dict] = {}
DOCTORS_DB: Dict[str, dict] = {}
HOSPITALS_DB: Dict[str, dict] = {}

# Initialize with sample data
def init_sample_data():
    """Initialize with sample data for demonstration"""
    if not HOSPITALS_DB:
        # Sample Hospitals
        hospital1 = {
            "id": str(uuid.uuid4()),
            "name": "City General Hospital",
            "address": "123 Medical Center Drive",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "country": "USA",
            "phone": "+1-555-0100",
            "email": "info@citygeneral.com",
            "emergency_phone": "+1-555-0101",
            "hospital_type": "General",
            "total_beds": 500,
            "icu_beds": 50,
            "specialties": ["Cardiology", "Emergency Medicine", "Surgery", "Pediatrics"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology"],
            "operating_hours": "24/7",
            "website": "https://citygeneral.com",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        HOSPITALS_DB[hospital1["id"]] = hospital1

        hospital2 = {
            "id": str(uuid.uuid4()),
            "name": "Central Medical Center",
            "address": "456 Health Boulevard",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "country": "USA",
            "phone": "+1-555-0200",
            "email": "contact@centralmed.com",
            "emergency_phone": "+1-555-0201",
            "hospital_type": "Specialty",
            "total_beds": 300,
            "icu_beds": 30,
            "specialties": ["Oncology", "Neurology", "Cardiology"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy"],
            "operating_hours": "24/7",
            "website": "https://centralmed.com",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        HOSPITALS_DB[hospital2["id"]] = hospital2

    if not DOCTORS_DB:
        hospital_ids = list(HOSPITALS_DB.keys())
        # Sample Doctors
        doctor1 = {
            "id": str(uuid.uuid4()),
            "first_name": "Sarah",
            "last_name": "Johnson",
            "specialization": "Cardiology",
            "qualification": "MD, FACC",
            "license_number": "MD-12345",
            "email": "sarah.johnson@citygeneral.com",
            "phone": "+1-555-1001",
            "hospital_id": hospital_ids[0] if hospital_ids else None,
            "department": "Cardiology",
            "experience_years": 15,
            "languages": ["English", "Spanish"],
            "consultation_fee": 250.00,
            "availability": "Available",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        DOCTORS_DB[doctor1["id"]] = doctor1

        doctor2 = {
            "id": str(uuid.uuid4()),
            "first_name": "Michael",
            "last_name": "Chen",
            "specialization": "Emergency Medicine",
            "qualification": "MD, FACEP",
            "license_number": "MD-12346",
            "email": "michael.chen@citygeneral.com",
            "phone": "+1-555-1002",
            "hospital_id": hospital_ids[0] if hospital_ids else None,
            "department": "Emergency Medicine",
            "experience_years": 10,
            "languages": ["English", "Mandarin"],
            "consultation_fee": 200.00,
            "availability": "Available",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        DOCTORS_DB[doctor2["id"]] = doctor2

        doctor3 = {
            "id": str(uuid.uuid4()),
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "specialization": "Pediatrics",
            "qualification": "MD, FAAP",
            "license_number": "MD-12347",
            "email": "emily.rodriguez@centralmed.com",
            "phone": "+1-555-2001",
            "hospital_id": hospital_ids[1] if len(hospital_ids) > 1 else None,
            "department": "Pediatrics",
            "experience_years": 8,
            "languages": ["English", "Spanish"],
            "consultation_fee": 180.00,
            "availability": "Available",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        DOCTORS_DB[doctor3["id"]] = doctor3

    if not PATIENTS_DB:
        # Sample Patients
        patient1 = {
            "id": str(uuid.uuid4()),
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1985-05-15",
            "gender": "M",
            "email": "john.doe@email.com",
            "phone": "+1-555-3001",
            "address": "789 Patient Street, New York, NY 10002",
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "+1-555-3002",
            "blood_type": "O+",
            "allergies": ["Penicillin", "Peanuts"],
            "medical_history": ["Hypertension", "Type 2 Diabetes"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        PATIENTS_DB[patient1["id"]] = patient1

        patient2 = {
            "id": str(uuid.uuid4()),
            "first_name": "Maria",
            "last_name": "Garcia",
            "date_of_birth": "1990-08-22",
            "gender": "F",
            "email": "maria.garcia@email.com",
            "phone": "+1-555-3003",
            "address": "321 Health Avenue, Los Angeles, CA 90002",
            "emergency_contact_name": "Carlos Garcia",
            "emergency_contact_phone": "+1-555-3004",
            "blood_type": "A+",
            "allergies": ["Latex"],
            "medical_history": ["Asthma"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        PATIENTS_DB[patient2["id"]] = patient2

# Initialize sample data
init_sample_data()

# Patient operations
def get_all_patients() -> List[dict]:
    return list(PATIENTS_DB.values())

def get_patient(patient_id: str) -> Optional[dict]:
    return PATIENTS_DB.get(patient_id)

def create_patient(patient_data: dict) -> dict:
    patient_id = str(uuid.uuid4())
    patient = {
        **patient_data,
        "id": patient_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    PATIENTS_DB[patient_id] = patient
    return patient

def update_patient(patient_id: str, patient_data: dict) -> Optional[dict]:
    if patient_id not in PATIENTS_DB:
        return None
    existing = PATIENTS_DB[patient_id]
    updated = {**existing, **patient_data, "updated_at": datetime.now().isoformat()}
    PATIENTS_DB[patient_id] = updated
    return updated

def delete_patient(patient_id: str) -> bool:
    if patient_id in PATIENTS_DB:
        del PATIENTS_DB[patient_id]
        return True
    return False

# Doctor operations
def get_all_doctors() -> List[dict]:
    return list(DOCTORS_DB.values())

def get_doctor(doctor_id: str) -> Optional[dict]:
    return DOCTORS_DB.get(doctor_id)

def get_doctors_by_hospital(hospital_id: str) -> List[dict]:
    return [d for d in DOCTORS_DB.values() if d.get("hospital_id") == hospital_id]

def get_doctors_by_specialization(specialization: str) -> List[dict]:
    return [d for d in DOCTORS_DB.values() if d.get("specialization") == specialization]

def create_doctor(doctor_data: dict) -> dict:
    doctor_id = str(uuid.uuid4())
    doctor = {
        **doctor_data,
        "id": doctor_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    DOCTORS_DB[doctor_id] = doctor
    return doctor

def update_doctor(doctor_id: str, doctor_data: dict) -> Optional[dict]:
    if doctor_id not in DOCTORS_DB:
        return None
    existing = DOCTORS_DB[doctor_id]
    updated = {**existing, **doctor_data, "updated_at": datetime.now().isoformat()}
    DOCTORS_DB[doctor_id] = updated
    return updated

def delete_doctor(doctor_id: str) -> bool:
    if doctor_id in DOCTORS_DB:
        del DOCTORS_DB[doctor_id]
        return True
    return False

# Hospital operations
def get_all_hospitals() -> List[dict]:
    return list(HOSPITALS_DB.values())

def get_hospital(hospital_id: str) -> Optional[dict]:
    return HOSPITALS_DB.get(hospital_id)

def search_hospitals(city: Optional[str] = None, state: Optional[str] = None, specialty: Optional[str] = None) -> List[dict]:
    results = list(HOSPITALS_DB.values())
    if city:
        results = [h for h in results if h.get("city", "").lower() == city.lower()]
    if state:
        results = [h for h in results if h.get("state", "").lower() == state.lower()]
    if specialty:
        results = [h for h in results if specialty.lower() in [s.lower() for s in h.get("specialties", [])]]
    return results

def create_hospital(hospital_data: dict) -> dict:
    hospital_id = str(uuid.uuid4())
    hospital = {
        **hospital_data,
        "id": hospital_id,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    HOSPITALS_DB[hospital_id] = hospital
    return hospital

def update_hospital(hospital_id: str, hospital_data: dict) -> Optional[dict]:
    if hospital_id not in HOSPITALS_DB:
        return None
    existing = HOSPITALS_DB[hospital_id]
    updated = {**existing, **hospital_data, "updated_at": datetime.now().isoformat()}
    HOSPITALS_DB[hospital_id] = updated
    return updated

def delete_hospital(hospital_id: str) -> bool:
    if hospital_id in HOSPITALS_DB:
        del HOSPITALS_DB[hospital_id]
        return True
    return False



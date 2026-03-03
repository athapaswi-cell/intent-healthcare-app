"""
Real Data Service with comprehensive hospital, patient, doctor, and bed availability data
This service provides realistic healthcare data for demonstration purposes
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid
import random

# In-memory storage with realistic data
PATIENTS_DB: Dict[str, dict] = {}
DOCTORS_DB: Dict[str, dict] = {}
HOSPITALS_DB: Dict[str, dict] = {}
BED_AVAILABILITY_DB: Dict[str, dict] = {}

def generate_realistic_data():
    """Generate comprehensive realistic healthcare data"""
    
    # Real Hospital Data
    hospitals_data = [
        {
            "name": "Mayo Clinic",
            "address": "200 First Street SW",
            "city": "Rochester",
            "state": "MN",
            "zip_code": "55905",
            "phone": "+1-507-284-2511",
            "emergency_phone": "+1-507-284-2511",
            "hospital_type": "Academic Medical Center",
            "total_beds": 1265,
            "icu_beds": 150,
            "specialties": ["Cardiology", "Oncology", "Neurology", "Orthopedics", "Gastroenterology", "Endocrinology"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "Cardiac Cath Lab", "MRI", "CT Scan"],
            "operating_hours": "24/7",
            "website": "https://mayoclinic.org",
            "rating": 4.9,
            "trauma_level": "Level I"
        },
        {
            "name": "Johns Hopkins Hospital",
            "address": "1800 Orleans Street",
            "city": "Baltimore",
            "state": "MD",
            "zip_code": "21287",
            "phone": "+1-410-955-5000",
            "emergency_phone": "+1-410-955-6070",
            "hospital_type": "Academic Medical Center",
            "total_beds": 1154,
            "icu_beds": 180,
            "specialties": ["Neurosurgery", "Cardiology", "Oncology", "Pediatrics", "Psychiatry", "Rheumatology"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "NICU", "Burn Center"],
            "operating_hours": "24/7",
            "website": "https://hopkinsmedicine.org",
            "rating": 4.8,
            "trauma_level": "Level I"
        },
        {
            "name": "Cleveland Clinic",
            "address": "9500 Euclid Avenue",
            "city": "Cleveland",
            "state": "OH",
            "zip_code": "44195",
            "phone": "+1-216-444-2200",
            "emergency_phone": "+1-216-444-7000",
            "hospital_type": "Academic Medical Center",
            "total_beds": 1285,
            "icu_beds": 160,
            "specialties": ["Cardiology", "Neurology", "Urology", "Gastroenterology", "Orthopedics", "Dermatology"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "Heart Center", "Cancer Center"],
            "operating_hours": "24/7",
            "website": "https://clevelandclinic.org",
            "rating": 4.7,
            "trauma_level": "Level I"
        },
        {
            "name": "Massachusetts General Hospital",
            "address": "55 Fruit Street",
            "city": "Boston",
            "state": "MA",
            "zip_code": "02114",
            "phone": "+1-617-726-2000",
            "emergency_phone": "+1-617-726-7000",
            "hospital_type": "Academic Medical Center",
            "total_beds": 999,
            "icu_beds": 140,
            "specialties": ["Emergency Medicine", "Surgery", "Internal Medicine", "Pediatrics", "Psychiatry", "Radiology"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "Trauma Center", "Burn Unit"],
            "operating_hours": "24/7",
            "website": "https://massgeneral.org",
            "rating": 4.6,
            "trauma_level": "Level I"
        },
        {
            "name": "Cedars-Sinai Medical Center",
            "address": "8700 Beverly Boulevard",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90048",
            "phone": "+1-310-423-3277",
            "emergency_phone": "+1-310-423-8780",
            "hospital_type": "Non-profit Academic",
            "total_beds": 886,
            "icu_beds": 120,
            "specialties": ["Cardiology", "Oncology", "Neurology", "Gastroenterology", "Orthopedics", "Women's Health"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "Heart Institute", "Cancer Center"],
            "operating_hours": "24/7",
            "website": "https://cedars-sinai.org",
            "rating": 4.5,
            "trauma_level": "Level II"
        },
        {
            "name": "Houston Methodist Hospital",
            "address": "6565 Fannin Street",
            "city": "Houston",
            "state": "TX",
            "zip_code": "77030",
            "phone": "+1-713-790-3311",
            "emergency_phone": "+1-713-790-2700",
            "hospital_type": "Academic Medical Center",
            "total_beds": 907,
            "icu_beds": 110,
            "specialties": ["Cardiology", "Neurology", "Oncology", "Orthopedics", "Transplant", "Emergency Medicine"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "Transplant Center", "Cancer Center"],
            "operating_hours": "24/7",
            "website": "https://houstonmethodist.org",
            "rating": 4.4,
            "trauma_level": "Level I"
        },
        {
            "name": "NewYork-Presbyterian Hospital",
            "address": "525 East 68th Street",
            "city": "New York",
            "state": "NY",
            "zip_code": "10065",
            "phone": "+1-212-746-5454",
            "emergency_phone": "+1-212-746-0050",
            "hospital_type": "Academic Medical Center",
            "total_beds": 2236,
            "icu_beds": 280,
            "specialties": ["Cardiology", "Neurology", "Oncology", "Pediatrics", "Surgery", "Emergency Medicine"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "NICU", "Trauma Center"],
            "operating_hours": "24/7",
            "website": "https://nyp.org",
            "rating": 4.3,
            "trauma_level": "Level I"
        },
        {
            "name": "UCSF Medical Center",
            "address": "505 Parnassus Avenue",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94143",
            "phone": "+1-415-476-1000",
            "emergency_phone": "+1-415-353-1037",
            "hospital_type": "Academic Medical Center",
            "total_beds": 878,
            "icu_beds": 100,
            "specialties": ["Neurology", "Oncology", "Cardiology", "Pediatrics", "Psychiatry", "Surgery"],
            "facilities": ["ICU", "Emergency", "Laboratory", "Pharmacy", "Radiology", "Surgery", "Children's Hospital", "Cancer Center"],
            "operating_hours": "24/7",
            "website": "https://ucsfhealth.org",
            "rating": 4.6,
            "trauma_level": "Level I"
        }
    ]

    # Generate hospital records
    for hospital_data in hospitals_data:
        hospital_id = str(uuid.uuid4())
        hospital = {
            **hospital_data,
            "id": hospital_id,
            "country": "USA",
            "email": f"info@{hospital_data['name'].lower().replace(' ', '').replace('-', '')}.com",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        HOSPITALS_DB[hospital_id] = hospital

    # Generate realistic doctors
    doctor_names = [
        ("Sarah", "Johnson", "Cardiology", "MD, FACC", 15),
        ("Michael", "Chen", "Emergency Medicine", "MD, FACEP", 12),
        ("Emily", "Rodriguez", "Pediatrics", "MD, FAAP", 8),
        ("David", "Williams", "Neurology", "MD, FAAN", 20),
        ("Lisa", "Brown", "Oncology", "MD, FASCO", 18),
        ("James", "Davis", "Orthopedics", "MD, FAAOS", 14),
        ("Maria", "Garcia", "Gastroenterology", "MD, FACG", 11),
        ("Robert", "Miller", "Cardiology", "MD, FACC", 16),
        ("Jennifer", "Wilson", "Dermatology", "MD, FAAD", 9),
        ("Christopher", "Moore", "Urology", "MD, FACS", 13),
        ("Amanda", "Taylor", "Psychiatry", "MD, FAPA", 10),
        ("Daniel", "Anderson", "Radiology", "MD, FACR", 17),
        ("Jessica", "Thomas", "Endocrinology", "MD, FACE", 7),
        ("Matthew", "Jackson", "Surgery", "MD, FACS", 19),
        ("Ashley", "White", "Internal Medicine", "MD, FACP", 6),
        ("Andrew", "Harris", "Anesthesiology", "MD, FASA", 12),
        ("Stephanie", "Martin", "Obstetrics", "MD, FACOG", 11),
        ("Kevin", "Thompson", "Ophthalmology", "MD, FACS", 15),
        ("Rachel", "Garcia", "Rheumatology", "MD, FACR", 8),
        ("Brandon", "Lee", "Emergency Medicine", "MD, FACEP", 5)
    ]

    hospital_ids = list(HOSPITALS_DB.keys())
    consultation_fees = {
        "Cardiology": 350, "Emergency Medicine": 250, "Pediatrics": 200,
        "Neurology": 400, "Oncology": 450, "Orthopedics": 300,
        "Gastroenterology": 280, "Dermatology": 220, "Urology": 320,
        "Psychiatry": 260, "Radiology": 180, "Endocrinology": 290,
        "Surgery": 500, "Internal Medicine": 200, "Anesthesiology": 350,
        "Obstetrics": 250, "Ophthalmology": 240, "Rheumatology": 270
    }

    for first_name, last_name, specialization, qualification, experience in doctor_names:
        doctor_id = str(uuid.uuid4())
        hospital_id = random.choice(hospital_ids)
        availability_options = ["Available", "Busy", "On Call", "Available"]  # Weighted towards available
        
        doctor = {
            "id": doctor_id,
            "first_name": first_name,
            "last_name": last_name,
            "specialization": specialization,
            "qualification": qualification,
            "license_number": f"MD-{random.randint(10000, 99999)}",
            "email": f"{first_name.lower()}.{last_name.lower()}@{HOSPITALS_DB[hospital_id]['name'].lower().replace(' ', '').replace('-', '')}.com",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "hospital_id": hospital_id,
            "department": specialization,
            "experience_years": experience,
            "languages": random.sample(["English", "Spanish", "French", "German", "Mandarin", "Portuguese"], random.randint(1, 3)),
            "consultation_fee": consultation_fees.get(specialization, 250),
            "availability": random.choice(availability_options),
            "next_available": (datetime.now() + timedelta(days=random.randint(1, 14))).strftime("%Y-%m-%d"),
            "rating": round(random.uniform(4.0, 5.0), 1),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        DOCTORS_DB[doctor_id] = doctor

    # Generate realistic patients
    patient_names = [
        ("John", "Doe", "1985-05-15", "M", "O+", ["Penicillin"], ["Hypertension", "Type 2 Diabetes"]),
        ("Maria", "Garcia", "1990-08-22", "F", "A+", ["Latex"], ["Asthma"]),
        ("William", "Smith", "1978-12-03", "M", "B+", ["Shellfish"], ["High Cholesterol"]),
        ("Jennifer", "Johnson", "1992-03-18", "F", "AB+", [], ["Migraine"]),
        ("Michael", "Brown", "1965-11-30", "M", "O-", ["Aspirin"], ["Arthritis", "Hypertension"]),
        ("Sarah", "Davis", "1988-07-14", "F", "A-", ["Peanuts"], ["Anxiety"]),
        ("Robert", "Wilson", "1975-09-25", "M", "B-", [], ["Back Pain"]),
        ("Lisa", "Miller", "1983-01-08", "F", "AB-", ["Sulfa"], ["Depression"]),
        ("David", "Moore", "1970-06-12", "M", "O+", ["Codeine"], ["Diabetes", "Heart Disease"]),
        ("Jessica", "Taylor", "1995-04-27", "F", "A+", [], ["Healthy"]),
        ("Christopher", "Anderson", "1982-10-19", "M", "B+", ["Iodine"], ["Kidney Stones"]),
        ("Amanda", "Thomas", "1987-02-14", "F", "O-", ["Morphine"], ["Fibromyalgia"]),
        ("Matthew", "Jackson", "1973-08-05", "M", "A-", [], ["COPD"]),
        ("Ashley", "White", "1991-12-22", "F", "AB+", ["Latex", "Penicillin"], ["Allergic Rhinitis"]),
        ("Daniel", "Harris", "1969-05-30", "M", "B-", ["Aspirin"], ["Prostate Issues"]),
        ("Stephanie", "Martin", "1986-09-17", "F", "O+", [], ["Pregnancy - 2nd Trimester"]),
        ("Kevin", "Thompson", "1979-03-11", "M", "A+", ["Shellfish"], ["Sleep Apnea"]),
        ("Rachel", "Garcia", "1993-07-28", "F", "B+", ["Peanuts"], ["Eating Disorder Recovery"]),
        ("Brandon", "Lee", "1984-11-02", "M", "AB-", [], ["Sports Injury"]),
        ("Nicole", "Clark", "1989-01-25", "F", "O-", ["Sulfa"], ["Postpartum Depression"])
    ]

    cities_states = [
        ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
        ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
        ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
        ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"), ("San Francisco", "CA"),
        ("Indianapolis", "IN"), ("Seattle", "WA"), ("Denver", "CO"), ("Boston", "MA")
    ]

    for first_name, last_name, dob, gender, blood_type, allergies, medical_history in patient_names:
        patient_id = str(uuid.uuid4())
        city, state = random.choice(cities_states)
        
        patient = {
            "id": patient_id,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": dob,
            "gender": gender,
            "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
            "phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar'])} {random.choice(['Street', 'Avenue', 'Drive', 'Lane'])}, {city}, {state} {random.randint(10000, 99999)}",
            "emergency_contact_name": f"{random.choice(['Jane', 'John', 'Mary', 'James'])} {last_name}",
            "emergency_contact_phone": f"+1-{random.randint(200, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "blood_type": blood_type,
            "allergies": allergies,
            "medical_history": medical_history,
            "insurance_provider": random.choice(["Blue Cross Blue Shield", "Aetna", "Cigna", "UnitedHealth", "Kaiser Permanente"]),
            "insurance_id": f"INS-{random.randint(100000, 999999)}",
            "primary_care_physician": random.choice(list(DOCTORS_DB.keys())) if DOCTORS_DB else None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        PATIENTS_DB[patient_id] = patient

    # Generate bed availability data
    for hospital_id, hospital in HOSPITALS_DB.items():
        total_beds = hospital["total_beds"]
        icu_beds = hospital["icu_beds"]
        
        # Calculate realistic occupancy (70-95%)
        occupancy_rate = random.uniform(0.70, 0.95)
        occupied_beds = int(total_beds * occupancy_rate)
        available_beds = total_beds - occupied_beds
        
        icu_occupancy_rate = random.uniform(0.75, 0.98)  # ICU typically higher occupancy
        occupied_icu = int(icu_beds * icu_occupancy_rate)
        available_icu = icu_beds - occupied_icu
        
        bed_data = {
            "id": str(uuid.uuid4()),
            "hospital_id": hospital_id,
            "hospital_name": hospital["name"],
            "total_beds": total_beds,
            "occupied_beds": occupied_beds,
            "available_beds": available_beds,
            "icu_beds": icu_beds,
            "occupied_icu": occupied_icu,
            "available_icu": available_icu,
            "emergency_beds": random.randint(5, 20),
            "available_emergency": random.randint(1, 8),
            "surgery_rooms": random.randint(8, 25),
            "available_surgery": random.randint(1, 5),
            "occupancy_rate": round(occupancy_rate * 100, 1),
            "icu_occupancy_rate": round(icu_occupancy_rate * 100, 1),
            "last_updated": datetime.now().isoformat(),
            "status": "Normal" if occupancy_rate < 0.85 else "High" if occupancy_rate < 0.95 else "Critical"
        }
        BED_AVAILABILITY_DB[hospital_id] = bed_data

# Initialize realistic data
generate_realistic_data()

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
    return [d for d in DOCTORS_DB.values() if d.get("specialization", "").lower() == specialization.lower()]

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

# Bed availability operations
def get_bed_availability(hospital_id: str) -> Optional[dict]:
    return BED_AVAILABILITY_DB.get(hospital_id)

def get_all_bed_availability() -> List[dict]:
    return list(BED_AVAILABILITY_DB.values())

def update_bed_availability(hospital_id: str, bed_data: dict) -> Optional[dict]:
    if hospital_id not in BED_AVAILABILITY_DB:
        return None
    existing = BED_AVAILABILITY_DB[hospital_id]
    updated = {**existing, **bed_data, "last_updated": datetime.now().isoformat()}
    BED_AVAILABILITY_DB[hospital_id] = updated
    return updated
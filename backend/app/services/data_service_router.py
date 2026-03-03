"""
Data Service Router - Routes to Hybrid data service for REAL FHIR + Mock data
Combines real FHIR data with comprehensive mock data for demonstration
"""
from app.config import EPIC_FHIR_ENABLED, USE_PUBLIC_FHIR
from typing import List, Dict, Optional

# Import Hybrid data service - FHIR + Mock data
try:
    from app.services.hybrid_data_service import hybrid_data_service
    FHIR_AVAILABLE = True
    print("[INFO] Hybrid data service (FHIR + Mock) loaded successfully", flush=True)
except Exception as e:
    print(f"[ERROR] Hybrid data service not available: {e}", flush=True)
    FHIR_AVAILABLE = False

# Import realistic data service ONLY for write operations (create/update/delete)
from app.services.real_data_service import (
    create_patient as real_create_patient,
    update_patient as real_update_patient,
    delete_patient as real_delete_patient,
    create_doctor as real_create_doctor,
    update_doctor as real_update_doctor,
    delete_doctor as real_delete_doctor,
    create_hospital as real_create_hospital,
    update_hospital as real_update_hospital,
    delete_hospital as real_delete_hospital,
    get_bed_availability as real_get_bed_availability,
    get_all_bed_availability as real_get_all_bed_availability,
    update_bed_availability as real_update_bed_availability
)

# Determine which service to use - MUST use FHIR for real data
USE_FHIR = (EPIC_FHIR_ENABLED or USE_PUBLIC_FHIR) and FHIR_AVAILABLE

def _get_fhir_data_only(method_name: str, *args, **kwargs):
    """Get data from FHIR ONLY - return empty list if FHIR fails (NO FALLBACK)"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        print(f"[WARNING] FHIR not enabled or not available. Returning empty list.", flush=True)
        return []
    
    try:
        method = getattr(epic_fhir_data_service, method_name)
        result = method(*args, **kwargs)
        if result is None:
            return []
        return result if isinstance(result, list) else []
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        print(f"[ERROR] Returning empty list - NO FALLBACK to mock data", flush=True)
        return []

# Export functions - FHIR ONLY (no fallback)
def get_all_patients(use_cache: bool = False) -> List[Dict]:
    """Get all patients from Hybrid service (FHIR + Mock data)"""
    if not FHIR_AVAILABLE:
        print("[ERROR] Hybrid data service not available", flush=True)
        return []
    try:
        return hybrid_data_service.get_all_patients()
    except Exception as e:
        print(f"[ERROR] Hybrid patients call failed: {e}", flush=True)
        return []

def get_patient(patient_id: str) -> Optional[Dict]:
    """Get patient from FHIR ONLY - returns None if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        print(f"[WARNING] FHIR not enabled. Returning None.", flush=True)
        return None
    try:
        # For single patient, we'll need to implement this in epic_fhir_data_service
        patients = epic_fhir_data_service.get_all_patients()
        for patient in patients:
            if patient.get('id') == patient_id:
                return patient
        return None
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return None

def create_patient(patient_data: Dict) -> Dict:
    return real_create_patient(patient_data)

def update_patient(patient_id: str, patient_data: Dict) -> Optional[Dict]:
    return real_update_patient(patient_id, patient_data)

def delete_patient(patient_id: str) -> bool:
    return real_delete_patient(patient_id)

def get_all_doctors(use_cache: bool = False) -> List[Dict]:
    """Get all doctors from Hybrid service (FHIR + Mock data)"""
    if not FHIR_AVAILABLE:
        print("[ERROR] Hybrid data service not available", flush=True)
        return []
    try:
        return hybrid_data_service.get_all_doctors()
    except Exception as e:
        print(f"[ERROR] Hybrid doctors call failed: {e}", flush=True)
        return []

def get_doctor(doctor_id: str) -> Optional[Dict]:
    """Get doctor from FHIR ONLY - returns None if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return None
    try:
        doctors = epic_fhir_data_service.get_all_doctors()
        for doctor in doctors:
            if doctor.get('id') == doctor_id:
                return doctor
        return None
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return None

def get_doctors_by_hospital(hospital_id: str) -> List[Dict]:
    """Get doctors by hospital from FHIR ONLY - returns empty list if FHIR fails"""
    # For now, return all doctors since FHIR doesn't have direct hospital-doctor relationship
    return _get_fhir_data_only('get_all_doctors')

def get_doctors_by_specialization(specialization: str) -> List[Dict]:
    """Get doctors by specialization from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        doctors = epic_fhir_data_service.get_all_doctors()
        return [doc for doc in doctors if doc.get('specialization', '').lower() == specialization.lower()]
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

def create_doctor(doctor_data: Dict) -> Dict:
    return real_create_doctor(doctor_data)

def update_doctor(doctor_id: str, doctor_data: Dict) -> Optional[Dict]:
    return real_update_doctor(doctor_id, doctor_data)

def delete_doctor(doctor_id: str) -> bool:
    return real_delete_doctor(doctor_id)

def get_all_hospitals(use_cache: bool = False) -> List[Dict]:
    """Get all hospitals from Hybrid service (FHIR + Mock data)"""
    if not FHIR_AVAILABLE:
        print("[ERROR] Hybrid data service not available", flush=True)
        return []
    try:
        return hybrid_data_service.get_all_hospitals()
    except Exception as e:
        print(f"[ERROR] Hybrid hospitals call failed: {e}", flush=True)
        return []

def get_hospital(hospital_id: str) -> Optional[Dict]:
    """Get hospital from FHIR ONLY - returns None if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return None
    try:
        hospitals = epic_fhir_data_service.get_all_hospitals()
        for hospital in hospitals:
            if hospital.get('id') == hospital_id:
                return hospital
        return None
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return None

def search_hospitals(city: Optional[str] = None, state: Optional[str] = None, specialty: Optional[str] = None) -> List[Dict]:
    """Search hospitals from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        hospitals = epic_fhir_data_service.get_all_hospitals()
        filtered = hospitals
        
        if city:
            filtered = [h for h in filtered if h.get('city', '').lower() == city.lower()]
        if state:
            filtered = [h for h in filtered if h.get('state', '').lower() == state.lower()]
        if specialty:
            filtered = [h for h in filtered if specialty.lower() in [s.lower() for s in h.get('specialties', [])]]
            
        return filtered
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

def create_hospital(hospital_data: Dict) -> Dict:
    return real_create_hospital(hospital_data)

def update_hospital(hospital_id: str, hospital_data: Dict) -> Optional[Dict]:
    return real_update_hospital(hospital_id, hospital_data)

def delete_hospital(hospital_id: str) -> bool:
    return real_delete_hospital(hospital_id)

def get_bed_availability(hospital_id: str) -> Dict:
    return real_get_bed_availability(hospital_id)

def get_all_bed_availability() -> List[Dict]:
    return real_get_all_bed_availability()

def update_bed_availability(hospital_id: str, bed_data: Dict) -> bool:
    return real_update_bed_availability(hospital_id, bed_data)

# For encounters/records - FHIR ONLY (no fallback)
def get_all_encounters(hospital_id: Optional[str] = None, patient_id: Optional[str] = None) -> List[Dict]:
    """Get encounters from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        return epic_fhir_data_service.get_encounters(hospital_id=hospital_id, patient_id=patient_id)
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

def get_encounters_by_patient(patient_id: str) -> List[Dict]:
    """Get encounters by patient from FHIR ONLY"""
    return get_all_encounters(patient_id=patient_id)

def get_encounters_by_hospital(hospital_id: str) -> List[Dict]:
    """Get encounters by hospital from FHIR ONLY"""
    return get_all_encounters(hospital_id=hospital_id)

# For insurance - FHIR ONLY (no fallback)
def get_insurance_claims(hospital_id: Optional[str] = None) -> List[Dict]:
    """Get insurance claims from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        return epic_fhir_data_service.get_insurance_claims(hospital_id=hospital_id)
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

def get_coverage_rules(hospital_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Get coverage rules from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        return epic_fhir_data_service.get_coverage_rules(hospital_id=hospital_id, limit=limit)
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

# For medical history - FHIR ONLY (no fallback)
def get_medical_history(patient_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
    """Get medical history from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        return epic_fhir_data_service.get_medical_history(patient_id=patient_id, limit=limit)
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

# For bed availability - FHIR ONLY (no fallback)
def get_bed_availability(hospital_id: str) -> Dict:
    """Get bed availability from FHIR ONLY - returns empty dict if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return {}
    try:
        bed_data = epic_fhir_data_service.get_bed_availability(hospital_id=hospital_id)
        return bed_data[0] if bed_data else {}
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return {}

def get_all_bed_availability() -> List[Dict]:
    """Get all bed availability from FHIR ONLY - returns empty list if FHIR fails"""
    if not USE_FHIR or not FHIR_AVAILABLE:
        return []
    try:
        return epic_fhir_data_service.get_bed_availability()
    except Exception as e:
        print(f"[ERROR] FHIR call failed: {e}", flush=True)
        return []

def update_bed_availability(hospital_id: str, bed_data: Dict) -> bool:
    """Update bed availability - use realistic data service for write operations"""
    return real_update_bed_availability(hospital_id, bed_data)

# Alias for compatibility
get_medical_records = get_all_encounters

# Export all functions
__all__ = [
    "get_all_patients", "get_patient", "create_patient", "update_patient", "delete_patient",
    "get_all_doctors", "get_doctor", "get_doctors_by_hospital", "get_doctors_by_specialization",
    "create_doctor", "update_doctor", "delete_doctor",
    "get_all_hospitals", "get_hospital", "search_hospitals",
    "create_hospital", "update_hospital", "delete_hospital",
    "get_bed_availability", "get_all_bed_availability", "update_bed_availability",
    "get_all_encounters", "get_encounters_by_patient", "get_encounters_by_hospital",
    "get_insurance_claims", "get_coverage_rules", "get_medical_history"
]



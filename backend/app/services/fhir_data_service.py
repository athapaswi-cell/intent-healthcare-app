"""
FHIR Data Service - Real-time data retrieval from FHIR servers
"""
from typing import List, Dict, Optional
from backend.app.services.fhir_client import get_fhir_client
from backend.app.services.fhir_mapper import (
    fhir_patient_to_model,
    fhir_practitioner_to_doctor,
    fhir_organization_to_hospital,
    fhir_encounter_to_record,
    fhir_claim_to_insurance_claim,
    fhir_coverage_to_coverage_rule,
    fhir_condition_to_medical_history,
    fhir_encounter_to_visit
)

# Cache for performance (optional, can be disabled for real-time)
USE_CACHE = False
_cache = {
    "patients": {},
    "doctors": {},
    "hospitals": {},
    "records": {}
}

def get_all_patients(use_cache: bool = USE_CACHE) -> List[Dict]:
    """Get all patients from FHIR server"""
    import sys
    print(f"[FHIR] Fetching patients from EPIC FHIR...", flush=True)
    sys.stdout.flush()
    try:
        client = get_fhir_client()
        
        # Search for Patient resources
        fhir_patients = client.search("Patient", params={"_count": 50})
        print(f"[FHIR] Found {len(fhir_patients)} patients from EPIC FHIR", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"[ERROR] Exception in get_all_patients: {e}", flush=True)
        sys.stdout.flush()
        raise
    
    patients = []
    for fhir_patient in fhir_patients:
        try:
            patient = fhir_patient_to_model(fhir_patient)
            patients.append(patient)
        except Exception as e:
            print(f"Error mapping FHIR Patient: {e}")
            continue
    
    return patients

def get_patient(patient_id: str) -> Optional[Dict]:
    """Get a specific patient by ID from FHIR server"""
    client = get_fhir_client()
    fhir_patient = client.read("Patient", patient_id)
    
    if fhir_patient:
        try:
            return fhir_patient_to_model(fhir_patient)
        except Exception as e:
            print(f"Error mapping FHIR Patient: {e}")
            return None
    return None

def get_all_doctors(use_cache: bool = USE_CACHE) -> List[Dict]:
    """Get all doctors (Practitioners) from FHIR server"""
    import sys
    print(f"[FHIR] Fetching doctors from EPIC FHIR...", flush=True)
    sys.stdout.flush()
    try:
        client = get_fhir_client()
        
        # Search for Practitioner resources
        fhir_practitioners = client.search("Practitioner", params={"_count": 50})
        print(f"[FHIR] Found {len(fhir_practitioners)} doctors from EPIC FHIR", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"[ERROR] Exception in get_all_doctors: {e}", flush=True)
        sys.stdout.flush()
        raise
    
    doctors = []
    for fhir_practitioner in fhir_practitioners:
        try:
            doctor = fhir_practitioner_to_doctor(fhir_practitioner)
            doctors.append(doctor)
        except Exception as e:
            print(f"Error mapping FHIR Practitioner: {e}")
            continue
    
    return doctors

def get_doctor(doctor_id: str) -> Optional[Dict]:
    """Get a specific doctor by ID from FHIR server"""
    client = get_fhir_client()
    fhir_practitioner = client.read("Practitioner", doctor_id)
    
    if fhir_practitioner:
        try:
            return fhir_practitioner_to_doctor(fhir_practitioner)
        except Exception as e:
            print(f"Error mapping FHIR Practitioner: {e}")
            return None
    return None

def get_doctors_by_hospital(hospital_id: str) -> List[Dict]:
    """
    Get doctors by hospital using multiple methods:
    1. PractitionerRole (primary method - links practitioners to organizations)
    2. Encounter participants (fallback - finds doctors who have encounters at this hospital)
    """
    client = get_fhir_client()
    
    doctors = []
    seen_doctor_ids = set()  # Avoid duplicates
    
    # Method 1: Search PractitionerRole by organization (primary method)
    search_params = [
        {"organization": hospital_id, "_count": 100},
        {"organization": f"Organization/{hospital_id}", "_count": 100},
    ]
    
    for params in search_params:
        fhir_roles = client.search("PractitionerRole", params=params)
        
        for role in fhir_roles:
            # Verify this role is for the correct organization
            org_ref = None
            org_obj = role.get("organization")
            if isinstance(org_obj, dict):
                org_ref = org_obj.get("reference", "")
            elif isinstance(org_obj, str):
                org_ref = org_obj
            
            # Check if organization matches (handle different reference formats)
            org_id = None
            if org_ref:
                org_id = org_ref.replace("Organization/", "").split("?")[0]
            
            if org_id != hospital_id:
                continue  # Skip if organization doesn't match
            
            # Extract practitioner reference - handle different formats
            practitioner_ref = None
            practitioner_obj = role.get("practitioner")
            
            if isinstance(practitioner_obj, dict):
                practitioner_ref = practitioner_obj.get("reference", "")
            elif isinstance(practitioner_obj, str):
                practitioner_ref = practitioner_obj
            
            if practitioner_ref:
                # Extract ID from reference (handle formats like "Practitioner/123" or just "123")
                practitioner_id = practitioner_ref.replace("Practitioner/", "").split("?")[0]
                
                if practitioner_id and practitioner_id not in seen_doctor_ids:
                    doctor = get_doctor(practitioner_id)
                    if doctor:
                        seen_doctor_ids.add(practitioner_id)
                        
                        # Update with role information
                        doctor["hospital_id"] = hospital_id
                        
                        # Extract department/role code
                        role_codes = role.get("code", [])
                        if role_codes:
                            if isinstance(role_codes[0], dict):
                                doctor["department"] = role_codes[0].get("text") or role_codes[0].get("coding", [{}])[0].get("display", "")
                            elif isinstance(role_codes[0], str):
                                doctor["department"] = role_codes[0]
                        
                        # Extract specialty from role
                        specialties = role.get("specialty", [])
                        if specialties:
                            specialty_text = specialties[0].get("coding", [{}])[0].get("display", "")
                            if specialty_text and specialty_text != doctor.get("specialization", ""):
                                doctor["department_specialty"] = specialty_text
                        
                        # Extract location if available
                        locations = role.get("location", [])
                        if locations:
                            location_ref = locations[0].get("reference", "") if isinstance(locations[0], dict) else locations[0]
                            if location_ref:
                                doctor["location"] = location_ref
                        
                        doctors.append(doctor)
    
    # Method 2: Fallback - Find doctors through Encounters at this hospital
    # This helps when PractitionerRole data is limited
    if len(doctors) == 0:
        # Search for Encounters at this hospital
        encounter_params = [
            {"service-provider": hospital_id, "_count": 50},
            {"service-provider": f"Organization/{hospital_id}", "_count": 50},
        ]
        
        for params in encounter_params:
            fhir_encounters = client.search("Encounter", params=params)
            
            for encounter in fhir_encounters:
                # Get participants (doctors) from the encounter
                participants = encounter.get("participant", [])
                for participant in participants:
                    individual_ref = None
                    individual_obj = participant.get("individual")
                    
                    if isinstance(individual_obj, dict):
                        individual_ref = individual_obj.get("reference", "")
                    elif isinstance(individual_obj, str):
                        individual_ref = individual_obj
                    
                    if individual_ref and "Practitioner/" in individual_ref:
                        practitioner_id = individual_ref.replace("Practitioner/", "").split("?")[0]
                        
                        if practitioner_id and practitioner_id not in seen_doctor_ids:
                            doctor = get_doctor(practitioner_id)
                            if doctor:
                                seen_doctor_ids.add(practitioner_id)
                                doctor["hospital_id"] = hospital_id
                                # Mark as found via encounters (less definitive than PractitionerRole)
                                doctor["source"] = "encounter"
                                doctors.append(doctor)
    
    return doctors

def get_doctors_by_specialization(specialization: str) -> List[Dict]:
    """Get doctors by specialization"""
    all_doctors = get_all_doctors()
    return [d for d in all_doctors if specialization.lower() in d.get("specialization", "").lower()]

def get_all_hospitals(use_cache: bool = USE_CACHE) -> List[Dict]:
    """Get all hospitals (Organizations) from FHIR server"""
    import sys
    print(f"[FHIR] Fetching hospitals from EPIC FHIR...", flush=True)
    sys.stdout.flush()
    try:
        client = get_fhir_client()
        
        # Search for Organization resources with type=prov (Healthcare Provider)
        fhir_orgs = client.search("Organization", params={
            "type": "prov",
            "_count": 50
        })
        print(f"[FHIR] Found {len(fhir_orgs)} hospitals from EPIC FHIR", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"[ERROR] Exception in get_all_hospitals: {e}", flush=True)
        sys.stdout.flush()
        raise
    
    hospitals = []
    for fhir_org in fhir_orgs:
        try:
            hospital = fhir_organization_to_hospital(fhir_org)
            hospitals.append(hospital)
        except Exception as e:
            print(f"Error mapping FHIR Organization: {e}")
            continue
    
    return hospitals

def get_hospital(hospital_id: str) -> Optional[Dict]:
    """Get a specific hospital by ID from FHIR server"""
    client = get_fhir_client()
    fhir_org = client.read("Organization", hospital_id)
    
    if fhir_org:
        try:
            return fhir_organization_to_hospital(fhir_org)
        except Exception as e:
            print(f"Error mapping FHIR Organization: {e}")
            return None
    return None

def search_hospitals(city: Optional[str] = None, state: Optional[str] = None, specialty: Optional[str] = None) -> List[Dict]:
    """Search hospitals by location and specialty"""
    all_hospitals = get_all_hospitals()
    
    results = all_hospitals
    if city:
        results = [h for h in results if city.lower() in h.get("city", "").lower()]
    if state:
        results = [h for h in results if state.lower() in h.get("state", "").lower()]
    if specialty:
        results = [h for h in results if any(specialty.lower() in s.lower() for s in h.get("specialties", []))]
    
    return results

def get_medical_records(hospital_id: Optional[str] = None, patient_id: Optional[str] = None) -> List[Dict]:
    """Get medical records (Encounters) from FHIR server"""
    client = get_fhir_client()
    
    params = {"_count": 50}
    if patient_id:
        params["subject"] = f"Patient/{patient_id}"
    if hospital_id:
        params["service-provider"] = f"Organization/{hospital_id}"
    
    fhir_encounters = client.search("Encounter", params=params)
    
    records = []
    for fhir_encounter in fhir_encounters:
        try:
            record = fhir_encounter_to_record(fhir_encounter)
            records.append(record)
        except Exception as e:
            print(f"Error mapping FHIR Encounter: {e}")
            continue
    
    return records

# CRUD operations (create/update/delete) - delegate to FHIR client
def create_patient(patient_data: Dict) -> Dict:
    """Create a new patient in FHIR server"""
    # Convert our model to FHIR Patient resource
    # This is simplified - in production, use a proper FHIR resource builder
    client = get_fhir_client()
    # Implementation would convert patient_data to FHIR Patient format
    # For now, return the data (would need full FHIR resource creation)
    return patient_data

def update_patient(patient_id: str, patient_data: Dict) -> Optional[Dict]:
    """Update a patient in FHIR server"""
    client = get_fhir_client()
    # Implementation would update FHIR Patient resource
    return patient_data

def delete_patient(patient_id: str) -> bool:
    """Delete a patient from FHIR server"""
    client = get_fhir_client()
    return client.delete("Patient", patient_id)

def create_doctor(doctor_data: Dict) -> Dict:
    """Create a new doctor in FHIR server"""
    return doctor_data

def update_doctor(doctor_id: str, doctor_data: Dict) -> Optional[Dict]:
    """Update a doctor in FHIR server"""
    return doctor_data

def delete_doctor(doctor_id: str) -> bool:
    """Delete a doctor from FHIR server"""
    client = get_fhir_client()
    return client.delete("Practitioner", doctor_id)

def create_hospital(hospital_data: Dict) -> Dict:
    """Create a new hospital in FHIR server"""
    return hospital_data

def update_hospital(hospital_id: str, hospital_data: Dict) -> Optional[Dict]:
    """Update a hospital in FHIR server"""
    return hospital_data

def delete_hospital(hospital_id: str) -> bool:
    """Delete a hospital from FHIR server"""
    client = get_fhir_client()
    return client.delete("Organization", hospital_id)

def get_insurance_claims(hospital_id: Optional[str] = None) -> List[Dict]:
    """Get insurance claims (FHIR Claim resources) from FHIR server"""
    client = get_fhir_client()
    
    params = {"_count": 100}
    if hospital_id:
        params["provider"] = f"Organization/{hospital_id}"
    
    fhir_claims = client.search("Claim", params=params)
    
    claims = []
    for fhir_claim in fhir_claims:
        try:
            claim = fhir_claim_to_insurance_claim(fhir_claim)
            
            # If hospital_id filter was provided, verify it matches
            if hospital_id and claim.get("hospitalId") != hospital_id:
                continue
            
            # Try to get patient name if we have patient_id
            if claim.get("patientId"):
                try:
                    patient = get_patient(claim["patientId"])
                    if patient:
                        claim["patientName"] = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip() or "Unknown Patient"
                except:
                    pass
            
            # Try to get hospital name if we have hospital_id
            if claim.get("hospitalId"):
                try:
                    hospital = get_hospital(claim["hospitalId"])
                    if hospital:
                        claim["hospitalName"] = hospital.get("name", "Unknown Hospital")
                except:
                    pass
            
            claims.append(claim)
        except Exception as e:
            print(f"Error mapping FHIR Claim: {e}")
            continue
    
    return claims

def get_coverage_rules(hospital_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Get insurance coverage rules (FHIR Coverage resources) from FHIR server"""
    try:
        client = get_fhir_client()
        
        # Limit results to improve performance - reduce default to 10
        effective_limit = min(limit, 10)  # Cap at 10 to prevent timeouts
        params = {"_count": effective_limit, "_summary": "true"}  # Use summary for faster response
        
        fhir_coverages = client.search("Coverage", params=params)
        
        coverage_rules = []
        count = 0
        for fhir_coverage in fhir_coverages:
            if count >= effective_limit:
                break
            try:
                coverage_rule = fhir_coverage_to_coverage_rule(fhir_coverage)
                coverage_rules.append(coverage_rule)
                count += 1
            except Exception as e:
                print(f"Error mapping FHIR Coverage: {e}")
                continue
        
        return coverage_rules
    except Exception as e:
        print(f"Error fetching coverage rules from FHIR: {e}")
        # Return empty list on error instead of crashing
        return []

def get_medical_history(patient_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Get medical history (FHIR Condition resources) from FHIR server"""
    try:
        client = get_fhir_client()
        
        # Limit results to improve performance
        params = {"_count": min(limit, 20)}
        if patient_id:
            params["subject"] = f"Patient/{patient_id}"
        
        fhir_conditions = client.search("Condition", params=params)
        
        medical_history = []
        count = 0
        unique_patient_ids = set()
        
        for fhir_condition in fhir_conditions:
            if count >= limit:
                break
            try:
                history_item = fhir_condition_to_medical_history(fhir_condition)
                medical_history.append(history_item)
                
                # Collect unique patient IDs for batch name lookup
                if history_item.get("patientId"):
                    unique_patient_ids.add(history_item["patientId"])
                
                count += 1
            except Exception as e:
                print(f"Error mapping FHIR Condition: {e}")
                continue
        
        # Batch fetch patient names (with limit to prevent slow performance)
        # Limit to first 10 unique patients to avoid timeout
        patient_names_cache = {}
        patient_ids_list = list(unique_patient_ids)[:10]  # Limit to 10 patients max
        
        for pid in patient_ids_list:
            try:
                patient = get_patient(pid)
                if patient:
                    first_name = patient.get('first_name', '')
                    last_name = patient.get('last_name', '')
                    full_name = f"{first_name} {last_name}".strip()
                    if full_name:
                        patient_names_cache[pid] = full_name
            except Exception as e:
                print(f"Error fetching patient name for {pid}: {e}")
                continue
        
        # Enrich medical history with patient names
        for item in medical_history:
            pid = item.get("patientId")
            if pid and pid in patient_names_cache:
                item["patientName"] = patient_names_cache[pid]
            elif pid:
                # If name not fetched, set a placeholder
                item["patientName"] = None  # Will show as empty in UI
        
        return medical_history
    except Exception as e:
        print(f"Error fetching medical history from FHIR: {e}")
        return []

def get_patient_visits(patient_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """Get patient visits (FHIR Encounter resources) from FHIR server"""
    try:
        client = get_fhir_client()
        
        # Limit results to improve performance
        params = {"_count": min(limit, 20)}
        if patient_id:
            params["subject"] = f"Patient/{patient_id}"
        
        fhir_encounters = client.search("Encounter", params=params)
        
        visits = []
        count = 0
        unique_patient_ids = set()
        unique_hospital_ids = set()
        
        for fhir_encounter in fhir_encounters:
            if count >= limit:
                break
            try:
                visit = fhir_encounter_to_visit(fhir_encounter)
                visits.append(visit)
                
                # Collect unique IDs for batch name lookup
                if visit.get("patientId"):
                    unique_patient_ids.add(visit["patientId"])
                if visit.get("hospitalId"):
                    unique_hospital_ids.add(visit["hospitalId"])
                
                count += 1
            except Exception as e:
                print(f"Error mapping FHIR Encounter: {e}")
                continue
        
        # Batch fetch patient names (with timeout and limit to prevent slow performance)
        # Limit to first 10 unique patients to avoid timeout
        patient_names_cache = {}
        patient_ids_list = list(unique_patient_ids)[:10]  # Limit to 10 patients max
        
        for pid in patient_ids_list:
            try:
                patient = get_patient(pid)
                if patient:
                    first_name = patient.get('first_name', '')
                    last_name = patient.get('last_name', '')
                    full_name = f"{first_name} {last_name}".strip()
                    if full_name:
                        patient_names_cache[pid] = full_name
            except Exception as e:
                print(f"Error fetching patient name for {pid}: {e}")
                continue
        
        # Batch fetch hospital names (with timeout and limit)
        # Limit to first 10 unique hospitals to avoid timeout
        hospital_names_cache = {}
        hospital_ids_list = list(unique_hospital_ids)[:10]  # Limit to 10 hospitals max
        
        for hid in hospital_ids_list:
            try:
                hospital = get_hospital(hid)
                if hospital:
                    hospital_name = hospital.get('name', '')
                    if hospital_name:
                        hospital_names_cache[hid] = hospital_name
            except Exception as e:
                print(f"Error fetching hospital name for {hid}: {e}")
                continue
        
        # Enrich visits with patient and hospital names
        for visit in visits:
            pid = visit.get("patientId")
            if pid and pid in patient_names_cache:
                visit["patientName"] = patient_names_cache[pid]
            elif pid:
                # If name not fetched, set a placeholder
                visit["patientName"] = None  # Will show as empty in UI
            
            hid = visit.get("hospitalId")
            if hid and hid in hospital_names_cache:
                visit["hospitalName"] = hospital_names_cache[hid]
            elif hid:
                # If name not fetched, set a placeholder
                visit["hospitalName"] = None  # Will show as empty in UI
        
        return visits
    except Exception as e:
        print(f"Error fetching patient visits from FHIR: {e}")
        return []


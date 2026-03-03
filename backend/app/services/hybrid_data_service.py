"""
Hybrid Data Service - Combines real FHIR data with comprehensive mock data
This ensures we always have plenty of hospitals, doctors, and patients for demonstration
"""
from typing import List, Dict, Optional
from app.services.epic_fhir_data_service import EpicFHIRDataService
from app.services.real_data_service import (
    get_all_hospitals as get_mock_hospitals,
    get_all_doctors as get_mock_doctors,
    get_all_patients as get_mock_patients,
    get_all_bed_availability as get_mock_bed_availability
)

class HybridDataService:
    def __init__(self):
        self.fhir_service = EpicFHIRDataService()
        print("[HYBRID] Initializing hybrid data service (FHIR + Mock)")
    
    def get_all_hospitals(self) -> List[Dict]:
        """Get hospitals from FHIR + comprehensive mock data"""
        print("[HYBRID] Fetching hospitals from FHIR + Mock data")
        
        # Try to get real FHIR data first
        fhir_hospitals = []
        try:
            fhir_hospitals = self.fhir_service.get_all_hospitals()
            print(f"[HYBRID] Got {len(fhir_hospitals)} hospitals from FHIR")
        except Exception as e:
            print(f"[HYBRID] FHIR hospitals failed: {e}")
        
        # Get comprehensive mock data
        mock_hospitals = get_mock_hospitals()
        print(f"[HYBRID] Got {len(mock_hospitals)} mock hospitals")
        
        # Combine both datasets, prioritizing FHIR data but ensuring we have plenty
        all_hospitals = []
        
        # Add FHIR hospitals first
        for hospital in fhir_hospitals:
            hospital['data_source'] = 'FHIR'
            all_hospitals.append(hospital)
        
        # Add mock hospitals, but avoid duplicates by name
        existing_names = {h['name'].lower() for h in all_hospitals}
        for hospital in mock_hospitals:
            if hospital['name'].lower() not in existing_names:
                hospital['data_source'] = 'Mock'
                all_hospitals.append(hospital)
        
        print(f"[HYBRID] Total hospitals: {len(all_hospitals)} (FHIR: {len(fhir_hospitals)}, Mock: {len(all_hospitals) - len(fhir_hospitals)})")
        return all_hospitals
    
    def get_all_doctors(self) -> List[Dict]:
        """Get doctors from FHIR + comprehensive mock data"""
        print("[HYBRID] Fetching doctors from FHIR + Mock data")
        
        # Try to get real FHIR data first
        fhir_doctors = []
        try:
            fhir_doctors = self.fhir_service.get_all_doctors()
            print(f"[HYBRID] Got {len(fhir_doctors)} doctors from FHIR")
        except Exception as e:
            print(f"[HYBRID] FHIR doctors failed: {e}")
        
        # Get comprehensive mock data
        mock_doctors = get_mock_doctors()
        print(f"[HYBRID] Got {len(mock_doctors)} mock doctors")
        
        # Combine both datasets
        all_doctors = []
        
        # Add FHIR doctors first
        for doctor in fhir_doctors:
            doctor['data_source'] = 'FHIR'
            all_doctors.append(doctor)
        
        # Add mock doctors, avoiding duplicates by name
        existing_names = {f"{d.get('first_name', '')} {d.get('last_name', '')}".lower() for d in all_doctors}
        for doctor in mock_doctors:
            doctor_name = f"{doctor.get('first_name', '')} {doctor.get('last_name', '')}".lower()
            if doctor_name not in existing_names:
                doctor['data_source'] = 'Mock'
                all_doctors.append(doctor)
        
        print(f"[HYBRID] Total doctors: {len(all_doctors)} (FHIR: {len(fhir_doctors)}, Mock: {len(all_doctors) - len(fhir_doctors)})")
        return all_doctors
    
    def get_all_patients(self) -> List[Dict]:
        """Get patients from FHIR + comprehensive mock data"""
        print("[HYBRID] Fetching patients from FHIR + Mock data")
        
        # Try to get real FHIR data first
        fhir_patients = []
        try:
            fhir_patients = self.fhir_service.get_all_patients()
            print(f"[HYBRID] Got {len(fhir_patients)} patients from FHIR")
        except Exception as e:
            print(f"[HYBRID] FHIR patients failed: {e}")
        
        # Get comprehensive mock data
        mock_patients = get_mock_patients()
        print(f"[HYBRID] Got {len(mock_patients)} mock patients")
        
        # Combine both datasets
        all_patients = []
        
        # Add FHIR patients first
        for patient in fhir_patients:
            patient['data_source'] = 'FHIR'
            all_patients.append(patient)
        
        # Add mock patients, avoiding duplicates by name
        existing_names = {f"{p.get('first_name', '')} {p.get('last_name', '')}".lower() for p in all_patients}
        for patient in mock_patients:
            patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".lower()
            if patient_name not in existing_names:
                patient['data_source'] = 'Mock'
                all_patients.append(patient)
        
        print(f"[HYBRID] Total patients: {len(all_patients)} (FHIR: {len(fhir_patients)}, Mock: {len(all_patients) - len(fhir_patients)})")
        return all_patients
    
    def get_all_bed_availability(self) -> List[Dict]:
        """Get bed availability data"""
        return get_mock_bed_availability()

# Create global instance
hybrid_data_service = HybridDataService()
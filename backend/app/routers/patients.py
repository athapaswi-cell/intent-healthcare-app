from fastapi import APIRouter, HTTPException
from backend.app.services.data_service_router import get_all_patients, get_patient, create_patient, update_patient, delete_patient
from backend.app.models.patient import PatientCreate, PatientUpdate
from typing import List

router = APIRouter(prefix="/patients", tags=["patients"])

@router.get("/", response_model=List[dict])
def get_patients():
    """Get all patients"""
    return get_all_patients()

@router.get("/{patient_id}", response_model=dict)
def get_patient_by_id(patient_id: str):
    """Get a specific patient by ID"""
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@router.post("/", response_model=dict)
def create_new_patient(patient: PatientCreate):
    """Create a new patient"""
    patient_data = patient.dict()
    return create_patient(patient_data)

@router.put("/{patient_id}", response_model=dict)
def update_existing_patient(patient_id: str, patient: PatientUpdate):
    """Update a patient"""
    patient_data = {k: v for k, v in patient.dict().items() if v is not None}
    updated = update_patient(patient_id, patient_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    return updated

@router.delete("/{patient_id}")
def delete_existing_patient(patient_id: str):
    """Delete a patient"""
    success = delete_patient(patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return {"message": "Patient deleted successfully"}


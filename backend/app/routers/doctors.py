from fastapi import APIRouter, HTTPException, Query
from backend.app.services.data_service_router import (
    get_all_doctors, get_doctor, get_doctors_by_hospital, 
    get_doctors_by_specialization, create_doctor, update_doctor, delete_doctor
)
from backend.app.models.doctor import DoctorCreate, DoctorUpdate
from typing import List, Optional

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("/", response_model=List[dict])
def get_doctors(
    hospital_id: Optional[str] = Query(None, description="Filter by hospital ID"),
    specialization: Optional[str] = Query(None, description="Filter by specialization")
):
    """Get all doctors, optionally filtered by hospital or specialization"""
    if hospital_id:
        return get_doctors_by_hospital(hospital_id)
    if specialization:
        return get_doctors_by_specialization(specialization)
    return get_all_doctors()

@router.get("/{doctor_id}", response_model=dict)
def get_doctor_by_id(doctor_id: str):
    """Get a specific doctor by ID"""
    doctor = get_doctor(doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.post("/", response_model=dict)
def create_new_doctor(doctor: DoctorCreate):
    """Create a new doctor"""
    doctor_data = doctor.dict()
    return create_doctor(doctor_data)

@router.put("/{doctor_id}", response_model=dict)
def update_existing_doctor(doctor_id: str, doctor: DoctorUpdate):
    """Update a doctor"""
    doctor_data = {k: v for k, v in doctor.dict().items() if v is not None}
    updated = update_doctor(doctor_id, doctor_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return updated

@router.delete("/{doctor_id}")
def delete_existing_doctor(doctor_id: str):
    """Delete a doctor"""
    success = delete_doctor(doctor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return {"message": "Doctor deleted successfully"}


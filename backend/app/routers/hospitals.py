from fastapi import APIRouter, HTTPException, Query
from backend.app.services.data_service_router import (
    get_all_hospitals, get_hospital, search_hospitals,
    create_hospital, update_hospital, delete_hospital,
    get_bed_availability, get_all_bed_availability, update_bed_availability
)
from backend.app.models.hospital import HospitalCreate, HospitalUpdate
from typing import List, Optional

router = APIRouter(prefix="/hospitals", tags=["hospitals"])

@router.get("/", response_model=List[dict])
def get_hospitals(
    city: Optional[str] = Query(None, description="Filter by city"),
    state: Optional[str] = Query(None, description="Filter by state"),
    specialty: Optional[str] = Query(None, description="Filter by specialty")
):
    """Get all hospitals, optionally filtered by location or specialty"""
    return search_hospitals(city=city, state=state, specialty=specialty)

@router.get("/{hospital_id}", response_model=dict)
def get_hospital_by_id(hospital_id: str):
    """Get a specific hospital by ID"""
    hospital = get_hospital(hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.post("/", response_model=dict)
def create_new_hospital(hospital: HospitalCreate):
    """Create a new hospital"""
    hospital_data = hospital.dict()
    return create_hospital(hospital_data)

@router.put("/{hospital_id}", response_model=dict)
def update_existing_hospital(hospital_id: str, hospital: HospitalUpdate):
    """Update a hospital"""
    hospital_data = {k: v for k, v in hospital.dict().items() if v is not None}
    updated = update_hospital(hospital_id, hospital_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return updated

@router.delete("/{hospital_id}")
def delete_existing_hospital(hospital_id: str):
    """Delete a hospital"""
    success = delete_hospital(hospital_id)
    if not success:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return {"message": "Hospital deleted successfully"}

# Bed Availability Endpoints
@router.get("/{hospital_id}/beds", response_model=dict)
def get_hospital_bed_availability(hospital_id: str):
    """Get bed availability for a specific hospital"""
    bed_data = get_bed_availability(hospital_id)
    if not bed_data:
        raise HTTPException(status_code=404, detail="Hospital bed data not found")
    return bed_data

@router.get("/beds/all", response_model=List[dict])
def get_all_hospital_bed_data():
    """Get bed availability for all hospitals"""
    return get_all_bed_availability()

@router.put("/{hospital_id}/beds", response_model=dict)
def update_hospital_bed_availability(hospital_id: str, bed_data: dict):
    """Update bed availability for a hospital"""
    updated = update_bed_availability(hospital_id, bed_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return updated

@router.get("/beds/summary")
def get_bed_status_summary():
    """Get a summary of bed availability across all hospitals"""
    all_beds = get_all_bed_availability()
    
    total_hospitals = len(all_beds)
    total_beds = sum(bed["total_beds"] for bed in all_beds)
    total_available = sum(bed["available_beds"] for bed in all_beds)
    total_icu_beds = sum(bed["icu_beds"] for bed in all_beds)
    total_available_icu = sum(bed["available_icu"] for bed in all_beds)
    
    critical_hospitals = [bed for bed in all_beds if bed["status"] == "Critical"]
    high_occupancy_hospitals = [bed for bed in all_beds if bed["status"] == "High"]
    
    return {
        "summary": {
            "total_hospitals": total_hospitals,
            "total_beds": total_beds,
            "total_available": total_available,
            "total_occupied": total_beds - total_available,
            "overall_occupancy_rate": round(((total_beds - total_available) / total_beds) * 100, 1) if total_beds > 0 else 0,
            "total_icu_beds": total_icu_beds,
            "total_available_icu": total_available_icu,
            "icu_occupancy_rate": round(((total_icu_beds - total_available_icu) / total_icu_beds) * 100, 1) if total_icu_beds > 0 else 0
        },
        "alerts": {
            "critical_hospitals": len(critical_hospitals),
            "high_occupancy_hospitals": len(high_occupancy_hospitals),
            "critical_hospital_names": [h["hospital_name"] for h in critical_hospitals],
            "high_occupancy_hospital_names": [h["hospital_name"] for h in high_occupancy_hospitals]
        },
        "detailed_data": all_beds
    }


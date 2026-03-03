from fastapi import APIRouter, HTTPException, Query
from backend.app.services.real_data_service import get_bed_availability, get_all_bed_availability, update_bed_availability
from typing import List, Optional

router = APIRouter(prefix="/beds", tags=["bed-availability"])

@router.get("/", response_model=List[dict])
def get_all_bed_data():
    """Get bed availability for all hospitals"""
    return get_all_bed_availability()

@router.get("/{hospital_id}", response_model=dict)
def get_hospital_bed_availability(hospital_id: str):
    """Get bed availability for a specific hospital"""
    bed_data = get_bed_availability(hospital_id)
    if not bed_data:
        raise HTTPException(status_code=404, detail="Hospital bed data not found")
    return bed_data

@router.put("/{hospital_id}", response_model=dict)
def update_hospital_bed_availability(hospital_id: str, bed_data: dict):
    """Update bed availability for a hospital"""
    updated = update_bed_availability(hospital_id, bed_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return updated

@router.get("/status/summary")
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
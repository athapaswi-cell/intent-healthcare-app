from fastapi import APIRouter, HTTPException, Query
from backend.app.services.data_service_router import get_all_encounters, get_encounters_by_patient, get_encounters_by_hospital, get_medical_history
from typing import List, Optional

router = APIRouter(prefix="/records", tags=["records"])

@router.get("/", response_model=List[dict])
def get_records(
    hospital_id: Optional[str] = Query(None, description="Filter by hospital ID"),
    patient_id: Optional[str] = Query(None, description="Filter by patient ID")
):
    """
    Get medical records/encounters from FHIR server
    Returns real-time data from FHIR Encounter resources
    """
    try:
        if patient_id:
            records = get_encounters_by_patient(patient_id)
        elif hospital_id:
            records = get_encounters_by_hospital(hospital_id)
        else:
            records = get_all_encounters()
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching records: {str(e)}")

@router.get("/medical-history", response_model=List[dict])
def get_medical_history_endpoint(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    limit: Optional[int] = Query(50, description="Maximum number of records to return", ge=1, le=100)
):
    """
    Get medical history (conditions/diagnoses) from FHIR server
    Returns real-time data from FHIR Condition resources (limited to 50 by default for performance)
    """
    try:
        records = get_medical_history(patient_id=patient_id, limit=limit)
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching medical history: {str(e)}")

@router.get("/visits", response_model=List[dict])
def get_visits_endpoint(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    limit: Optional[int] = Query(100, description="Maximum number of visits to return", ge=1, le=500)
):
    """
    Get patient visits (encounters) from FHIR server
    Returns real-time data from FHIR Encounter resources (limited to 100 by default for performance)
    """
    try:
        if patient_id:
            records = get_encounters_by_patient(patient_id)
        else:
            records = get_all_encounters()
        return records[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching visits: {str(e)}")


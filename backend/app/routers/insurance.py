from fastapi import APIRouter, HTTPException, Query
from backend.app.services.data_service_router import get_insurance_claims, get_coverage_rules
from typing import List, Optional

router = APIRouter(prefix="/insurance", tags=["insurance"])

@router.get("/policies", response_model=List[dict])
def get_policies(
    hospital_id: Optional[str] = Query(None, description="Filter by hospital ID"),
    limit: Optional[int] = Query(50, description="Maximum number of policies to return", ge=1, le=100)
):
    """Get all insurance policies (Coverage resources) from FHIR server, optionally filtered by hospital"""
    try:
        return get_coverage_rules(hospital_id=hospital_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policies: {str(e)}")

@router.get("/claims", response_model=List[dict])
def get_claims(
    hospital_id: Optional[str] = Query(None, description="Filter by hospital ID")
):
    """Get all insurance claims from FHIR server, optionally filtered by hospital"""
    return get_insurance_claims(hospital_id=hospital_id)

@router.get("/coverage-rules", response_model=List[dict])
def get_coverage_rules_endpoint(
    limit: Optional[int] = Query(20, description="Maximum number of coverage rules to return", ge=1, le=50)
):
    """Get insurance coverage rules from FHIR server (limited to 20 by default for performance)"""
    try:
        return get_coverage_rules(limit=limit)
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Error fetching coverage rules: {str(e)}")


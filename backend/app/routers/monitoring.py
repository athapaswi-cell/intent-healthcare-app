"""
Patient Monitoring Router - Epic FHIR patient vitals/labs monitoring
"""
from fastapi import APIRouter, HTTPException
from backend.app.services.epic_fhir_observation_client import EpicFHIRObservationClient
from backend.app.services.fhir_extract import extract_metrics_from_bundle
from backend.app.services.patient_classifier import classify
from backend.app.services.alert_service import alert_slack

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

fhir_client = EpicFHIRObservationClient()

@router.get("/monitor/{patient_id}")
def monitor_patient(patient_id: str):
    """
    Pull latest lab/vitals from Epic FHIR and classify into Healthy/Average/Poor.
    
    This endpoint:
    1. Fetches patient data from Epic FHIR
    2. Retrieves vital signs and laboratory observations
    3. Extracts key metrics (HbA1c, LDL, Systolic BP, SpO2, Heart Rate)
    4. Classifies patient into Healthy/Average/Poor category
    5. Sends Slack alert if patient is in Poor category
    """
    try:
        patient = fhir_client.get_patient(patient_id)
        vitals_bundle = fhir_client.get_observations(patient_id, category="vital-signs")
        labs_bundle = fhir_client.get_observations(patient_id, category="laboratory")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"FHIR fetch failed: {str(e)}")

    vitals = extract_metrics_from_bundle(vitals_bundle)
    labs = extract_metrics_from_bundle(labs_bundle)

    metrics = {**vitals, **labs}
    result = classify(metrics)

    # Alert if Poor
    if result.get("category") == "Poor":
        name = patient.get("name", [{}])[0]
        display_name = " ".join(name.get("given", []) + [name.get("family", "")]).strip()

        msg = (
            f"🚨 EPIC FHIR ALERT: POOR CATEGORY\n"
            f"patient_id={patient_id}\n"
            f"name={display_name}\n"
            f"score={result.get('score')}\n"
            f"details={result.get('details')}"
        )
        try:
            alert_slack(msg)
        except Exception:
            # best effort alerting
            pass

    return {
        "patient_id": patient_id,
        "patient": patient,
        "metrics": metrics,
        "classification": result
    }

@router.get("/health")
def health_check():
    """Health check endpoint for monitoring service"""
    return {"status": "ok", "service": "patient_monitoring"}


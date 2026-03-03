
FHIR_DB = []

def persist(resource_type, payload):
    """
    Persist FHIR resources to the database
    In production, this would connect to a real FHIR server
    """
    resource = {
        "id": payload.get("encounter_id") or payload.get("appointment_id") or payload.get("prescription_id") or str(len(FHIR_DB)),
        "resourceType": resource_type,
        "data": payload,
        "timestamp": payload.get("timestamp") or payload.get("created_at") or payload.get("requested_at")
    }
    FHIR_DB.append(resource)
    return resource

def get_resources(resource_type=None, patient_id=None):
    """
    Retrieve FHIR resources from the database
    """
    results = FHIR_DB
    if resource_type:
        results = [r for r in results if r["resourceType"] == resource_type]
    if patient_id:
        results = [r for r in results if r["data"].get("patient_id") == patient_id]
    return results

def get_patient_records(patient_id):
    """
    Get all records for a specific patient
    """
    return get_resources(patient_id=patient_id)

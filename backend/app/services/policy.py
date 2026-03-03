
def enforce(intent, actor):
    """
    Policy enforcement engine - ensures actors can only perform authorized actions
    """
    # Define allowed intents per actor type
    patient_allowed = [
        "PATIENT_EMERGENCY_HELP",
        "PATIENT_SYMPTOM_REPORT",
        "SCHEDULE_APPOINTMENT",
        "CANCEL_APPOINTMENT",
        "RESCHEDULE_APPOINTMENT",
        "REQUEST_PRESCRIPTION_REFILL",
        "VIEW_PRESCRIPTIONS",
        "VIEW_LAB_RESULTS",
        "REQUEST_TELEHEALTH_CONSULTATION",
        "VIEW_MEDICAL_RECORDS",
        "HEALTH_QUERY"
    ]
    
    clinician_allowed = [
        "CLINICAL_PRESCRIPTION_REQUEST",
        "CLINICAL_DIAGNOSIS",
        "CLINICAL_ORDER_LAB",
        "CLINICAL_VIEW_PATIENT_RECORDS",
        "CLINICAL_UPDATE_RECORDS"
    ]
    
    admin_allowed = [
        "ADMIN_MANAGE_USERS",
        "ADMIN_VIEW_ANALYTICS",
        "ADMIN_SYSTEM_CONFIG"
    ]
    
    # Check permissions
    if actor == "PATIENT":
        if intent not in patient_allowed:
            raise Exception(f"Policy violation: Patient cannot perform {intent}")
    elif actor == "CLINICIAN" or actor == "DOCTOR":
        if intent not in clinician_allowed and intent not in patient_allowed:
            raise Exception(f"Policy violation: Clinician cannot perform {intent}")
    elif actor == "ADMIN":
        if intent not in admin_allowed and intent not in clinician_allowed:
            raise Exception(f"Policy violation: Admin cannot perform {intent}")
    else:
        raise Exception(f"Unknown actor type: {actor}")

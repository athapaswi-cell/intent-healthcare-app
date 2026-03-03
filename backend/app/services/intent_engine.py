
from backend.app.services.policy import enforce
from backend.app.services.fhir import persist
from backend.app.services.ai import triage
from datetime import datetime, timedelta
import uuid

def execute(payload):
    intent = payload["intent"]["name"]
    actor = payload["actor"]["type"]

    enforce(intent, actor)

    # Emergency & Urgent Care Intents
    if intent == "PATIENT_EMERGENCY_HELP":
        encounter_id = str(uuid.uuid4())
        persist("Encounter", {
            **payload,
            "encounter_id": encounter_id,
            "type": "emergency",
            "timestamp": datetime.now().isoformat()
        })
        return {
            "status": "EMERGENCY_TRIGGERED",
            "encounter_id": encounter_id,
            "message": "Emergency response team has been notified",
            "estimated_response_time": "5-10 minutes"
        }

    if intent == "PATIENT_SYMPTOM_REPORT":
        risk = triage(payload["payload"]["symptoms"])
        observation_id = str(uuid.uuid4())
        persist("Observation", {
            **payload,
            "observation_id": observation_id,
            "risk_score": risk["risk_score"],
            "timestamp": datetime.now().isoformat()
        })
        return {
            "status": "RECEIVED",
            "observation_id": observation_id,
            "risk": risk,
            "recommendation": get_recommendation(risk["risk_score"])
        }

    # Appointment Intents
    if intent == "SCHEDULE_APPOINTMENT":
        appointment_id = str(uuid.uuid4())
        appointment_date = payload["payload"].get("preferred_date", 
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"))
        persist("Appointment", {
            **payload,
            "appointment_id": appointment_id,
            "status": "scheduled",
            "appointment_date": appointment_date,
            "created_at": datetime.now().isoformat()
        })
        return {
            "status": "APPOINTMENT_SCHEDULED",
            "appointment_id": appointment_id,
            "appointment_date": appointment_date,
            "message": f"Appointment scheduled for {appointment_date}"
        }

    if intent == "CANCEL_APPOINTMENT":
        persist("Appointment", {
            **payload,
            "status": "cancelled",
            "cancelled_at": datetime.now().isoformat()
        })
        return {
            "status": "APPOINTMENT_CANCELLED",
            "message": "Appointment has been cancelled successfully"
        }

    if intent == "RESCHEDULE_APPOINTMENT":
        persist("Appointment", {
            **payload,
            "status": "rescheduled",
            "rescheduled_at": datetime.now().isoformat()
        })
        return {
            "status": "APPOINTMENT_RESCHEDULED",
            "new_date": payload["payload"].get("new_date"),
            "message": "Appointment has been rescheduled"
        }

    # Prescription Intents
    if intent == "REQUEST_PRESCRIPTION_REFILL":
        prescription_id = str(uuid.uuid4())
        persist("MedicationRequest", {
            **payload,
            "prescription_id": prescription_id,
            "type": "refill",
            "status": "pending",
            "requested_at": datetime.now().isoformat()
        })
        return {
            "status": "REFILL_REQUESTED",
            "prescription_id": prescription_id,
            "message": "Prescription refill request submitted. Doctor will review within 24 hours."
        }

    if intent == "VIEW_PRESCRIPTIONS":
        # In a real app, this would query the database
        return {
            "status": "SUCCESS",
            "prescriptions": [],
            "message": "No active prescriptions found"
        }

    # Lab Results Intent
    if intent == "VIEW_LAB_RESULTS":
        return {
            "status": "SUCCESS",
            "lab_results": [],
            "message": "No recent lab results available"
        }

    # Consultation Intent
    if intent == "REQUEST_TELEHEALTH_CONSULTATION":
        consultation_id = str(uuid.uuid4())
        persist("Encounter", {
            **payload,
            "encounter_id": consultation_id,
            "type": "telehealth",
            "status": "scheduled",
            "created_at": datetime.now().isoformat()
        })
        return {
            "status": "CONSULTATION_SCHEDULED",
            "consultation_id": consultation_id,
            "message": "Telehealth consultation request received. You will be contacted shortly."
        }

    # Medical Records Intent
    if intent == "VIEW_MEDICAL_RECORDS":
        return {
            "status": "SUCCESS",
            "records": [],
            "message": "Medical records retrieved"
        }

    # General Health Query
    if intent == "HEALTH_QUERY":
        query = payload["payload"].get("query", "")
        return {
            "status": "SUCCESS",
            "response": f"Processing your health query: {query}",
            "suggestions": ["Schedule appointment", "View lab results", "Contact doctor"]
        }

    return {"status": "OK", "message": "Intent processed"}

def get_recommendation(risk_score):
    if risk_score >= 80:
        return "Seek immediate medical attention or call emergency services"
    elif risk_score >= 50:
        return "Schedule an appointment with your doctor within 24 hours"
    elif risk_score >= 30:
        return "Monitor symptoms and consider scheduling a routine appointment"
    else:
        return "Continue monitoring. Contact doctor if symptoms worsen"

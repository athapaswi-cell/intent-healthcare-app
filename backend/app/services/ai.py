
def triage(symptoms):
    """
    AI-powered triage system that analyzes symptoms and provides risk assessment
    """
    if not symptoms or len(symptoms) == 0:
        return {
            "risk_score": 0,
            "severity": "low",
            "explanation": "No symptoms reported"
        }
    
    # High-risk symptom keywords
    high_risk_keywords = ["chest pain", "difficulty breathing", "severe pain", 
                          "unconscious", "severe bleeding", "heart attack", 
                          "stroke", "seizure", "severe allergic reaction"]
    
    # Medium-risk symptom keywords
    medium_risk_keywords = ["fever", "persistent cough", "headache", 
                           "nausea", "dizziness", "fatigue", "pain"]
    
    symptoms_lower = [s.lower() for s in symptoms]
    
    # Calculate risk score
    risk_score = 0
    severity = "low"
    
    # Check for high-risk symptoms
    high_risk_count = sum(1 for keyword in high_risk_keywords 
                         if any(keyword in symptom for symptom in symptoms_lower))
    if high_risk_count > 0:
        risk_score = min(90 + (high_risk_count * 5), 100)
        severity = "high"
    # Check for medium-risk symptoms
    elif any(keyword in symptom for keyword in medium_risk_keywords 
             for symptom in symptoms_lower):
        risk_score = min(40 + (len(symptoms) * 10), 80)
        severity = "medium"
    else:
        risk_score = min(len(symptoms) * 15, 40)
        severity = "low"
    
    return {
        "risk_score": risk_score,
        "severity": severity,
        "explanation": f"Analyzed {len(symptoms)} symptom(s). Risk assessment: {severity}",
        "symptom_count": len(symptoms),
        "recommended_action": get_recommended_action(severity)
    }

def get_recommended_action(severity):
    actions = {
        "high": "Seek immediate emergency care",
        "medium": "Schedule urgent appointment or visit urgent care",
        "low": "Monitor symptoms and schedule routine appointment if needed"
    }
    return actions.get(severity, "Monitor symptoms")

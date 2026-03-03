"""
Medication Recommendation Service
Provides medication recommendations based on diagnosis
"""
from typing import List, Dict

# Diagnosis to Medication Mapping
# In production, this would come from a medical database or API
DIAGNOSIS_MEDICATIONS = {
    "hypertension": [
        {
            "name": "Lisinopril",
            "dosage": "10mg",
            "frequency": "Once daily",
            "duration": "Ongoing",
            "instructions": "Take with or without food",
            "quantity": "30 tablets",
            "category": "ACE Inhibitor"
        },
        {
            "name": "Amlodipine",
            "dosage": "5mg",
            "frequency": "Once daily",
            "duration": "Ongoing",
            "instructions": "Take with or without food",
            "quantity": "30 tablets",
            "category": "Calcium Channel Blocker"
        }
    ],
    "diabetes": [
        {
            "name": "Metformin",
            "dosage": "500mg",
            "frequency": "Twice daily",
            "duration": "Ongoing",
            "instructions": "Take with meals",
            "quantity": "60 tablets",
            "category": "Biguanide"
        },
        {
            "name": "Glipizide",
            "dosage": "5mg",
            "frequency": "Once daily before breakfast",
            "duration": "Ongoing",
            "instructions": "Take 30 minutes before meals",
            "quantity": "30 tablets",
            "category": "Sulfonylurea"
        }
    ],
    "infection": [
        {
            "name": "Amoxicillin",
            "dosage": "500mg",
            "frequency": "Three times daily",
            "duration": "7-10 days",
            "instructions": "Take with or without food",
            "quantity": "21-30 capsules",
            "category": "Antibiotic"
        },
        {
            "name": "Azithromycin",
            "dosage": "500mg",
            "frequency": "Once daily",
            "duration": "5 days",
            "instructions": "Take on empty stomach",
            "quantity": "5 tablets",
            "category": "Antibiotic"
        }
    ],
    "pain": [
        {
            "name": "Ibuprofen",
            "dosage": "400mg",
            "frequency": "Every 6-8 hours as needed",
            "duration": "As needed",
            "instructions": "Take with food or milk",
            "quantity": "30 tablets",
            "category": "NSAID"
        },
        {
            "name": "Acetaminophen",
            "dosage": "500mg",
            "frequency": "Every 4-6 hours as needed",
            "duration": "As needed",
            "instructions": "Take with or without food",
            "quantity": "50 tablets",
            "category": "Analgesic"
        }
    ],
    "asthma": [
        {
            "name": "Albuterol",
            "dosage": "90mcg",
            "frequency": "2 puffs every 4-6 hours as needed",
            "duration": "As needed",
            "instructions": "Inhaler - shake before use",
            "quantity": "1 inhaler",
            "category": "Bronchodilator"
        },
        {
            "name": "Montelukast",
            "dosage": "10mg",
            "frequency": "Once daily at bedtime",
            "duration": "Ongoing",
            "instructions": "Take with or without food",
            "quantity": "30 tablets",
            "category": "Leukotriene Receptor Antagonist"
        }
    ],
    "high cholesterol": [
        {
            "name": "Atorvastatin",
            "dosage": "20mg",
            "frequency": "Once daily",
            "duration": "Ongoing",
            "instructions": "Take at bedtime",
            "quantity": "30 tablets",
            "category": "Statin"
        },
        {
            "name": "Simvastatin",
            "dosage": "20mg",
            "frequency": "Once daily",
            "duration": "Ongoing",
            "instructions": "Take at bedtime",
            "quantity": "30 tablets",
            "category": "Statin"
        }
    ],
    "depression": [
        {
            "name": "Sertraline",
            "dosage": "50mg",
            "frequency": "Once daily",
            "duration": "Ongoing",
            "instructions": "Take with or without food",
            "quantity": "30 tablets",
            "category": "SSRI"
        },
        {
            "name": "Fluoxetine",
            "dosage": "20mg",
            "frequency": "Once daily",
            "duration": "Ongoing",
            "instructions": "Take in the morning",
            "quantity": "30 capsules",
            "category": "SSRI"
        }
    ],
    "acid reflux": [
        {
            "name": "Omeprazole",
            "dosage": "20mg",
            "frequency": "Once daily before breakfast",
            "duration": "4-8 weeks",
            "instructions": "Take 30 minutes before first meal",
            "quantity": "30 capsules",
            "category": "Proton Pump Inhibitor"
        },
        {
            "name": "Pantoprazole",
            "dosage": "40mg",
            "frequency": "Once daily",
            "duration": "4-8 weeks",
            "instructions": "Take before meals",
            "quantity": "30 tablets",
            "category": "Proton Pump Inhibitor"
        }
    ],
    "anxiety": [
        {
            "name": "Alprazolam",
            "dosage": "0.5mg",
            "frequency": "Three times daily as needed",
            "duration": "Short-term",
            "instructions": "Take as directed by doctor",
            "quantity": "30 tablets",
            "category": "Benzodiazepine"
        },
        {
            "name": "Lorazepam",
            "dosage": "1mg",
            "frequency": "Two to three times daily as needed",
            "duration": "Short-term",
            "instructions": "Take as directed",
            "quantity": "30 tablets",
            "category": "Benzodiazepine"
        }
    ],
    "allergy": [
        {
            "name": "Cetirizine",
            "dosage": "10mg",
            "frequency": "Once daily",
            "duration": "As needed",
            "instructions": "Take with or without food",
            "quantity": "30 tablets",
            "category": "Antihistamine"
        },
        {
            "name": "Loratadine",
            "dosage": "10mg",
            "frequency": "Once daily",
            "duration": "As needed",
            "instructions": "Take with or without food",
            "quantity": "30 tablets",
            "category": "Antihistamine"
        }
    ]
}

def get_medications_for_diagnosis(diagnosis: str) -> List[Dict]:
    """
    Get recommended medications based on diagnosis
    
    Args:
        diagnosis: The medical diagnosis/condition
        
    Returns:
        List of recommended medications with dosages and instructions
    """
    diagnosis_lower = diagnosis.lower().strip()
    
    # Direct match
    if diagnosis_lower in DIAGNOSIS_MEDICATIONS:
        return DIAGNOSIS_MEDICATIONS[diagnosis_lower]
    
    # Partial match - check if diagnosis contains any key
    for key, medications in DIAGNOSIS_MEDICATIONS.items():
        if key in diagnosis_lower or diagnosis_lower in key:
            return medications
    
    # Common variations
    diagnosis_mappings = {
        "high blood pressure": "hypertension",
        "blood pressure": "hypertension",
        "bp": "hypertension",
        "type 2 diabetes": "diabetes",
        "diabetes mellitus": "diabetes",
        "bacterial infection": "infection",
        "viral infection": "infection",
        "uti": "infection",
        "urinary tract infection": "infection",
        "headache": "pain",
        "back pain": "pain",
        "joint pain": "pain",
        "arthritis": "pain",
        "copd": "asthma",
        "chronic obstructive pulmonary disease": "asthma",
        "hyperlipidemia": "high cholesterol",
        "cholesterol": "high cholesterol",
        "gerd": "acid reflux",
        "gastroesophageal reflux": "acid reflux",
        "heartburn": "acid reflux",
        "panic disorder": "anxiety",
        "seasonal allergies": "allergy",
        "hay fever": "allergy"
    }
    
    # Check mappings
    for key, mapped_diagnosis in diagnosis_mappings.items():
        if key in diagnosis_lower:
            return DIAGNOSIS_MEDICATIONS.get(mapped_diagnosis, [])
    
    # If no match found, return general recommendations
    return [
        {
            "name": "Consult with Doctor",
            "dosage": "N/A",
            "frequency": "N/A",
            "duration": "N/A",
            "instructions": f"Please consult with a healthcare provider for diagnosis: {diagnosis}. This system cannot provide medication recommendations for this condition.",
            "quantity": "N/A",
            "category": "General"
        }
    ]



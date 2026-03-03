"""
FHIR Resource Mapper - Converts FHIR resources to our application models
"""
from typing import Dict, List, Optional
from datetime import datetime

def fhir_patient_to_model(fhir_patient: Dict) -> Dict:
    """Convert FHIR Patient resource to our Patient model"""
    name = fhir_patient.get("name", [{}])[0] if fhir_patient.get("name") else {}
    given_names = name.get("given", [])
    family_name = name.get("family", "")
    
    # Extract email and phone from contact points
    email = None
    phone = None
    for telecom in fhir_patient.get("telecom", []):
        system = telecom.get("system", "")
        value = telecom.get("value", "")
        if system == "email":
            email = value
        elif system == "phone":
            phone = value
    
    # Extract address
    address = None
    if fhir_patient.get("address"):
        addr = fhir_patient["address"][0]
        line = ", ".join(addr.get("line", []))
        city = addr.get("city", "")
        state = addr.get("state", "")
        postal = addr.get("postalCode", "")
        address = f"{line}, {city}, {state} {postal}".strip()
    
    # Extract emergency contact
    emergency_contact_name = None
    emergency_contact_phone = None
    for contact in fhir_patient.get("contact", []):
        relationship = contact.get("relationship", [{}])[0]
        if relationship.get("coding", [{}])[0].get("code") == "C":
            emergency_contact_name = contact.get("name", {}).get("text", "")
            for telecom in contact.get("telecom", []):
                if telecom.get("system") == "phone":
                    emergency_contact_phone = telecom.get("value")
                    break
    
    return {
        "id": fhir_patient.get("id"),
        "first_name": " ".join(given_names) if given_names else "Unknown",
        "last_name": family_name or "Unknown",
        "date_of_birth": fhir_patient.get("birthDate", ""),
        "gender": fhir_patient.get("gender", "unknown").upper(),
        "email": email,
        "phone": phone,
        "address": address,
        "emergency_contact_name": emergency_contact_name,
        "emergency_contact_phone": emergency_contact_phone,
        "blood_type": None,  # Not typically in FHIR Patient
        "allergies": [],  # Would come from AllergyIntolerance resources
        "medical_history": [],  # Would come from Condition resources
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def fhir_practitioner_to_doctor(fhir_practitioner: Dict) -> Dict:
    """Convert FHIR Practitioner resource to our Doctor model"""
    name = fhir_practitioner.get("name", [{}])[0] if fhir_practitioner.get("name") else {}
    given_names = name.get("given", [])
    family_name = name.get("family", "")
    
    # Extract email and phone
    email = None
    phone = None
    for telecom in fhir_practitioner.get("telecom", []):
        system = telecom.get("system", "")
        value = telecom.get("value", "")
        if system == "email":
            email = value
        elif system == "phone":
            phone = value
    
    # Extract qualification/specialization
    qualification_text = ""
    specialization = "General Practice"
    if fhir_practitioner.get("qualification"):
        qual = fhir_practitioner["qualification"][0]
        qualification_text = qual.get("code", {}).get("text", "")
        for coding in qual.get("code", {}).get("coding", []):
            if coding.get("system") == "http://snomed.info/sct":
                specialization = coding.get("display", specialization)
    
    # Extract identifier (license number)
    license_number = ""
    for identifier in fhir_practitioner.get("identifier", []):
        if identifier.get("type", {}).get("coding", [{}])[0].get("code") == "LN":
            license_number = identifier.get("value", "")
    
    return {
        "id": fhir_practitioner.get("id"),
        "first_name": " ".join(given_names) if given_names else "Unknown",
        "last_name": family_name or "Unknown",
        "specialization": specialization,
        "qualification": qualification_text or "MD",
        "license_number": license_number or f"MD-{fhir_practitioner.get('id', 'N/A')}",
        "email": email,
        "phone": phone,
        "hospital_id": None,  # Would come from PractitionerRole
        "department": None,
        "experience_years": None,
        "languages": [],
        "consultation_fee": None,
        "availability": "Available",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def fhir_organization_to_hospital(fhir_org: Dict) -> Dict:
    """Convert FHIR Organization resource to our Hospital model"""
    name = fhir_org.get("name", "Unknown Hospital")
    
    # Extract address
    address = ""
    city = ""
    state = ""
    zip_code = ""
    if fhir_org.get("address"):
        addr = fhir_org["address"][0]
        address = ", ".join(addr.get("line", []))
        city = addr.get("city", "")
        state = addr.get("state", "")
        zip_code = addr.get("postalCode", "")
    
    # Extract phone and email
    phone = None
    email = None
    emergency_phone = None
    for telecom in fhir_org.get("telecom", []):
        system = telecom.get("system", "")
        value = telecom.get("value", "")
        use = telecom.get("use", "")
        if system == "phone":
            if use == "work":
                phone = value
            elif use == "mobile" or use == "temp":
                emergency_phone = value
        elif system == "email":
            email = value
    
    # Extract type (hospital type)
    hospital_type = "General"
    for type_coding in fhir_org.get("type", []):
        for coding in type_coding.get("coding", []):
            if "hospital" in coding.get("display", "").lower():
                hospital_type = coding.get("display", hospital_type)
    
    # Extract specialties from extension or type
    specialties = []
    for type_coding in fhir_org.get("type", []):
        for coding in type_coding.get("coding", []):
            display = coding.get("display", "")
            if display and display not in specialties:
                specialties.append(display)
    
    return {
        "id": fhir_org.get("id"),
        "name": name,
        "address": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": "USA",
        "phone": phone,
        "email": email,
        "emergency_phone": emergency_phone,
        "hospital_type": hospital_type,
        "total_beds": None,  # Not in standard FHIR Organization
        "icu_beds": None,
        "specialties": specialties[:10],  # Limit to 10
        "facilities": [],  # Would come from Location resources
        "operating_hours": None,
        "website": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

def fhir_encounter_to_record(fhir_encounter: Dict) -> Dict:
    """Convert FHIR Encounter resource to our Medical Record model"""
    return {
        "id": fhir_encounter.get("id"),
        "patient_id": fhir_encounter.get("subject", {}).get("reference", "").replace("Patient/", ""),
        "patient_name": None,  # Would need to fetch Patient resource
        "encounter_type": fhir_encounter.get("class", {}).get("display", "Unknown"),
        "status": fhir_encounter.get("status", "unknown"),
        "timestamp": fhir_encounter.get("period", {}).get("start", datetime.now().isoformat()),
        "hospital_id": fhir_encounter.get("serviceProvider", {}).get("reference", "").replace("Organization/", "")
    }

def fhir_encounter_to_visit(fhir_encounter: Dict) -> Dict:
    """Convert FHIR Encounter resource to our Visit model"""
    encounter_id = fhir_encounter.get("id", "")
    
    # Extract patient reference
    subject_ref = fhir_encounter.get("subject", {}).get("reference", "")
    patient_id = subject_ref.replace("Patient/", "").split("?")[0] if subject_ref else None
    
    # Extract encounter type/class
    encounter_class = fhir_encounter.get("class", {})
    encounter_type = encounter_class.get("display", encounter_class.get("code", "Unknown"))
    encounter_code = encounter_class.get("code", None)
    
    # Extract status
    status = fhir_encounter.get("status", "unknown").title()
    
    # Extract period (visit dates)
    period = fhir_encounter.get("period", {})
    start_date = period.get("start", datetime.now().isoformat())
    end_date = period.get("end", None)
    duration_minutes = None
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
            duration_minutes = int((end - start).total_seconds() / 60)
        except:
            pass
    
    # Extract service provider (hospital)
    service_provider_ref = fhir_encounter.get("serviceProvider", {}).get("reference", "")
    hospital_id = service_provider_ref.replace("Organization/", "").split("?")[0] if service_provider_ref else None
    
    # Extract location
    location_name = None
    locations = fhir_encounter.get("location", [])
    if locations:
        location_obj = locations[0] if isinstance(locations[0], dict) else {}
        location_ref = location_obj.get("location", {}).get("reference", "")
        if location_ref:
            location_name = location_ref.replace("Location/", "").split("?")[0]
    
    # Extract reason (chief complaint)
    reason_text = None
    reason_coding = fhir_encounter.get("reasonCode", [{}])[0].get("coding", [])
    if reason_coding:
        reason_text = reason_coding[0].get("display", reason_coding[0].get("code", None))
    
    # Extract diagnosis
    diagnoses = []
    for diagnosis in fhir_encounter.get("diagnosis", []):
        condition_ref = diagnosis.get("condition", {}).get("reference", "")
        if condition_ref:
            diagnoses.append(condition_ref.replace("Condition/", "").split("?")[0])
    
    # Extract participants (doctors/staff)
    participants = []
    for participant in fhir_encounter.get("participant", []):
        participant_type = participant.get("type", [{}])[0].get("coding", [{}])[0].get("code", "")
        participant_ref = participant.get("individual", {}).get("reference", "")
        if participant_ref:
            participants.append({
                "type": participant_type,
                "reference": participant_ref.replace("Practitioner/", "").split("?")[0]
            })
    
    return {
        "id": encounter_id,
        "patientId": patient_id or "",
        "patientName": None,  # Will be enriched by service
        "encounterType": encounter_type,
        "encounterCode": encounter_code,
        "status": status,
        "startDate": start_date.split("T")[0] if "T" in start_date else start_date,
        "startTime": start_date.split("T")[1].split(".")[0] if "T" in start_date and len(start_date.split("T")) > 1 else None,
        "endDate": end_date.split("T")[0] if end_date and "T" in end_date else (end_date or None),
        "endTime": end_date.split("T")[1].split(".")[0] if end_date and "T" in end_date and len(end_date.split("T")) > 1 else None,
        "durationMinutes": duration_minutes,
        "hospitalId": hospital_id or "",
        "hospitalName": None,  # Will be enriched by service
        "location": location_name,
        "reason": reason_text,
        "diagnoses": diagnoses,
        "participants": participants
    }

def fhir_condition_to_medical_history(fhir_condition: Dict) -> Dict:
    """Convert FHIR Condition resource to our Medical History model"""
    condition_id = fhir_condition.get("id", "")
    
    # Extract patient reference
    subject_ref = fhir_condition.get("subject", {}).get("reference", "")
    patient_id = subject_ref.replace("Patient/", "").split("?")[0] if subject_ref else None
    
    # Extract condition/diagnosis
    condition_text = "Unknown Condition"
    condition_code = None
    coding_list = fhir_condition.get("code", {}).get("coding", [])
    if coding_list:
        condition_text = coding_list[0].get("display", coding_list[0].get("code", condition_text))
        condition_code = coding_list[0].get("code", None)
    
    # Extract category
    category = "Diagnosis"
    category_coding = fhir_condition.get("category", [{}])[0].get("coding", [])
    if category_coding:
        category = category_coding[0].get("display", category_coding[0].get("code", category))
    
    # Extract severity
    severity = None
    severity_coding = fhir_condition.get("severity", {}).get("coding", [])
    if severity_coding:
        severity = severity_coding[0].get("display", severity_coding[0].get("code", None))
    
    # Extract clinical status
    clinical_status = fhir_condition.get("clinicalStatus", {}).get("coding", [{}])[0].get("code", "active")
    
    # Extract verification status
    verification_status = fhir_condition.get("verificationStatus", {}).get("coding", [{}])[0].get("code", "confirmed")
    
    # Extract onset date
    onset_date = None
    onset_datetime = fhir_condition.get("onsetDateTime")
    if onset_datetime:
        onset_date = onset_datetime
    elif fhir_condition.get("onsetPeriod"):
        onset_date = fhir_condition["onsetPeriod"].get("start", None)
    elif fhir_condition.get("onsetAge"):
        # Calculate approximate date from age
        onset_date = datetime.now().isoformat()
    
    # Extract abatement date (when condition resolved)
    abatement_date = None
    abatement_datetime = fhir_condition.get("abatementDateTime")
    if abatement_datetime:
        abatement_date = abatement_datetime
    elif fhir_condition.get("abatementPeriod"):
        abatement_date = fhir_condition["abatementPeriod"].get("end", None)
    
    # Extract encounter reference (related visit)
    encounter_id = None
    encounter_refs = fhir_condition.get("encounter", [])
    if encounter_refs:
        encounter_ref = encounter_refs[0] if isinstance(encounter_refs[0], str) else encounter_refs[0].get("reference", "")
        if encounter_ref:
            encounter_id = encounter_ref.replace("Encounter/", "").split("?")[0]
    
    # Extract body site
    body_site = None
    body_site_coding = fhir_condition.get("bodySite", [{}])[0].get("coding", [])
    if body_site_coding:
        body_site = body_site_coding[0].get("display", body_site_coding[0].get("code", None))
    
    # Extract notes
    notes = []
    for note in fhir_condition.get("note", []):
        note_text = note.get("text", "")
        if note_text:
            notes.append(note_text)
    
    return {
        "id": condition_id,
        "patientId": patient_id or "",
        "patientName": None,  # Will be enriched by service
        "condition": condition_text,
        "conditionCode": condition_code,
        "category": category,
        "severity": severity,
        "clinicalStatus": clinical_status.title(),
        "verificationStatus": verification_status.title(),
        "onsetDate": onset_date.split("T")[0] if onset_date and "T" in onset_date else (onset_date or "Unknown"),
        "abatementDate": abatement_date.split("T")[0] if abatement_date and "T" in abatement_date else (abatement_date or None),
        "encounterId": encounter_id,
        "bodySite": body_site,
        "notes": notes,
        "recordedDate": fhir_condition.get("recordedDate", datetime.now().isoformat()).split("T")[0] if fhir_condition.get("recordedDate") else None
    }

def fhir_claim_to_insurance_claim(fhir_claim: Dict) -> Dict:
    """Convert FHIR Claim resource to our Insurance Claim model"""
    claim_id = fhir_claim.get("id", "")
    
    # Extract claim number
    claim_number = claim_id
    for identifier in fhir_claim.get("identifier", []):
        if identifier.get("type", {}).get("coding", [{}])[0].get("code") == "MR":
            claim_number = identifier.get("value", claim_id)
            break
    
    # Extract patient info
    patient_obj = fhir_claim.get("patient", {})
    if isinstance(patient_obj, dict):
        patient_ref = patient_obj.get("reference", "")
    else:
        patient_ref = str(patient_obj) if patient_obj else ""
    patient_id = patient_ref.replace("Patient/", "").split("?")[0] if patient_ref else None
    patient_name = "Unknown Patient"
    
    # Extract hospital/provider info
    provider_obj = fhir_claim.get("provider", {})
    if isinstance(provider_obj, dict):
        provider_ref = provider_obj.get("reference", "")
    else:
        provider_ref = str(provider_obj) if provider_obj else ""
    hospital_id = None
    hospital_name = "Unknown Hospital"
    if provider_ref and "Organization/" in provider_ref:
        hospital_id = provider_ref.replace("Organization/", "").split("?")[0]
    
    # Extract insurance provider
    insurance_provider = "Unknown Provider"
    for insurance in fhir_claim.get("insurance", []):
        coverage_ref = insurance.get("coverage", {}).get("reference", "")
        if coverage_ref:
            # Extract provider name from coverage reference or identifier
            insurance_provider = coverage_ref.split("/")[-1] if "/" in coverage_ref else "Unknown"
            break
    
    # Extract claim type
    claim_type = "Medical"
    type_coding = fhir_claim.get("type", {}).get("coding", [])
    if type_coding:
        claim_type = type_coding[0].get("display", type_coding[0].get("code", "Medical"))
    
    # Extract status
    status = fhir_claim.get("status", "active").title()
    status_mapping = {
        "active": "Pending",
        "cancelled": "Denied",
        "draft": "Pending",
        "entered-in-error": "Rejected"
    }
    status = status_mapping.get(status.lower(), status)
    
    # Extract dates
    created_date = fhir_claim.get("created", datetime.now().isoformat())
    service_date = created_date
    if fhir_claim.get("billablePeriod"):
        service_date = fhir_claim["billablePeriod"].get("start", created_date)
    
    # Extract diagnosis
    diagnosis = "General Examination"
    diagnosis_coding = fhir_claim.get("diagnosis", [{}])[0].get("diagnosis", {}).get("coding", [])
    if diagnosis_coding:
        diagnosis = diagnosis_coding[0].get("display", diagnosis_coding[0].get("code", diagnosis))
    
    # Extract service description
    service_description = claim_type
    items = fhir_claim.get("item", [])
    if items:
        first_item = items[0]
        product_or_service = first_item.get("productOrService", {}).get("coding", [])
        if product_or_service:
            service_description = product_or_service[0].get("display", service_description)
    
    # Extract financial amounts
    total_amount = 0
    for item in items:
        quantity = item.get("quantity", {}).get("value", 1)
        unit_price = item.get("unitPrice", {}).get("value", 0)
        total_amount += quantity * unit_price
    
    # If no items, use total from total field
    if total_amount == 0:
        total_amount = fhir_claim.get("total", {}).get("value", 0)
    
    # Calculate covered amount (assume 80% coverage)
    coverage_percentage = 80
    covered_amount = int(total_amount * (coverage_percentage / 100))
    patient_responsibility = total_amount - covered_amount
    
    return {
        "id": claim_id,
        "claimNumber": claim_number,
        "hospitalId": hospital_id or "",
        "hospitalName": hospital_name,
        "patientId": patient_id or "",
        "patientName": patient_name,
        "provider": insurance_provider,
        "claimType": claim_type,
        "status": status,
        "submissionDate": created_date.split("T")[0] if "T" in created_date else created_date,
        "serviceDate": service_date.split("T")[0] if "T" in service_date else service_date,
        "totalAmount": f"${total_amount:,.2f}",
        "coveredAmount": f"${covered_amount:,.2f}",
        "patientResponsibility": f"${patient_responsibility:,.2f}",
        "diagnosis": diagnosis,
        "serviceDescription": service_description
    }

def fhir_coverage_to_coverage_rule(fhir_coverage: Dict) -> Dict:
    """Convert FHIR Coverage resource to our Coverage Rule model"""
    coverage_id = fhir_coverage.get("id", "")
    
    # Extract subscriber info (patient)
    subscriber_ref = fhir_coverage.get("subscriber", {}).get("reference", "")
    subscriber_id = subscriber_ref.replace("Patient/", "").split("?")[0] if subscriber_ref else None
    
    # Extract beneficiary (who is covered)
    beneficiary_ref = fhir_coverage.get("beneficiary", {}).get("reference", "")
    beneficiary_id = beneficiary_ref.replace("Patient/", "").split("?")[0] if beneficiary_ref else None
    
    # Extract payor (insurance company)
    payor_refs = fhir_coverage.get("payor", [])
    insurance_provider = "Unknown Provider"
    if payor_refs:
        payor_obj = payor_refs[0]
        if isinstance(payor_obj, dict):
            payor_ref = payor_obj.get("reference", "")
            # Try to get display name if available
            if payor_obj.get("display"):
                insurance_provider = payor_obj["display"]
            elif payor_ref:
                # Extract from reference (could be Organization/123 or just an ID)
                if "/" in payor_ref:
                    insurance_provider = payor_ref.split("/")[-1]
                else:
                    insurance_provider = payor_ref
        else:
            insurance_provider = str(payor_obj)
    
    # If still unknown, try to extract from identifier
    if insurance_provider == "Unknown Provider":
        for identifier in fhir_coverage.get("identifier", []):
            if identifier.get("type", {}).get("coding", [{}])[0].get("code") == "MB":
                insurance_provider = identifier.get("value", insurance_provider)
                break
    
    # Extract coverage type
    coverage_type = "Health Insurance"
    type_coding = fhir_coverage.get("type", {}).get("coding", [])
    if type_coding:
        coverage_type = type_coding[0].get("display", type_coding[0].get("code", coverage_type))
    
    # Extract status
    status = fhir_coverage.get("status", "active").title()
    
    # Extract period
    period = fhir_coverage.get("period", {})
    start_date = period.get("start", datetime.now().isoformat())
    end_date = period.get("end", None)
    
    # Extract cost sharing
    cost_to_beneficiary = fhir_coverage.get("costToBeneficiary", [{}])[0] if fhir_coverage.get("costToBeneficiary") else {}
    copay = cost_to_beneficiary.get("value", {}).get("value", 0)
    copay_currency = cost_to_beneficiary.get("value", {}).get("currency", "USD")
    
    # Extract network
    network = fhir_coverage.get("network", [])
    network_type = "In-Network"
    if network:
        network_type = network[0] if isinstance(network[0], str) else "In-Network"
    
    # Extract dependent number
    dependent = fhir_coverage.get("dependent", "")
    
    # Extract relationship
    relationship_coding = fhir_coverage.get("relationship", {}).get("coding", [])
    relationship = "Self"
    if relationship_coding:
        relationship = relationship_coding[0].get("display", relationship_coding[0].get("code", relationship))
    
    # Extract class (coverage details)
    coverage_class = fhir_coverage.get("class", [])
    plan_type = "Standard"
    plan_name = ""
    if coverage_class:
        for cls in coverage_class:
            if cls.get("type", {}).get("coding", [{}])[0].get("code") == "plan":
                plan_name = cls.get("name", plan_name)
            elif cls.get("type", {}).get("coding", [{}])[0].get("code") == "subplan":
                plan_type = cls.get("name", plan_type)
    
    # Extract coverage rules from extensions or text
    rules = []
    if fhir_coverage.get("text"):
        rules.append(fhir_coverage["text"].get("div", ""))
    
    # Common coverage rules based on type
    if "preventive" in coverage_type.lower():
        rules.extend([
            "Preventive care covered at 100%",
            "Annual physical exams covered",
            "Immunizations covered"
        ])
    elif "dental" in coverage_type.lower():
        rules.extend([
            "Dental cleanings covered twice per year",
            "Basic procedures covered at 80%",
            "Major procedures covered at 50%"
        ])
    else:
        rules.extend([
            "In-network providers: 80% coverage after deductible",
            "Out-of-network providers: 60% coverage after deductible",
            "Emergency services: Covered at in-network rates",
            "Prescription drugs: Tier-based copay structure"
        ])
    
    return {
        "id": coverage_id,
        "coverageId": coverage_id,
        "subscriberId": subscriber_id or "",
        "beneficiaryId": beneficiary_id or "",
        "insuranceProvider": insurance_provider,
        "coverageType": coverage_type,
        "planName": plan_name or f"{insurance_provider} {coverage_type}",
        "planType": plan_type,
        "status": status,
        "startDate": start_date.split("T")[0] if "T" in start_date else start_date,
        "endDate": end_date.split("T")[0] if end_date and "T" in end_date else (end_date or "Active"),
        "networkType": network_type,
        "copay": f"${copay:.2f}" if copay > 0 else "Varies",
        "relationship": relationship,
        "dependentNumber": dependent or "N/A",
        "rules": rules[:10]  # Limit to 10 rules
    }


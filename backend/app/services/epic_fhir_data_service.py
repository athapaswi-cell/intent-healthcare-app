"""
Epic FHIR Data Service - Fetches real data from Epic FHIR API
"""
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid
from backend.app.config import (
    EPIC_FHIR_ENABLED, EPIC_FHIR_BASE_URL, EPIC_CLIENT_ID, 
    EPIC_CLIENT_SECRET, EPIC_SCOPES, USE_PUBLIC_FHIR, PUBLIC_FHIR_BASE_URL
)

class EpicFHIRDataService:
    def __init__(self):
        self.use_epic = EPIC_FHIR_ENABLED and EPIC_FHIR_BASE_URL and EPIC_CLIENT_ID
        self.use_public = USE_PUBLIC_FHIR or not self.use_epic
        
        if self.use_epic:
            self.base_url = EPIC_FHIR_BASE_URL
            self.client_id = EPIC_CLIENT_ID
            self.client_secret = EPIC_CLIENT_SECRET
            print(f"[EPIC FHIR] Using Epic FHIR: {self.base_url}")
        elif self.use_public:
            self.base_url = PUBLIC_FHIR_BASE_URL
            print(f"[PUBLIC FHIR] Using public FHIR server: {self.base_url}")
        else:
            print("[FHIR] No FHIR configuration found, using mock data")
            
        self.access_token = None
        self.token_expires = None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token for Epic FHIR (if using Epic)"""
        if not self.use_epic:
            return None  # Public FHIR doesn't need auth
            
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        # For Epic sandbox/public, we might not need authentication
        # This is a simplified version - Epic production requires JWT
        if not self.client_secret:
            print("[EPIC FHIR] No client secret - using public access")
            return None
            
        try:
            token_url = self.base_url.replace('/api/FHIR/R4', '/oauth2/token')
            
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': EPIC_SCOPES
            }
            
            response = requests.post(token_url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                print("[EPIC FHIR] Access token obtained successfully")
                return self.access_token
            else:
                print(f"[EPIC FHIR] Token request failed: {response.status_code}")
                return None
        except Exception as e:
            print(f"[EPIC FHIR] Error getting access token: {e}")
            return None
    
    def _make_fhir_request(self, resource_type: str, params: Dict = None) -> Dict:
        """Make request to FHIR API"""
        headers = {
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }
        
        # Add authorization if using Epic
        if self.use_epic:
            token = self.get_access_token()
            if token:
                headers['Authorization'] = f'Bearer {token}'
        
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = requests.get(url, headers=headers, params=params or {}, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[FHIR] Request failed: {response.status_code} - {response.text}")
                return {'error': f'Request failed: {response.status_code}'}
        except Exception as e:
            print(f"[FHIR] Request error: {str(e)}")
            return {'error': f'Request error: {str(e)}'}
    
    def get_all_hospitals(self) -> List[Dict]:
        """Fetch hospitals from FHIR Organization resource"""
        print("[FHIR] Fetching hospitals from FHIR API...")
        
        result = self._make_fhir_request('Organization', {
            '_count': 200,
            'type': 'prov'  # Provider organizations
        })
        
        if 'error' in result:
            print(f"[FHIR] Error fetching hospitals: {result['error']}")
            return self._get_fallback_hospitals()
        
        hospitals = []
        entries = result.get('entry', [])
        print(f"[FHIR] Found {len(entries)} organizations")
        
        for entry in entries:
            org = entry.get('resource', {})
            
            hospital = {
                'id': org.get('id', str(uuid.uuid4())),
                'name': org.get('name', 'Unknown Hospital'),
                'hospital_type': 'Healthcare Provider',
                'active': org.get('active', True),
                'specialties': [],
                'facilities': ['Emergency', 'Laboratory', 'Radiology'],
                'total_beds': 200 + (hash(org.get('id', '')) % 800),  # Generate realistic bed count
                'icu_beds': 20 + (hash(org.get('id', '')) % 80),
                'operating_hours': '24/7',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract addresses
            addresses = org.get('address', [])
            if addresses:
                addr = addresses[0]
                hospital.update({
                    'address': ', '.join(addr.get('line', ['123 Medical Center Dr'])),
                    'city': addr.get('city', 'Unknown City'),
                    'state': addr.get('state', 'Unknown State'),
                    'zip_code': addr.get('postalCode', '00000'),
                    'country': addr.get('country', 'USA')
                })
            else:
                hospital.update({
                    'address': '123 Medical Center Drive',
                    'city': 'Healthcare City',
                    'state': 'HC',
                    'zip_code': '12345',
                    'country': 'USA'
                })
            
            # Extract contact information
            telecoms = org.get('telecom', [])
            phone_found = False
            for telecom in telecoms:
                if telecom.get('system') == 'phone' and not phone_found:
                    hospital['phone'] = telecom.get('value', '+1-555-0100')
                    hospital['emergency_phone'] = telecom.get('value', '+1-555-0101')
                    phone_found = True
                elif telecom.get('system') == 'email':
                    hospital['email'] = telecom.get('value', 'info@hospital.com')
            
            if not phone_found:
                hospital['phone'] = '+1-555-0100'
                hospital['emergency_phone'] = '+1-555-0101'
                hospital['email'] = 'info@hospital.com'
            
            # Extract specialties from organization types
            types = org.get('type', [])
            for org_type in types:
                codings = org_type.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display and display not in hospital['specialties']:
                        hospital['specialties'].append(display)
            
            # Add default specialties if none found
            if not hospital['specialties']:
                hospital['specialties'] = ['General Medicine', 'Emergency Medicine', 'Surgery']
            
            hospitals.append(hospital)
        
        print(f"[FHIR] Processed {len(hospitals)} hospitals")
        return hospitals if hospitals else self._get_fallback_hospitals()
    
    def get_all_doctors(self) -> List[Dict]:
        """Fetch doctors from FHIR Practitioner resource"""
        print("[FHIR] Fetching doctors from FHIR API...")
        
        result = self._make_fhir_request('Practitioner', {
            '_count': 500,
            'active': 'true'
        })
        
        if 'error' in result:
            print(f"[FHIR] Error fetching doctors: {result['error']}")
            return self._get_fallback_doctors()
        
        doctors = []
        entries = result.get('entry', [])
        print(f"[FHIR] Found {len(entries)} practitioners")
        
        # Realistic doctor names for better user experience
        realistic_names = [
            ("Dr. Sarah", "Johnson"), ("Dr. Michael", "Chen"), ("Dr. Emily", "Rodriguez"),
            ("Dr. David", "Thompson"), ("Dr. Lisa", "Anderson"), ("Dr. James", "Wilson"),
            ("Dr. Maria", "Garcia"), ("Dr. Robert", "Martinez"), ("Dr. Jennifer", "Taylor"),
            ("Dr. Christopher", "Brown"), ("Dr. Amanda", "Davis"), ("Dr. Daniel", "Miller"),
            ("Dr. Jessica", "Moore"), ("Dr. Matthew", "Jackson"), ("Dr. Ashley", "White"),
            ("Dr. Joshua", "Harris"), ("Dr. Stephanie", "Clark"), ("Dr. Andrew", "Lewis"),
            ("Dr. Michelle", "Walker"), ("Dr. Kevin", "Hall"), ("Dr. Rachel", "Allen"),
            ("Dr. Brian", "Young"), ("Dr. Nicole", "King"), ("Dr. Ryan", "Wright"),
            ("Dr. Samantha", "Lopez"), ("Dr. Justin", "Hill"), ("Dr. Megan", "Scott"),
            ("Dr. Brandon", "Green"), ("Dr. Kimberly", "Adams"), ("Dr. Tyler", "Baker"),
            ("Dr. Brittany", "Gonzalez"), ("Dr. Jonathan", "Nelson"), ("Dr. Danielle", "Carter"),
            ("Dr. Nathan", "Mitchell"), ("Dr. Heather", "Perez"), ("Dr. Zachary", "Roberts"),
            ("Dr. Melissa", "Turner"), ("Dr. Aaron", "Phillips"), ("Dr. Amy", "Campbell"),
            ("Dr. Jeremy", "Parker"), ("Dr. Tiffany", "Evans"), ("Dr. Sean", "Edwards"),
            ("Dr. Crystal", "Collins"), ("Dr. Adam", "Stewart"), ("Dr. Vanessa", "Sanchez"),
            ("Dr. Eric", "Morris"), ("Dr. Kathryn", "Rogers"), ("Dr. Jason", "Reed"),
            ("Dr. Lindsay", "Cook"), ("Dr. Mark", "Morgan"), ("Dr. Courtney", "Bell"),
            ("Dr. Steven", "Murphy"), ("Dr. Allison", "Bailey"), ("Dr. Benjamin", "Rivera"),
            ("Dr. Kristen", "Cooper"), ("Dr. Gregory", "Richardson"), ("Dr. Lauren", "Cox"),
            ("Dr. Patrick", "Howard"), ("Dr. Jasmine", "Ward"), ("Dr. Timothy", "Torres"),
            ("Dr. Monica", "Peterson"), ("Dr. Richard", "Gray"), ("Dr. Alexis", "Ramirez"),
            ("Dr. Charles", "James"), ("Dr. Kayla", "Watson"), ("Dr. Jacob", "Brooks"),
            ("Dr. Natalie", "Kelly"), ("Dr. Thomas", "Sanders"), ("Dr. Cassandra", "Price"),
            ("Dr. Nicholas", "Bennett"), ("Dr. Erica", "Wood"), ("Dr. Anthony", "Barnes"),
            ("Dr. Jacqueline", "Ross"), ("Dr. William", "Henderson"), ("Dr. Amber", "Coleman"),
            ("Dr. Kyle", "Jenkins"), ("Dr. Cynthia", "Perry"), ("Dr. Alexander", "Powell"),
            ("Dr. Jenna", "Long"), ("Dr. Jose", "Patterson"), ("Dr. Brooke", "Hughes"),
            ("Dr. Scott", "Flores"), ("Dr. Paige", "Washington"), ("Dr. Ian", "Butler"),
            ("Dr. Haley", "Simmons"), ("Dr. Carl", "Foster"), ("Dr. Destiny", "Gonzales"),
            ("Dr. Lucas", "Bryant"), ("Dr. Mariah", "Alexander"), ("Dr. Mason", "Russell"),
            ("Dr. Gabrielle", "Griffin"), ("Dr. Logan", "Diaz"), ("Dr. Sabrina", "Hayes"),
            ("Dr. Victor", "Myers"), ("Dr. Breanna", "Ford"), ("Dr. Caleb", "Hamilton"),
            ("Dr. Jillian", "Graham"), ("Dr. Ethan", "Sullivan"), ("Dr. Ariana", "Wallace"),
            ("Dr. Devin", "Woods"), ("Dr. Kiara", "Cole"), ("Dr. Garrett", "West"),
            ("Dr. Mikayla", "Jordan"), ("Dr. Trevor", "Owens"), ("Dr. Shelby", "Reynolds"),
            ("Dr. Colton", "Fisher"), ("Dr. Marissa", "Ellis"), ("Dr. Blake", "Gibson"),
            ("Dr. Cheyenne", "Hunt"), ("Dr. Dalton", "Marshall"), ("Dr. Kendra", "Silva")
        ]
        
        for i, entry in enumerate(entries):
            prac = entry.get('resource', {})
            
            # Extract name from FHIR data
            names = prac.get('name', [])
            first_name = 'Dr'
            last_name = 'Unknown'
            
            if names:
                name = names[0]
                given_names = name.get('given', [])
                family_name = name.get('family', '')
                
                if given_names:
                    first_name = ' '.join(given_names) if isinstance(given_names, list) else str(given_names)
                if family_name:
                    last_name = family_name if isinstance(family_name, str) else ' '.join(family_name) if isinstance(family_name, list) else 'Unknown'
            
            # If name is incomplete, "Unknown", or has weird characters, use realistic names
            if (first_name in ['Dr', 'Dr.', ''] or 
                last_name in ['Unknown', ''] or 
                'unknown' in first_name.lower() or 
                'unknown' in last_name.lower() or
                len(first_name) < 2 or len(last_name) < 2 or
                any(char.isdigit() for char in first_name) or
                any(char.isdigit() for char in last_name) or
                len(first_name) > 20 or len(last_name) > 20):
                
                # Use realistic names from our list
                realistic_first, realistic_last = realistic_names[i % len(realistic_names)]
                first_name = realistic_first
                last_name = realistic_last
            else:
                # Clean up existing names
                if not first_name.startswith('Dr'):
                    first_name = f"Dr. {first_name}"
                # Remove numbers and weird characters from names
                import re
                first_name = re.sub(r'\d+', '', first_name)
                last_name = re.sub(r'\d+', '', last_name)
                first_name = re.sub(r'[^\w\s\.]', '', first_name).strip()
                last_name = re.sub(r'[^\w\s\.]', '', last_name).strip()
                
                # If cleaning resulted in empty names, use realistic names
                if len(first_name) < 3 or len(last_name) < 2:
                    realistic_first, realistic_last = realistic_names[i % len(realistic_names)]
                    first_name = realistic_first
                    last_name = realistic_last
            
            doctor = {
                'id': prac.get('id', str(uuid.uuid4())),
                'first_name': first_name,
                'last_name': last_name,
                'active': prac.get('active', True),
                'gender': prac.get('gender', 'unknown'),
                'specialization': 'General Medicine',
                'qualification': 'MD',
                'department': 'General Medicine',
                'experience_years': 5 + (hash(prac.get('id', '')) % 20),
                'languages': ['English'],
                'consultation_fee': 200 + (hash(prac.get('id', '')) % 300),
                'availability': 'Available',
                'rating': 4.0 + (hash(prac.get('id', '')) % 20) / 20,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract contact information
            telecoms = prac.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    doctor['phone'] = telecom.get('value', '+1-555-1000')
                elif telecom.get('system') == 'email':
                    doctor['email'] = telecom.get('value', f"{first_name.lower().replace('dr. ', '').replace(' ', '')}.{last_name.lower()}@hospital.com")
            
            if 'phone' not in doctor:
                doctor['phone'] = '+1-555-1000'
            if 'email' not in doctor:
                clean_first = first_name.lower().replace('dr. ', '').replace(' ', '')
                doctor['email'] = f"{clean_first}.{last_name.lower()}@hospital.com"
            
            # Extract qualifications
            qualifications = prac.get('qualification', [])
            qual_list = []
            for qual in qualifications:
                code = qual.get('code', {})
                codings = code.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display:
                        qual_list.append(display)
            
            if qual_list:
                doctor['qualification'] = ', '.join(qual_list[:2])  # Take first 2
            
            # Extract specialties (this might come from PractitionerRole)
            specialties = ['General Medicine', 'Internal Medicine', 'Family Medicine', 'Emergency Medicine', 
                          'Cardiology', 'Neurology', 'Pediatrics', 'Surgery', 'Oncology', 'Psychiatry']
            doctor['specialization'] = specialties[hash(prac.get('id', '')) % len(specialties)]
            doctor['department'] = doctor['specialization']
            
            doctors.append(doctor)
        
        print(f"[FHIR] Processed {len(doctors)} doctors with realistic names")
        return doctors if doctors else self._get_fallback_doctors()
    
    def get_all_patients(self) -> List[Dict]:
        """Fetch patients from FHIR Patient resource"""
        print("[FHIR] Fetching patients from FHIR API...")
        
        result = self._make_fhir_request('Patient', {
            '_count': 200,
            'active': 'true'
        })
        
        if 'error' in result:
            print(f"[FHIR] Error fetching patients: {result['error']}")
            return self._get_fallback_patients()
        
        patients = []
        entries = result.get('entry', [])
        print(f"[FHIR] Found {len(entries)} patients")
        
        for entry in entries:
            patient_resource = entry.get('resource', {})
            
            # Extract name
            names = patient_resource.get('name', [])
            if names:
                name = names[0]
                first_name = ' '.join(name.get('given', ['Unknown']))
                last_name = name.get('family', 'Patient') if isinstance(name.get('family'), str) else ' '.join(name.get('family', ['Patient']))
            else:
                first_name = 'Unknown'
                last_name = 'Patient'
            
            patient = {
                'id': patient_resource.get('id', str(uuid.uuid4())),
                'first_name': first_name,
                'last_name': last_name,
                'active': patient_resource.get('active', True),
                'gender': patient_resource.get('gender', 'unknown'),
                'date_of_birth': patient_resource.get('birthDate', '1990-01-01'),
                'blood_type': ['A+', 'B+', 'AB+', 'O+', 'A-', 'B-', 'AB-', 'O-'][hash(patient_resource.get('id', '')) % 8],
                'allergies': [],
                'medical_history': [],
                'insurance_provider': ['Blue Cross Blue Shield', 'Aetna', 'Cigna', 'UnitedHealth'][hash(patient_resource.get('id', '')) % 4],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract contact information
            telecoms = patient_resource.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    patient['phone'] = telecom.get('value', '+1-555-2000')
                elif telecom.get('system') == 'email':
                    patient['email'] = telecom.get('value', f"{first_name.lower()}.{last_name.lower()}@email.com")
            
            if 'phone' not in patient:
                patient['phone'] = '+1-555-2000'
            if 'email' not in patient:
                patient['email'] = f"{first_name.lower()}.{last_name.lower()}@email.com"
            
            # Extract address
            addresses = patient_resource.get('address', [])
            if addresses:
                addr = addresses[0]
                address_line = ', '.join(addr.get('line', ['123 Patient St']))
                city = addr.get('city', 'Patient City')
                state = addr.get('state', 'PC')
                postal_code = addr.get('postalCode', '12345')
                patient['address'] = f"{address_line}, {city}, {state} {postal_code}"
            else:
                patient['address'] = "123 Patient Street, Patient City, PC 12345"
            
            # Add some realistic medical data
            common_allergies = ['Penicillin', 'Peanuts', 'Shellfish', 'Latex', 'Aspirin']
            common_conditions = ['Hypertension', 'Diabetes', 'Asthma', 'High Cholesterol', 'Arthritis']
            
            # Randomly assign some allergies and conditions
            patient_hash = hash(patient_resource.get('id', ''))
            if patient_hash % 3 == 0:  # 33% chance of allergies
                patient['allergies'] = [common_allergies[patient_hash % len(common_allergies)]]
            if patient_hash % 4 == 0:  # 25% chance of medical history
                patient['medical_history'] = [common_conditions[patient_hash % len(common_conditions)]]
            
            patients.append(patient)
        
        print(f"[FHIR] Processed {len(patients)} patients")
        return patients if patients else self._get_fallback_patients()
    
    def _get_fallback_hospitals(self) -> List[Dict]:
        """Fallback hospital data if FHIR fails"""
        return [
            {
                'id': str(uuid.uuid4()),
                'name': 'General Hospital',
                'address': '123 Medical Center Drive',
                'city': 'Healthcare City',
                'state': 'HC',
                'zip_code': '12345',
                'phone': '+1-555-0100',
                'emergency_phone': '+1-555-0101',
                'hospital_type': 'General Hospital',
                'total_beds': 300,
                'icu_beds': 30,
                'specialties': ['General Medicine', 'Emergency Medicine', 'Surgery'],
                'facilities': ['ICU', 'Emergency', 'Laboratory', 'Pharmacy', 'Radiology'],
                'operating_hours': '24/7'
            }
        ]
    
    def _get_fallback_doctors(self) -> List[Dict]:
        """Fallback doctor data if FHIR fails"""
        return [
            {
                'id': str(uuid.uuid4()),
                'first_name': 'Dr. Sarah',
                'last_name': 'Johnson',
                'specialization': 'Cardiology',
                'qualification': 'MD, FACC',
                'phone': '+1-555-1001',
                'email': 'sarah.johnson@hospital.com',
                'department': 'Cardiology',
                'experience_years': 12,
                'languages': ['English'],
                'consultation_fee': 350,
                'availability': 'Available'
            },
            {
                'id': str(uuid.uuid4()),
                'first_name': 'Dr. Michael',
                'last_name': 'Chen',
                'specialization': 'Emergency Medicine',
                'qualification': 'MD, FACEP',
                'phone': '+1-555-1002',
                'email': 'michael.chen@hospital.com',
                'department': 'Emergency Medicine',
                'experience_years': 8,
                'languages': ['English', 'Mandarin'],
                'consultation_fee': 275,
                'availability': 'Available'
            },
            {
                'id': str(uuid.uuid4()),
                'first_name': 'Dr. Emily',
                'last_name': 'Rodriguez',
                'specialization': 'Pediatrics',
                'qualification': 'MD, FAAP',
                'phone': '+1-555-1003',
                'email': 'emily.rodriguez@hospital.com',
                'department': 'Pediatrics',
                'experience_years': 10,
                'languages': ['English', 'Spanish'],
                'consultation_fee': 225,
                'availability': 'Available'
            }
        ]
    
    def get_insurance_claims(self, hospital_id: Optional[str] = None) -> List[Dict]:
        """Generate realistic insurance claims data"""
        print("[FHIR] Generating realistic insurance claims...")
        
        # Get hospitals and patients for realistic claims
        hospitals = self.get_all_hospitals()
        patients = self.get_all_patients()
        
        if not hospitals or not patients:
            return []
        
        claims = []
        claim_types = [
            'Emergency Room Visit', 'Routine Check-up', 'Surgery', 'Laboratory Tests',
            'Radiology', 'Prescription Medication', 'Physical Therapy', 'Specialist Consultation'
        ]
        
        insurance_providers = [
            'Blue Cross Blue Shield', 'Aetna', 'Cigna', 'UnitedHealth', 'Humana', 
            'Kaiser Permanente', 'Anthem', 'Molina Healthcare'
        ]
        
        statuses = ['Pending', 'Approved', 'Denied', 'Under Review', 'Paid']
        
        # Generate 20-30 realistic claims
        for i in range(25):
            hospital = hospitals[i % len(hospitals)]
            patient = patients[i % len(patients)]
            
            claim_date = datetime.now() - timedelta(days=hash(str(i)) % 365)
            
            claim = {
                'id': f"CLM-{str(uuid.uuid4())[:8].upper()}",
                'claimNumber': f"CLM{2024}{str(i+1).zfill(6)}",
                'patientId': patient.get('id'),
                'patientName': f"{patient.get('first_name', 'Unknown')} {patient.get('last_name', 'Patient')}",
                'hospitalId': hospital.get('id'),
                'hospitalName': hospital.get('name', 'Unknown Hospital'),
                'serviceType': claim_types[hash(str(i)) % len(claim_types)],
                'insuranceProvider': insurance_providers[hash(str(i)) % len(insurance_providers)],
                'claimAmount': round(500 + (hash(str(i)) % 5000), 2),
                'approvedAmount': 0,
                'status': statuses[hash(str(i)) % len(statuses)],
                'submissionDate': claim_date.isoformat(),
                'processedDate': (claim_date + timedelta(days=hash(str(i)) % 30)).isoformat(),
                'diagnosis': 'ICD-10 Code Placeholder',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Set approved amount based on status
            if claim['status'] in ['Approved', 'Paid']:
                claim['approvedAmount'] = round(claim['claimAmount'] * (0.7 + (hash(str(i)) % 30) / 100), 2)
            elif claim['status'] == 'Denied':
                claim['approvedAmount'] = 0
            else:
                claim['approvedAmount'] = 0  # Pending/Under Review
            
            # Filter by hospital if specified
            if hospital_id and hospital.get('id') != hospital_id:
                continue
                
            claims.append(claim)
        
        print(f"[FHIR] Generated {len(claims)} insurance claims")
        return claims
    
    def get_coverage_rules(self, hospital_id: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """Generate realistic coverage rules data"""
        print("[FHIR] Generating realistic coverage rules...")
        
        coverage_rules = [
            {
                'id': str(uuid.uuid4()),
                'coverageId': f"COV-{str(uuid.uuid4())[:8].upper()}",
                'subscriberId': f"SUB-{str(uuid.uuid4())[:8].upper()}",
                'subscriberName': 'John Doe',
                'beneficiaryId': f"BEN-{str(uuid.uuid4())[:8].upper()}",
                'beneficiaryName': 'John Doe',
                'insuranceProvider': 'Blue Cross Blue Shield',
                'coverageType': 'Medical',
                'planName': 'Emergency Room Coverage Plan',
                'planType': 'PPO',
                'status': 'Active',
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'networkType': 'In-Network',
                'copay': '$150',
                'relationship': 'Self',
                'dependentNumber': '0',
                'rules': ['Emergency room visits covered at 80%', 'Urgent care covered at 90%']
            },
            {
                'id': str(uuid.uuid4()),
                'coverageId': f"COV-{str(uuid.uuid4())[:8].upper()}",
                'subscriberId': f"SUB-{str(uuid.uuid4())[:8].upper()}",
                'subscriberName': 'Jane Smith',
                'beneficiaryId': f"BEN-{str(uuid.uuid4())[:8].upper()}",
                'beneficiaryName': 'Jane Smith',
                'insuranceProvider': 'Aetna',
                'coverageType': 'Medical',
                'planName': 'Routine Care Coverage Plan',
                'planType': 'HMO',
                'status': 'Active',
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'networkType': 'In-Network',
                'copay': '$25',
                'relationship': 'Self',
                'dependentNumber': '0',
                'rules': ['Routine check-ups covered at 100%', 'Preventive care no deductible']
            },
            {
                'id': str(uuid.uuid4()),
                'coverageId': f"COV-{str(uuid.uuid4())[:8].upper()}",
                'subscriberId': f"SUB-{str(uuid.uuid4())[:8].upper()}",
                'subscriberName': 'Robert Johnson',
                'beneficiaryId': f"BEN-{str(uuid.uuid4())[:8].upper()}",
                'beneficiaryName': 'Robert Johnson',
                'insuranceProvider': 'Cigna',
                'coverageType': 'Medical',
                'planName': 'Specialist Consultation Plan',
                'planType': 'EPO',
                'status': 'Active',
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'networkType': 'In-Network',
                'copay': '$50',
                'relationship': 'Self',
                'dependentNumber': '0',
                'rules': ['Specialist consultations covered at 70%', 'Referral required']
            },
            {
                'id': str(uuid.uuid4()),
                'coverageId': f"COV-{str(uuid.uuid4())[:8].upper()}",
                'subscriberId': f"SUB-{str(uuid.uuid4())[:8].upper()}",
                'subscriberName': 'Maria Garcia',
                'beneficiaryId': f"BEN-{str(uuid.uuid4())[:8].upper()}",
                'beneficiaryName': 'Maria Garcia',
                'insuranceProvider': 'UnitedHealth',
                'coverageType': 'Medical',
                'planName': 'Surgery Coverage Plan',
                'planType': 'PPO',
                'status': 'Active',
                'startDate': '2024-01-01',
                'endDate': '2024-12-31',
                'networkType': 'In-Network',
                'copay': '$0',
                'relationship': 'Self',
                'dependentNumber': '0',
                'rules': ['Surgical procedures covered at 85%', 'Pre-authorization required']
            },
            {
                'id': str(uuid.uuid4()),
                'coverageId': f"COV-{str(uuid.uuid4())[:8].upper()}",
                'subscriberId': f"SUB-{str(uuid.uuid4())[:8].upper()}",
                'subscriberName': 'David Wilson',
                'beneficiaryId': f"BEN-{str(uuid.uuid4())[:8].upper()}",
                'beneficiaryName': 'David Wilson',
                'insuranceProvider': 'Kaiser Permanente',
                'coverageType': 'Medical',
                'planName': 'Diagnostic Testing Plan',
                'planType': 'HMO',
                'status': 'Inactive',
                'startDate': '2023-01-01',
                'endDate': '2023-12-31',
                'networkType': 'In-Network',
                'copay': '$20',
                'relationship': 'Self',
                'dependentNumber': '0',
                'rules': ['Laboratory tests covered at 90%', 'Diagnostic imaging covered at 85%']
            }
        ]
        
        print(f"[FHIR] Generated {len(coverage_rules[:limit])} coverage rules")
        return coverage_rules[:limit]

    def get_encounters(self, hospital_id: Optional[str] = None, patient_id: Optional[str] = None) -> List[Dict]:
        """Generate realistic encounter/visit data"""
        print("[FHIR] Generating realistic encounters/visits...")
        
        # Get hospitals and patients for realistic encounters
        hospitals = self.get_all_hospitals()
        patients = self.get_all_patients()
        doctors = self.get_all_doctors()
        
        if not hospitals or not patients or not doctors:
            return []
        
        encounters = []
        encounter_types = [
            'Emergency Room Visit', 'Routine Check-up', 'Follow-up Visit', 'Consultation',
            'Surgery', 'Laboratory Tests', 'Radiology', 'Physical Therapy'
        ]
        
        statuses = ['Finished', 'In Progress', 'Cancelled', 'Planned']
        
        # Generate 20-30 realistic encounters
        for i in range(25):
            hospital = hospitals[i % len(hospitals)]
            patient = patients[i % len(patients)]
            doctor = doctors[i % len(doctors)]
            
            encounter_date = datetime.now() - timedelta(days=hash(str(i)) % 180)
            
            encounter = {
                'id': f"ENC-{str(uuid.uuid4())[:8].upper()}",
                'patientId': patient.get('id'),
                'patientName': f"{patient.get('first_name', 'Unknown')} {patient.get('last_name', 'Patient')}",
                'hospitalId': hospital.get('id'),
                'hospitalName': hospital.get('name', 'Unknown Hospital'),
                'doctorId': doctor.get('id'),
                'doctorName': f"{doctor.get('first_name', 'Dr')} {doctor.get('last_name', 'Unknown')}",
                'encounterType': encounter_types[hash(str(i)) % len(encounter_types)],
                'status': statuses[hash(str(i)) % len(statuses)],
                'startDate': encounter_date.isoformat(),
                'endDate': (encounter_date + timedelta(hours=hash(str(i)) % 24)).isoformat(),
                'diagnosis': f"ICD-10: {['Z00.00', 'M79.3', 'K59.00', 'R50.9', 'I10'][hash(str(i)) % 5]}",
                'notes': f"Patient visit for {encounter_types[hash(str(i)) % len(encounter_types)].lower()}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Filter by hospital or patient if specified
            if hospital_id and hospital.get('id') != hospital_id:
                continue
            if patient_id and patient.get('id') != patient_id:
                continue
                
            encounters.append(encounter)
        
        print(f"[FHIR] Generated {len(encounters)} encounters/visits")
        return encounters

    def get_medical_history(self, patient_id: Optional[str] = None, limit: int = 50) -> List[Dict]:
        """Generate realistic medical history/condition data"""
        print("[FHIR] Generating realistic medical history/conditions...")
        
        # Get patients for realistic medical history
        patients = self.get_all_patients()
        
        if not patients:
            return []
        
        medical_history = []
        
        # Common medical conditions
        conditions = [
            'Hypertension', 'Type 2 Diabetes', 'Asthma', 'High Cholesterol', 'Arthritis',
            'Depression', 'Anxiety', 'Migraine', 'Gastroesophageal Reflux Disease', 'Osteoporosis',
            'Chronic Kidney Disease', 'Atrial Fibrillation', 'Chronic Obstructive Pulmonary Disease',
            'Hypothyroidism', 'Sleep Apnea', 'Coronary Artery Disease', 'Heart Failure',
            'Stroke', 'Cancer (Remission)', 'Allergic Rhinitis'
        ]
        
        categories = [
            'problem-list-item', 'encounter-diagnosis', 'health-concern', 'survey'
        ]
        
        clinical_statuses = ['active', 'recurrence', 'relapse', 'inactive', 'remission', 'resolved']
        verification_statuses = ['confirmed', 'provisional', 'differential', 'entered-in-error']
        severities = ['mild', 'moderate', 'severe']
        
        # Generate 20-30 realistic medical history records
        for i in range(25):
            patient = patients[i % len(patients)]
            
            condition_date = datetime.now() - timedelta(days=hash(str(i)) % 1095)  # Up to 3 years ago
            
            condition_name = conditions[hash(str(i)) % len(conditions)]
            clinical_status = clinical_statuses[hash(str(i)) % len(clinical_statuses)]
            
            history_item = {
                'id': f"COND-{str(uuid.uuid4())[:8].upper()}",
                'patientId': patient.get('id'),
                'patientName': f"{patient.get('first_name', 'Unknown')} {patient.get('last_name', 'Patient')}",
                'condition': condition_name,
                'conditionName': condition_name,
                'conditionCode': f"ICD-10: {['M79.3', 'E11.9', 'J45.9', 'E78.5', 'M19.90'][hash(str(i)) % 5]}",
                'category': categories[hash(str(i)) % len(categories)],
                'clinicalStatus': clinical_status,
                'severity': severities[hash(str(i)) % len(severities)] if hash(str(i)) % 3 == 0 else None,
                'verificationStatus': verification_statuses[hash(str(i)) % len(verification_statuses)],
                'onsetDate': condition_date.strftime('%Y-%m-%d'),
                'onsetDateTime': condition_date.isoformat(),
                'recordedDate': (condition_date + timedelta(days=hash(str(i)) % 30)).strftime('%Y-%m-%d'),
                'bodySite': None,
                'notes': f"Patient diagnosed with {condition_name.lower()} during routine examination.",
                'encounterId': f"ENC-{str(uuid.uuid4())[:8].upper()}",
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Add abatement date for resolved conditions
            if clinical_status in ['resolved', 'remission']:
                abatement_date = condition_date + timedelta(days=hash(str(i)) % 365)
                history_item['abatementDate'] = abatement_date.strftime('%Y-%m-%d')
                history_item['abatementDateTime'] = abatement_date.isoformat()
            else:
                history_item['abatementDate'] = None
                history_item['abatementDateTime'] = None
            
            # Add body site for some conditions
            body_sites = ['chest', 'abdomen', 'head', 'back', 'knee', 'shoulder']
            if condition_name in ['Arthritis', 'Migraine', 'Chronic Pain']:
                history_item['bodySite'] = body_sites[hash(str(i)) % len(body_sites)]
            
            # Filter by patient if specified
            if patient_id and patient.get('id') != patient_id:
                continue
                
            medical_history.append(history_item)
        
        print(f"[FHIR] Generated {len(medical_history)} medical history records")
        return medical_history[:limit]

    def get_bed_availability(self, hospital_id: Optional[str] = None) -> List[Dict]:
        """Generate realistic bed availability data based on real FHIR hospitals"""
        print("[FHIR] Generating realistic bed availability data...")
        
        # Get real hospitals from FHIR
        hospitals = self.get_all_hospitals()
        
        if not hospitals:
            return []
        
        bed_availability = []
        
        for hospital in hospitals:
            hospital_id_val = hospital.get('id', str(uuid.uuid4()))
            hospital_name = hospital.get('name', 'Unknown Hospital')
            
            # Generate realistic bed numbers based on hospital size
            # Use hospital ID hash to ensure consistent data
            hospital_hash = hash(hospital_id_val) % 1000
            
            # Base bed counts (realistic ranges for different hospital sizes)
            base_beds = 100 + (hospital_hash % 400)  # 100-500 beds
            icu_beds = max(10, base_beds // 10)  # ~10% ICU beds
            emergency_beds = max(5, base_beds // 20)  # ~5% emergency beds
            surgery_rooms = max(3, base_beds // 25)  # ~4% surgery rooms
            
            # Generate realistic occupancy (70-95% typical)
            occupancy_base = 70 + (hospital_hash % 25)  # 70-95%
            icu_occupancy_base = 75 + (hospital_hash % 20)  # 75-95%
            
            # Calculate occupied and available
            occupied_beds = int(base_beds * occupancy_base / 100)
            available_beds = base_beds - occupied_beds
            
            occupied_icu = int(icu_beds * icu_occupancy_base / 100)
            available_icu = icu_beds - occupied_icu
            
            # Emergency and surgery availability (usually higher availability)
            available_emergency = max(1, emergency_beds - (hospital_hash % 3))
            available_surgery = max(1, surgery_rooms - (hospital_hash % 2))
            
            # Calculate occupancy rates
            occupancy_rate = round((occupied_beds / base_beds) * 100, 1) if base_beds > 0 else 0
            icu_occupancy_rate = round((occupied_icu / icu_beds) * 100, 1) if icu_beds > 0 else 0
            
            # Determine status based on occupancy
            if occupancy_rate >= 95 or icu_occupancy_rate >= 95:
                status = "Critical"
            elif occupancy_rate >= 85 or icu_occupancy_rate >= 85:
                status = "High"
            else:
                status = "Normal"
            
            bed_data = {
                'id': f"BED-{hospital_id_val}",
                'hospital_id': hospital_id_val,
                'hospital_name': hospital_name,
                'total_beds': base_beds,
                'occupied_beds': occupied_beds,
                'available_beds': available_beds,
                'icu_beds': icu_beds,
                'occupied_icu': occupied_icu,
                'available_icu': available_icu,
                'emergency_beds': emergency_beds,
                'available_emergency': available_emergency,
                'surgery_rooms': surgery_rooms,
                'available_surgery': available_surgery,
                'occupancy_rate': occupancy_rate,
                'icu_occupancy_rate': icu_occupancy_rate,
                'last_updated': datetime.now().isoformat(),
                'status': status,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Filter by hospital if specified
            if hospital_id and hospital_id_val != hospital_id:
                continue
                
            bed_availability.append(bed_data)
        
        print(f"[FHIR] Generated bed availability for {len(bed_availability)} hospitals")
        return bed_availability

    def _get_fallback_patients(self) -> List[Dict]:
        """Fallback patient data if FHIR fails"""
        return [
            {
                'id': str(uuid.uuid4()),
                'first_name': 'Jane',
                'last_name': 'Doe',
                'date_of_birth': '1985-05-15',
                'gender': 'female',
                'phone': '+1-555-2000',
                'email': 'jane.doe@email.com',
                'blood_type': 'O+',
                'allergies': ['Penicillin'],
                'medical_history': ['Hypertension'],
                'address': '456 Patient Avenue, Patient City, PC 67890'
            }
        ]

# Create singleton instance
epic_fhir_data_service = EpicFHIRDataService()
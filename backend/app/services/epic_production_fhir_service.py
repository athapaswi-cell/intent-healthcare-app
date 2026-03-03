"""
Epic Production FHIR Service - Real healthcare data from Epic systems
"""
import jwt
import requests
import json
import uuid
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from backend.app.config import (
    EPIC_FHIR_ENABLED, EPIC_FHIR_BASE_URL, EPIC_CLIENT_ID, 
    EPIC_CLIENT_SECRET, EPIC_SCOPES
)

class EpicProductionFHIRService:
    def __init__(self):
        self.base_url = EPIC_FHIR_BASE_URL
        self.client_id = EPIC_CLIENT_ID
        self.client_secret = EPIC_CLIENT_SECRET
        self.scopes = EPIC_SCOPES
        self.access_token = None
        self.token_expires = None
        
        # Load private key for JWT authentication
        self.private_key = self._load_private_key()
        
        print(f"[EPIC PRODUCTION] Initialized Epic Production FHIR Service")
        print(f"[EPIC PRODUCTION] Base URL: {self.base_url}")
        print(f"[EPIC PRODUCTION] Client ID: {self.client_id[:10]}...")
    
    def _load_private_key(self) -> str:
        """Load private key for JWT authentication"""
        try:
            # Try to load from environment or file
            key_path = Path("epic_private_key.pem")
            if key_path.exists():
                with open(key_path, 'r') as f:
                    return f.read()
            else:
                print("[EPIC PRODUCTION] Warning: Private key not found. Using client_secret method.")
                return None
        except Exception as e:
            print(f"[EPIC PRODUCTION] Error loading private key: {e}")
            return None
    
    def _create_jwt_assertion(self) -> str:
        """Create JWT assertion for Epic authentication"""
        if not self.private_key:
            return None
            
        token_url = self.base_url.replace('/api/FHIR/R4', '/oauth2/token')
        
        payload = {
            'iss': self.client_id,
            'sub': self.client_id,
            'aud': token_url,
            'jti': str(uuid.uuid4()),
            'exp': datetime.utcnow() + timedelta(minutes=5)
        }
        
        try:
            return jwt.encode(payload, self.private_key, algorithm='RS384')
        except Exception as e:
            print(f"[EPIC PRODUCTION] Error creating JWT: {e}")
            return None
    
    def get_access_token(self) -> Optional[str]:
        """Get access token for Epic FHIR"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        token_url = self.base_url.replace('/api/FHIR/R4', '/oauth2/token')
        
        # Try JWT authentication first (production method)
        jwt_assertion = self._create_jwt_assertion()
        if jwt_assertion:
            data = {
                'grant_type': 'client_credentials',
                'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
                'client_assertion': jwt_assertion,
                'scope': self.scopes
            }
        else:
            # Fallback to client_credentials (sandbox method)
            data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': self.scopes
            }
        
        try:
            response = requests.post(token_url, data=data, timeout=30)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                print("[EPIC PRODUCTION] Access token obtained successfully")
                return self.access_token
            else:
                print(f"[EPIC PRODUCTION] Token request failed: {response.status_code}")
                print(f"[EPIC PRODUCTION] Response: {response.text}")
                return None
        except Exception as e:
            print(f"[EPIC PRODUCTION] Error getting access token: {e}")
            return None
    
    def _make_fhir_request(self, resource_type: str, params: Dict = None) -> Dict:
        """Make authenticated request to Epic FHIR API"""
        token = self.get_access_token()
        if not token:
            return {'error': 'Authentication failed'}
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }
        
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = requests.get(url, headers=headers, params=params or {}, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"[EPIC PRODUCTION] Request failed: {response.status_code} - {response.text}")
                return {'error': f'Request failed: {response.status_code}'}
        except Exception as e:
            print(f"[EPIC PRODUCTION] Request error: {str(e)}")
            return {'error': f'Request error: {str(e)}'}
    
    def get_all_hospitals(self) -> List[Dict]:
        """Fetch real hospitals from Epic FHIR"""
        print("[EPIC PRODUCTION] Fetching real hospitals from Epic FHIR...")
        
        result = self._make_fhir_request('Organization', {
            '_count': 100,
            'type': 'prov'
        })
        
        if 'error' in result:
            print(f"[EPIC PRODUCTION] Error: {result['error']}")
            return []
        
        hospitals = []
        entries = result.get('entry', [])
        print(f"[EPIC PRODUCTION] Found {len(entries)} real hospitals")
        
        for entry in entries:
            org = entry.get('resource', {})
            
            hospital = {
                'id': org.get('id'),
                'name': org.get('name', 'Unknown Hospital'),
                'hospital_type': 'Healthcare Provider',
                'active': org.get('active', True),
                'specialties': [],
                'facilities': [],
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract real address
            addresses = org.get('address', [])
            if addresses:
                addr = addresses[0]
                hospital.update({
                    'address': ', '.join(addr.get('line', [])),
                    'city': addr.get('city', ''),
                    'state': addr.get('state', ''),
                    'zip_code': addr.get('postalCode', ''),
                    'country': addr.get('country', 'USA')
                })
            
            # Extract real contact information
            telecoms = org.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    hospital['phone'] = telecom.get('value')
                    hospital['emergency_phone'] = telecom.get('value')
                elif telecom.get('system') == 'email':
                    hospital['email'] = telecom.get('value')
            
            # Extract organization types/specialties
            types = org.get('type', [])
            for org_type in types:
                codings = org_type.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display and display not in hospital['specialties']:
                        hospital['specialties'].append(display)
            
            hospitals.append(hospital)
        
        print(f"[EPIC PRODUCTION] Processed {len(hospitals)} real hospitals")
        return hospitals
    
    def get_all_doctors(self) -> List[Dict]:
        """Fetch real doctors from Epic FHIR"""
        print("[EPIC PRODUCTION] Fetching real doctors from Epic FHIR...")
        
        result = self._make_fhir_request('Practitioner', {
            '_count': 200,
            'active': 'true'
        })
        
        if 'error' in result:
            print(f"[EPIC PRODUCTION] Error: {result['error']}")
            return []
        
        doctors = []
        entries = result.get('entry', [])
        print(f"[EPIC PRODUCTION] Found {len(entries)} real practitioners")
        
        for entry in entries:
            prac = entry.get('resource', {})
            
            # Extract real name
            names = prac.get('name', [])
            first_name = 'Dr.'
            last_name = 'Unknown'
            prefix = []
            suffix = []
            
            if names:
                name = names[0]
                given_names = name.get('given', [])
                family_name = name.get('family', '')
                prefix = name.get('prefix', [])
                suffix = name.get('suffix', [])
                
                if given_names:
                    first_name = ' '.join(given_names)
                if family_name:
                    last_name = family_name
            
            # Format name properly
            if prefix:
                first_name = f"{' '.join(prefix)} {first_name}"
            elif not first_name.startswith('Dr'):
                first_name = f"Dr. {first_name}"
            
            doctor = {
                'id': prac.get('id'),
                'first_name': first_name,
                'last_name': last_name,
                'active': prac.get('active', True),
                'gender': prac.get('gender', 'unknown'),
                'specialization': 'General Medicine',
                'qualification': ', '.join(suffix) if suffix else 'MD',
                'department': 'General Medicine',
                'npi': None,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract NPI (National Provider Identifier)
            identifiers = prac.get('identifier', [])
            for identifier in identifiers:
                if identifier.get('system') == 'http://hl7.org/fhir/sid/us-npi':
                    doctor['npi'] = identifier.get('value')
            
            # Extract real contact information
            telecoms = prac.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    doctor['phone'] = telecom.get('value')
                elif telecom.get('system') == 'email':
                    doctor['email'] = telecom.get('value')
            
            # Extract real qualifications
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
                doctor['qualification'] = ', '.join(qual_list)
            
            doctors.append(doctor)
        
        # Fetch PractitionerRole for specializations
        self._enrich_doctor_specializations(doctors)
        
        print(f"[EPIC PRODUCTION] Processed {len(doctors)} real doctors")
        return doctors
    
    def _enrich_doctor_specializations(self, doctors: List[Dict]):
        """Enrich doctors with real specializations from PractitionerRole"""
        print("[EPIC PRODUCTION] Fetching real specializations...")
        
        result = self._make_fhir_request('PractitionerRole', {
            '_count': 200,
            'active': 'true'
        })
        
        if 'error' in result:
            print(f"[EPIC PRODUCTION] Could not fetch specializations: {result['error']}")
            return
        
        # Create mapping of practitioner ID to specializations
        specialization_map = {}
        entries = result.get('entry', [])
        
        for entry in entries:
            role = entry.get('resource', {})
            practitioner_ref = role.get('practitioner', {}).get('reference', '')
            
            if practitioner_ref:
                prac_id = practitioner_ref.split('/')[-1]
                
                # Extract specialties
                specialties = role.get('specialty', [])
                for specialty in specialties:
                    codings = specialty.get('coding', [])
                    for coding in codings:
                        display = coding.get('display')
                        if display:
                            if prac_id not in specialization_map:
                                specialization_map[prac_id] = []
                            specialization_map[prac_id].append(display)
        
        # Apply specializations to doctors
        for doctor in doctors:
            doctor_id = doctor.get('id')
            if doctor_id in specialization_map:
                specializations = specialization_map[doctor_id]
                if specializations:
                    doctor['specialization'] = specializations[0]  # Primary specialty
                    doctor['department'] = specializations[0]
                    doctor['all_specializations'] = specializations
        
        print(f"[EPIC PRODUCTION] Applied specializations to {len([d for d in doctors if d.get('all_specializations')])} doctors")
    
    def get_all_patients(self) -> List[Dict]:
        """Fetch real patients from Epic FHIR (with privacy considerations)"""
        print("[EPIC PRODUCTION] Fetching real patients from Epic FHIR...")
        
        result = self._make_fhir_request('Patient', {
            '_count': 100,
            'active': 'true'
        })
        
        if 'error' in result:
            print(f"[EPIC PRODUCTION] Error: {result['error']}")
            return []
        
        patients = []
        entries = result.get('entry', [])
        print(f"[EPIC PRODUCTION] Found {len(entries)} real patients")
        
        for entry in entries:
            patient_resource = entry.get('resource', {})
            
            # Extract real name (may be anonymized in production)
            names = patient_resource.get('name', [])
            first_name = 'Patient'
            last_name = 'Unknown'
            
            if names:
                name = names[0]
                given_names = name.get('given', [])
                family_name = name.get('family', '')
                
                if given_names:
                    first_name = ' '.join(given_names)
                if family_name:
                    last_name = family_name
            
            patient = {
                'id': patient_resource.get('id'),
                'first_name': first_name,
                'last_name': last_name,
                'active': patient_resource.get('active', True),
                'gender': patient_resource.get('gender', 'unknown'),
                'date_of_birth': patient_resource.get('birthDate'),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Extract real contact information (if available)
            telecoms = patient_resource.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    patient['phone'] = telecom.get('value')
                elif telecom.get('system') == 'email':
                    patient['email'] = telecom.get('value')
            
            # Extract real address (if available)
            addresses = patient_resource.get('address', [])
            if addresses:
                addr = addresses[0]
                address_parts = []
                if addr.get('line'):
                    address_parts.extend(addr.get('line'))
                if addr.get('city'):
                    address_parts.append(addr.get('city'))
                if addr.get('state'):
                    address_parts.append(addr.get('state'))
                if addr.get('postalCode'):
                    address_parts.append(addr.get('postalCode'))
                
                patient['address'] = ', '.join(address_parts)
            
            patients.append(patient)
        
        print(f"[EPIC PRODUCTION] Processed {len(patients)} real patients")
        return patients

# Create singleton instance
epic_production_fhir_service = EpicProductionFHIRService()
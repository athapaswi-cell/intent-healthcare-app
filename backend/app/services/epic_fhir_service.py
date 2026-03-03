"""
Epic FHIR Service - Real data integration with Epic's FHIR API
"""
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import base64
import os
from backend.app.config import EPIC_FHIR_CONFIG

class EpicFHIRService:
    def __init__(self):
        self.base_url = EPIC_FHIR_CONFIG.get('base_url', 'https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4')
        self.client_id = EPIC_FHIR_CONFIG.get('client_id')
        self.private_key = EPIC_FHIR_CONFIG.get('private_key')
        self.access_token = None
        self.token_expires = None
        
    def get_access_token(self) -> str:
        """Get OAuth2 access token for Epic FHIR API"""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
            
        # Epic uses JWT-based authentication
        token_url = f"{self.base_url.replace('/api/FHIR/R4', '')}/oauth2/token"
        
        # Create JWT assertion (simplified - in production use proper JWT library)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_assertion_type': 'urn:ietf:params:oauth:client-assertion-type:jwt-bearer',
            'client_assertion': self._create_jwt_assertion(),
            'scope': 'system/Patient.read system/Practitioner.read system/Organization.read system/Location.read'
        }
        
        try:
            response = requests.post(token_url, headers=headers, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data['access_token']
                expires_in = token_data.get('expires_in', 3600)
                self.token_expires = datetime.now() + timedelta(seconds=expires_in - 60)
                return self.access_token
            else:
                print(f"Token request failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error getting access token: {e}")
            return None
    
    def _create_jwt_assertion(self) -> str:
        """Create JWT assertion for Epic authentication"""
        # In production, use proper JWT library like PyJWT
        # This is a simplified version
        import jwt
        import time
        
        payload = {
            'iss': self.client_id,
            'sub': self.client_id,
            'aud': f"{self.base_url.replace('/api/FHIR/R4', '')}/oauth2/token",
            'jti': str(time.time()),
            'exp': int(time.time()) + 300,  # 5 minutes
            'iat': int(time.time())
        }
        
        return jwt.encode(payload, self.private_key, algorithm='RS384')
    
    def _make_fhir_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make authenticated request to Epic FHIR API"""
        token = self.get_access_token()
        if not token:
            return {'error': 'Authentication failed'}
            
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params or {})
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Request failed: {response.status_code} - {response.text}'}
        except Exception as e:
            return {'error': f'Request error: {str(e)}'}
    
    def get_organizations(self) -> List[Dict]:
        """Fetch hospital/organization data from Epic FHIR"""
        result = self._make_fhir_request('Organization', {
            '_count': 50,
            'type': 'prov'  # Provider organizations
        })
        
        if 'error' in result:
            return []
            
        organizations = []
        for entry in result.get('entry', []):
            org = entry.get('resource', {})
            
            # Extract organization details
            hospital = {
                'id': org.get('id'),
                'name': org.get('name', 'Unknown Hospital'),
                'type': 'Hospital',
                'active': org.get('active', True),
                'specialties': [],
                'facilities': [],
                'total_beds': None,
                'icu_beds': None,
                'operating_hours': '24/7'
            }
            
            # Extract addresses
            addresses = org.get('address', [])
            if addresses:
                addr = addresses[0]
                hospital.update({
                    'address': ', '.join(addr.get('line', [])),
                    'city': addr.get('city'),
                    'state': addr.get('state'),
                    'zip_code': addr.get('postalCode'),
                    'country': addr.get('country', 'USA')
                })
            
            # Extract contact information
            telecoms = org.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    if telecom.get('use') == 'work':
                        hospital['phone'] = telecom.get('value')
                    elif telecom.get('use') == 'emergency':
                        hospital['emergency_phone'] = telecom.get('value')
                elif telecom.get('system') == 'email':
                    hospital['email'] = telecom.get('value')
            
            # Extract organization type/specialties
            types = org.get('type', [])
            for org_type in types:
                codings = org_type.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display:
                        hospital['specialties'].append(display)
            
            organizations.append(hospital)
        
        return organizations
    
    def get_practitioners(self, organization_id: str = None) -> List[Dict]:
        """Fetch doctor/practitioner data from Epic FHIR"""
        params = {'_count': 100}
        if organization_id:
            params['organization'] = organization_id
            
        result = self._make_fhir_request('Practitioner', params)
        
        if 'error' in result:
            return []
            
        practitioners = []
        for entry in result.get('entry', []):
            prac = entry.get('resource', {})
            
            # Extract practitioner details
            names = prac.get('name', [])
            name = names[0] if names else {}
            
            doctor = {
                'id': prac.get('id'),
                'first_name': ' '.join(name.get('given', [])),
                'last_name': ' '.join(name.get('family', [])) if isinstance(name.get('family'), list) else name.get('family', ''),
                'active': prac.get('active', True),
                'gender': prac.get('gender'),
                'languages': [],
                'specialties': [],
                'qualifications': []
            }
            
            # Extract contact information
            telecoms = prac.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    doctor['phone'] = telecom.get('value')
                elif telecom.get('system') == 'email':
                    doctor['email'] = telecom.get('value')
            
            # Extract qualifications
            qualifications = prac.get('qualification', [])
            for qual in qualifications:
                code = qual.get('code', {})
                codings = code.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display:
                        doctor['qualifications'].append(display)
            
            # Extract communication languages
            communications = prac.get('communication', [])
            for comm in communications:
                codings = comm.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display:
                        doctor['languages'].append(display)
            
            practitioners.append(doctor)
        
        return practitioners
    
    def get_patients(self, limit: int = 50) -> List[Dict]:
        """Fetch patient data from Epic FHIR"""
        result = self._make_fhir_request('Patient', {
            '_count': limit,
            'active': 'true'
        })
        
        if 'error' in result:
            return []
            
        patients = []
        for entry in result.get('entry', []):
            patient_resource = entry.get('resource', {})
            
            # Extract patient details
            names = patient_resource.get('name', [])
            name = names[0] if names else {}
            
            patient = {
                'id': patient_resource.get('id'),
                'first_name': ' '.join(name.get('given', [])),
                'last_name': ' '.join(name.get('family', [])) if isinstance(name.get('family'), list) else name.get('family', ''),
                'active': patient_resource.get('active', True),
                'gender': patient_resource.get('gender'),
                'birth_date': patient_resource.get('birthDate'),
                'deceased': patient_resource.get('deceasedBoolean', False)
            }
            
            # Extract contact information
            telecoms = patient_resource.get('telecom', [])
            for telecom in telecoms:
                if telecom.get('system') == 'phone':
                    patient['phone'] = telecom.get('value')
                elif telecom.get('system') == 'email':
                    patient['email'] = telecom.get('value')
            
            # Extract addresses
            addresses = patient_resource.get('address', [])
            if addresses:
                addr = addresses[0]
                patient['address'] = {
                    'line': addr.get('line', []),
                    'city': addr.get('city'),
                    'state': addr.get('state'),
                    'postal_code': addr.get('postalCode'),
                    'country': addr.get('country')
                }
            
            # Extract marital status
            marital_status = patient_resource.get('maritalStatus', {})
            codings = marital_status.get('coding', [])
            if codings:
                patient['marital_status'] = codings[0].get('display')
            
            patients.append(patient)
        
        return patients
    
    def get_locations(self) -> List[Dict]:
        """Fetch location/facility data from Epic FHIR"""
        result = self._make_fhir_request('Location', {
            '_count': 100,
            'status': 'active'
        })
        
        if 'error' in result:
            return []
            
        locations = []
        for entry in result.get('entry', []):
            location = entry.get('resource', {})
            
            loc_data = {
                'id': location.get('id'),
                'name': location.get('name'),
                'status': location.get('status'),
                'mode': location.get('mode'),
                'type': []
            }
            
            # Extract location types
            types = location.get('type', [])
            for loc_type in types:
                codings = loc_type.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display:
                        loc_data['type'].append(display)
            
            # Extract address
            address = location.get('address', {})
            if address:
                loc_data['address'] = {
                    'line': address.get('line', []),
                    'city': address.get('city'),
                    'state': address.get('state'),
                    'postal_code': address.get('postalCode'),
                    'country': address.get('country')
                }
            
            # Extract contact information
            telecom = location.get('telecom', [])
            for contact in telecom:
                if contact.get('system') == 'phone':
                    loc_data['phone'] = contact.get('value')
                elif contact.get('system') == 'email':
                    loc_data['email'] = contact.get('value')
            
            locations.append(loc_data)
        
        return locations
    
    def get_practitioner_roles(self) -> List[Dict]:
        """Fetch practitioner roles to link doctors with organizations"""
        result = self._make_fhir_request('PractitionerRole', {
            '_count': 200,
            'active': 'true'
        })
        
        if 'error' in result:
            return []
            
        roles = []
        for entry in result.get('entry', []):
            role = entry.get('resource', {})
            
            role_data = {
                'id': role.get('id'),
                'active': role.get('active', True),
                'practitioner_id': None,
                'organization_id': None,
                'location_ids': [],
                'specialties': [],
                'availability': []
            }
            
            # Extract practitioner reference
            practitioner = role.get('practitioner', {})
            if practitioner.get('reference'):
                role_data['practitioner_id'] = practitioner['reference'].split('/')[-1]
            
            # Extract organization reference
            organization = role.get('organization', {})
            if organization.get('reference'):
                role_data['organization_id'] = organization['reference'].split('/')[-1]
            
            # Extract location references
            locations = role.get('location', [])
            for location in locations:
                if location.get('reference'):
                    role_data['location_ids'].append(location['reference'].split('/')[-1])
            
            # Extract specialties
            specialties = role.get('specialty', [])
            for specialty in specialties:
                codings = specialty.get('coding', [])
                for coding in codings:
                    display = coding.get('display')
                    if display:
                        role_data['specialties'].append(display)
            
            roles.append(role_data)
        
        return roles

# Singleton instance
epic_fhir_service = EpicFHIRService()
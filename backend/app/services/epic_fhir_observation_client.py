"""
Epic FHIR Observation Client - For fetching patient vitals and lab observations
Supports both Epic FHIR (with OAuth) and public FHIR servers (no auth)
"""
import requests
from typing import Dict, Optional
from backend.app.config import (
    EPIC_FHIR_ENABLED,
    EPIC_FHIR_BASE_URL,
    EPIC_CLIENT_ID,
    EPIC_CLIENT_SECRET,
    EPIC_OAUTH_URL,
    EPIC_SCOPES,
    USE_PUBLIC_FHIR,
    PUBLIC_FHIR_BASE_URL
)

class EpicFHIRObservationClient:
    """Client for fetching patient observations (vitals/labs) from Epic FHIR or public FHIR"""
    
    def __init__(self):
        self.token: Optional[str] = None
        self.requires_auth = False
        
        # Determine which FHIR server to use
        if EPIC_FHIR_ENABLED and EPIC_FHIR_BASE_URL and EPIC_CLIENT_SECRET:
            # Use Epic FHIR with authentication
            self.fhir_base = EPIC_FHIR_BASE_URL
            self.token_url = EPIC_OAUTH_URL or f"{EPIC_FHIR_BASE_URL.replace('/api/FHIR/R4', '')}/oauth2/token"
            self.requires_auth = True
            print(f"[MONITORING] Using Epic FHIR with authentication: {self.fhir_base}")
        elif USE_PUBLIC_FHIR or (EPIC_FHIR_ENABLED and not EPIC_CLIENT_SECRET):
            # Use public FHIR server (no authentication required)
            self.fhir_base = PUBLIC_FHIR_BASE_URL or "https://hapi.fhir.org/baseR4"
            self.requires_auth = False
            print(f"[MONITORING] Using public FHIR server (no auth): {self.fhir_base}")
        elif EPIC_FHIR_BASE_URL:
            # Try Epic FHIR without auth (may work for some sandbox environments)
            self.fhir_base = EPIC_FHIR_BASE_URL
            self.requires_auth = False
            print(f"[MONITORING] Using Epic FHIR without authentication: {self.fhir_base}")
        else:
            raise RuntimeError("No FHIR server configured. Set USE_PUBLIC_FHIR=true or configure EPIC_FHIR_BASE_URL")

    def get_access_token(self) -> str:
        """
        SMART Backend Services / Client Credentials flow.
        Epic supports client_credentials for system scopes.
        Only called if authentication is required.
        """
        if not self.requires_auth:
            return None  # No token needed for public FHIR
        
        if not self.token_url:
            raise RuntimeError("EPIC_OAUTH_URL or EPIC_FHIR_BASE_URL is not configured in .env file")
        if not EPIC_CLIENT_ID:
            raise RuntimeError("EPIC_CLIENT_ID is not configured in .env file. Please add EPIC_CLIENT_ID=your_client_id")
        if not EPIC_CLIENT_SECRET:
            raise RuntimeError("EPIC_CLIENT_SECRET is not configured in .env file. Please add EPIC_CLIENT_SECRET=your_client_secret")

        data = {
            "grant_type": "client_credentials",
            "client_id": EPIC_CLIENT_ID,
            "client_secret": EPIC_CLIENT_SECRET,
            "scope": EPIC_SCOPES,
        }
        resp = requests.post(self.token_url, data=data, timeout=20)
        resp.raise_for_status()
        self.token = resp.json()["access_token"]
        return self.token

    def _headers(self):
        """Get headers for FHIR requests, including auth if needed"""
        headers = {
            "Accept": "application/fhir+json"
        }
        if self.requires_auth:
            if not self.token:
                self.get_access_token()
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get_patient(self, patient_id: str) -> dict:
        """Fetch patient resource by ID"""
        if not self.fhir_base:
            raise RuntimeError("EPIC_FHIR_BASE_URL is not configured")
        url = f"{self.fhir_base}/Patient/{patient_id}"
        resp = requests.get(url, headers=self._headers(), timeout=20)
        resp.raise_for_status()
        return resp.json()

    def get_observations(self, patient_id: str, category: str, limit: int = 100) -> dict:
        """
        Fetch observations for a patient by category.
        
        Args:
            patient_id: Patient ID
            category: 'vital-signs' or 'laboratory'
            limit: Maximum number of observations to return
            
        Returns:
            FHIR Bundle containing Observation resources
        """
        if not self.fhir_base:
            raise RuntimeError("EPIC_FHIR_BASE_URL is not configured")

        url = f"{self.fhir_base}/Observation"
        params = {
            "patient": patient_id,
            "category": category,
            "_count": limit,
            "_sort": "-date"
        }
        resp = requests.get(url, headers=self._headers(), params=params, timeout=20)
        resp.raise_for_status()
        return resp.json()


"""
FHIR Client Service for retrieving real-time data from FHIR servers
Supports HAPI FHIR, Azure FHIR, EPIC FHIR, and other FHIR R4 servers
"""
import requests
from typing import List, Dict, Optional, Any
import json
from datetime import datetime, timedelta
from backend.app.config import (
    FHIR_BASE_URL, EPIC_FHIR_ENABLED, EPIC_FHIR_BASE_URL,
    EPIC_CLIENT_ID, EPIC_CLIENT_SECRET, EPIC_OAUTH_URL, EPIC_SCOPES,
    USE_PUBLIC_FHIR, PUBLIC_FHIR_BASE_URL
)

class FHIRClient:
    def __init__(self, base_url: str = None):
        """
        Initialize FHIR client
        
        Args:
            base_url: FHIR server base URL (defaults to config setting)
        """
        # Priority: EPIC FHIR > Public FHIR > Configured base URL
        import sys
        if EPIC_FHIR_ENABLED:
            # EPIC FHIR takes highest priority when enabled
            # Use exact URLs from configuration (matching previous project)
            if EPIC_FHIR_BASE_URL:
                self.base_url = EPIC_FHIR_BASE_URL
                print(f"[CONFIG] Using EPIC FHIR Base URL: {self.base_url}", flush=True)
            elif FHIR_BASE_URL:
                self.base_url = FHIR_BASE_URL
                print(f"[CONFIG] Using FHIR Base URL: {self.base_url}", flush=True)
            else:
                self.base_url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"  # Default EPIC URL
                print(f"[WARNING] Using default EPIC FHIR URL. Set EPIC_FHIR_BASE_URL in .env", flush=True)
            
            self.is_epic = True
            # Check if authentication is required (Client Secret provided)
            self.requires_auth = bool(EPIC_CLIENT_SECRET and EPIC_OAUTH_URL)
            
            # Log OAuth URL if configured
            if EPIC_OAUTH_URL:
                print(f"[CONFIG] EPIC OAuth URL: {EPIC_OAUTH_URL}", flush=True)
        elif USE_PUBLIC_FHIR:
            # Use public FHIR only if EPIC is not enabled
            self.base_url = PUBLIC_FHIR_BASE_URL
            self.is_epic = False
            self.requires_auth = False
        else:
            self.base_url = base_url or FHIR_BASE_URL
            self.is_epic = False
            self.requires_auth = False
        
        # Validate base URL
        if not self.base_url:
            print(f"[ERROR] FHIR base URL is empty! Check EPIC_FHIR_BASE_URL or FHIR_BASE_URL in .env", flush=True)
            sys.stdout.flush()
        else:
            print(f"[FHIR] Base URL set to: {self.base_url}", flush=True)
            sys.stdout.flush()
        
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json"
        })
        
        # Store Client ID for use in requests (will try multiple methods)
        self.client_id = EPIC_CLIENT_ID if EPIC_CLIENT_ID else None
        if self.client_id and not self.requires_auth:
            print(f"[INFO] Client ID configured: {self.client_id[:20]}... (will try multiple auth methods)", flush=True)
        
        # EPIC OAuth2 token management
        self._access_token = None
        self._token_expires_at = None
        
        # Authenticate if EPIC is enabled
        if self.is_epic:
            if self.requires_auth:
                # Full OAuth with Client Secret
                self._authenticate_epic()
            elif EPIC_CLIENT_ID and EPIC_OAUTH_URL:
                # Try OAuth with Client ID only (sandbox mode)
                print(f"[INFO] EPIC FHIR sandbox: Attempting Client ID only OAuth")
                if self._try_client_id_only_oauth():
                    print(f"[INFO] OAuth with Client ID only successful")
                else:
                    print(f"[INFO] OAuth failed, will use X-Client-ID header")
            elif EPIC_CLIENT_ID:
                print(f"[INFO] EPIC FHIR enabled with Client ID only (header-based)")
                print(f"[INFO] Using EPIC FHIR Base URL: {self.base_url}")
    
    def _try_client_id_only_oauth(self) -> bool:
        """Try OAuth authentication with Client ID only (for sandbox environments)"""
        if not EPIC_CLIENT_ID or not EPIC_OAUTH_URL:
            return False
        
        try:
            print(f"[INFO] Attempting OAuth with Client ID only: {EPIC_CLIENT_ID[:20]}...")
            token_data = {
                "grant_type": "client_credentials",
                "client_id": EPIC_CLIENT_ID
            }
            response = requests.post(EPIC_OAUTH_URL, data=token_data, timeout=10)
            print(f"[INFO] OAuth response status: {response.status_code}")
            
            if response.status_code == 200:
                token_response = response.json()
                self._access_token = token_response.get("access_token")
                if self._access_token:
                    expires_in = token_response.get("expires_in", 3600)
                    self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    self.session.headers.update({
                        "Authorization": f"Bearer {self._access_token}"
                    })
                    # Remove X-Client-ID header since we're using Bearer token
                    if "X-Client-ID" in self.session.headers:
                        del self.session.headers["X-Client-ID"]
                    print(f"[SUCCESS] EPIC FHIR sandbox authentication successful (Client ID only)")
                    return True
            else:
                print(f"[INFO] OAuth failed with status {response.status_code}: {response.text[:200]}")
        except Exception as e:
            print(f"[INFO] Client ID only OAuth failed: {str(e)}")
        
        return False
    
    def _authenticate_epic(self):
        """Authenticate with EPIC FHIR using OAuth2 Client Credentials flow (with Client Secret)"""
        if not EPIC_CLIENT_ID:
            print("[WARNING] EPIC FHIR enabled but Client ID not configured")
            return False
        
        # If no Client Secret, try Client ID only OAuth first
        if not EPIC_CLIENT_SECRET and EPIC_OAUTH_URL:
            return self._try_client_id_only_oauth()
        
        # If no Client Secret or OAuth URL, assume public/sandbox access with header
        if not EPIC_CLIENT_SECRET or not EPIC_OAUTH_URL:
            print("[INFO] EPIC FHIR using Client ID only (public/sandbox mode - header-based)")
            print(f"[INFO] Client ID: {EPIC_CLIENT_ID}")
            return True
        
        try:
            token_data = {
                "grant_type": "client_credentials",
                "client_id": EPIC_CLIENT_ID,
                "client_secret": EPIC_CLIENT_SECRET,
                "scope": EPIC_SCOPES
            }
            
            response = requests.post(EPIC_OAUTH_URL, data=token_data, timeout=10)
            response.raise_for_status()
            
            token_response = response.json()
            self._access_token = token_response.get("access_token")
            expires_in = token_response.get("expires_in", 3600)
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)  # Refresh 1 min early
            
            # Add authorization header
            self.session.headers.update({
                "Authorization": f"Bearer {self._access_token}"
            })
            
            print(f"[SUCCESS] EPIC FHIR authentication successful")
            return True
        except Exception as e:
            print(f"[ERROR] EPIC FHIR authentication failed: {str(e)}")
            return False
    
    def _ensure_authenticated(self, resource_type: str = None):
        """
        Ensure EPIC token is valid, refresh if needed
        For Client ID only mode, allow access to Organization and Practitioner resources
        """
        if self.is_epic and self.requires_auth:
            if not self._access_token or (self._token_expires_at and datetime.now() >= self._token_expires_at):
                self._authenticate_epic()
        elif self.is_epic and not self.requires_auth and resource_type:
            # Client ID only mode - allow access to non-PHI resources
            if resource_type in ["Organization", "Practitioner"]:
                # These resources may be accessible with Client ID only
                print(f"[INFO] Attempting Client ID only access for {resource_type}", flush=True)
            # For Patient and other PHI resources, will still get 401 (expected)
    
    def search(self, resource_type: str, params: Dict[str, Any] = None) -> List[Dict]:
        """
        Search for FHIR resources
        
        Args:
            resource_type: FHIR resource type (Patient, Practitioner, Organization, etc.)
            params: Search parameters (e.g., {"name": "john", "_count": 10})
        
        Returns:
            List of FHIR resources
        """
        self._ensure_authenticated(resource_type)
        
        url = f"{self.base_url}/{resource_type}"
        
        # Set default count for EPIC
        search_params = params or {}
        if "_count" not in search_params:
            search_params["_count"] = 50
        
        try:
            print(f"[FHIR] Searching {resource_type} at {url}")
            
            # Try multiple authentication methods for Client ID only
            if self.is_epic and not self.requires_auth and self.client_id:
                print(f"[FHIR] Using EPIC FHIR with Client ID only: {self.client_id[:8]}...")
                
                # Try X-Client-ID header first (most common method) with short timeout
                response = None
                try:
                    test_headers = self.session.headers.copy()
                    test_headers["X-Client-ID"] = self.client_id
                    print(f"[FHIR] Trying X-Client-ID header (3s timeout)")
                    test_response = requests.get(url, headers=test_headers, params=search_params, timeout=3)
                    
                    if test_response.status_code == 200:
                        print(f"[SUCCESS] X-Client-ID header method worked!")
                        self.session.headers["X-Client-ID"] = self.client_id
                        response = test_response
                    elif test_response.status_code == 401:
                        # 401 means auth failed - return empty immediately instead of trying other methods
                        print(f"[INFO] X-Client-ID returned 401 - authentication failed")
                        print(f"[INFO] Returning empty results (Client ID authentication not working)")
                        # Return empty bundle to avoid timeout
                        return []
                    else:
                        print(f"[INFO] X-Client-ID returned status {test_response.status_code}")
                        response = test_response
                except requests.exceptions.Timeout:
                    print(f"[INFO] X-Client-ID timeout - EPIC server not responding")
                    # Return empty to avoid frontend timeout
                    return []
                except Exception as e:
                    print(f"[INFO] X-Client-ID error: {str(e)[:100]}")
                    # Return empty to avoid frontend timeout
                    return []
            elif self.is_epic:
                print(f"[FHIR] Using EPIC FHIR with OAuth token")
                response = self.session.get(url, params=search_params, timeout=30)
            else:
                response = self.session.get(url, params=search_params, timeout=30)
            
            response.raise_for_status()
            
            bundle = response.json()
            resources = []
            
            if bundle.get("resourceType") == "Bundle" and bundle.get("entry"):
                for entry in bundle.get("entry", []):
                    if "resource" in entry:
                        resources.append(entry["resource"])
            
            print(f"[FHIR] Successfully retrieved {len(resources)} {resource_type} resources")
            
            # Handle pagination for EPIC
            if self.is_epic and bundle.get("link"):
                for link in bundle.get("link", []):
                    if link.get("relation") == "next":
                        # Could implement pagination here if needed
                        pass
            
            return resources
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] FHIR search error for {resource_type}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"[ERROR] Response status: {e.response.status_code}")
                print(f"[ERROR] Response body: {e.response.text[:500]}")
            return []
    
    def read(self, resource_type: str, resource_id: str) -> Optional[Dict]:
        """
        Read a specific FHIR resource by ID
        
        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID
        
        Returns:
            FHIR resource or None
        """
        self._ensure_authenticated(resource_type)
        
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"FHIR read error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text[:500]}")
            return None
    
    def create(self, resource_type: str, resource: Dict) -> Optional[Dict]:
        """
        Create a new FHIR resource
        
        Args:
            resource_type: FHIR resource type
            resource: FHIR resource data
        
        Returns:
            Created FHIR resource with server-assigned ID
        """
        url = f"{self.base_url}/{resource_type}"
        
        try:
            response = self.session.post(url, json=resource, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"FHIR create error: {e}")
            return None
    
    def update(self, resource_type: str, resource_id: str, resource: Dict) -> Optional[Dict]:
        """
        Update a FHIR resource
        
        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID
            resource: Updated FHIR resource data
        
        Returns:
            Updated FHIR resource
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        resource["id"] = resource_id
        
        try:
            response = self.session.put(url, json=resource, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"FHIR update error: {e}")
            return None
    
    def delete(self, resource_type: str, resource_id: str) -> bool:
        """
        Delete a FHIR resource
        
        Args:
            resource_type: FHIR resource type
            resource_id: Resource ID
        
        Returns:
            True if successful, False otherwise
        """
        url = f"{self.base_url}/{resource_type}/{resource_id}"
        
        try:
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"FHIR delete error: {e}")
            return False


# Global FHIR client instance
_fhir_client: Optional[FHIRClient] = None
_last_config_hash: Optional[str] = None

def get_fhir_client(base_url: str = None) -> FHIRClient:
    """Get or create FHIR client instance - recreates if config changes"""
    import sys
    import hashlib
    global _fhir_client, _last_config_hash
    
    # Create a hash of current config to detect changes (including Client ID)
    config_str = f"{EPIC_FHIR_ENABLED}_{EPIC_FHIR_BASE_URL}_{EPIC_CLIENT_ID}_{USE_PUBLIC_FHIR}_{PUBLIC_FHIR_BASE_URL}_{base_url}"
    config_hash = hashlib.md5(config_str.encode()).hexdigest()
    
    # Recreate client if config changed or doesn't exist
    if _fhir_client is None or _last_config_hash != config_hash:
        if _fhir_client is not None:
            print(f"[FHIR] Configuration changed, recreating FHIR client...", flush=True)
        else:
            print(f"[FHIR] Initializing FHIR client...", flush=True)
        sys.stdout.flush()
        _fhir_client = FHIRClient(base_url)
        _last_config_hash = config_hash
        print(f"[FHIR] FHIR client initialized", flush=True)
        sys.stdout.flush()
    return _fhir_client


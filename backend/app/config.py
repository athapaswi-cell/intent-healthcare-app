"""
Configuration settings for the application
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Find .env file in backend directory (parent of app directory)
backend_dir = Path(__file__).parent.parent
env_file = backend_dir / ".env"
load_dotenv(dotenv_path=env_file)

# Debug: Print loaded values (remove in production)
print(f"[CONFIG] Loading .env from: {env_file}", flush=True)
print(f"[CONFIG] .env file exists: {env_file.exists()}", flush=True)
if os.getenv("EPIC_FHIR_ENABLED", "").lower() == "true":
    print(f"[CONFIG] EPIC_FHIR_ENABLED: {os.getenv('EPIC_FHIR_ENABLED')}", flush=True)
    print(f"[CONFIG] EPIC_FHIR_BASE_URL: {os.getenv('EPIC_FHIR_BASE_URL', 'NOT SET')}", flush=True)
    client_id = os.getenv('EPIC_CLIENT_ID', 'NOT SET')
    print(f"[CONFIG] EPIC_CLIENT_ID: {client_id[:20] if len(client_id) > 20 else client_id}...", flush=True)
    client_secret = os.getenv('EPIC_CLIENT_SECRET', 'NOT SET')
    print(f"[CONFIG] EPIC_CLIENT_SECRET: {'SET' if client_secret and client_secret != 'NOT SET' else 'NOT SET'}...", flush=True)

# FHIR Server Configuration
# EPIC FHIR Base URL format: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
# Or organization-specific: https://fhir.epic.com/[org]/api/FHIR/R4
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "")
FHIR_USE_REAL_DATA = os.getenv("FHIR_USE_REAL_DATA", "true").lower() == "true"

# EPIC FHIR OAuth2 Configuration
EPIC_FHIR_ENABLED = os.getenv("EPIC_FHIR_ENABLED", "false").lower() == "true"
EPIC_FHIR_BASE_URL = os.getenv("EPIC_FHIR_BASE_URL", "")
EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID", "")
EPIC_CLIENT_SECRET = os.getenv("EPIC_CLIENT_SECRET", "")  # Optional - can be empty for public/sandbox servers
EPIC_OAUTH_URL = os.getenv("EPIC_OAUTH_URL", "")  # Optional - can be empty for public/sandbox servers
EPIC_SCOPES = os.getenv("EPIC_SCOPES", "system/Patient.read system/Practitioner.read system/Organization.read system/Encounter.read system/Encounter.read system/Claim.read system/Coverage.read system/Observation.read")

# Public FHIR Server Option (for testing without EPIC credentials)
USE_PUBLIC_FHIR = os.getenv("USE_PUBLIC_FHIR", "false").lower() == "true"
PUBLIC_FHIR_BASE_URL = os.getenv("PUBLIC_FHIR_BASE_URL", "https://hapi.fhir.org/baseR4")  # Public HAPI FHIR server

# Patient Monitoring Configuration
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
HEALTHY_MIN_SCORE = int(os.getenv("HEALTHY_MIN_SCORE", "75"))
AVERAGE_MIN_SCORE = int(os.getenv("AVERAGE_MIN_SCORE", "45"))

# Application Settings
DEBUG = os.getenv("DEBUG", "false").lower() == "true"


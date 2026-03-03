# Patient Monitoring Setup Guide

## Configuration Options

You can run patient monitoring **WITHOUT** an Epic client secret by using a public FHIR server!

### Option 1: Public FHIR Server (No Credentials Required) ✅ RECOMMENDED

Perfect for testing and development. No Epic credentials needed!

```env
# Use Public FHIR Server
USE_PUBLIC_FHIR=true
PUBLIC_FHIR_BASE_URL=https://hapi.fhir.org/baseR4

# Disable Epic FHIR
EPIC_FHIR_ENABLED=false

# Patient Monitoring Configuration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
HEALTHY_MIN_SCORE=75
AVERAGE_MIN_SCORE=45
```

### Option 2: Epic FHIR with Full Credentials (Production)

For production use with Epic FHIR:

```env
# Epic FHIR Configuration
EPIC_FHIR_ENABLED=true
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
EPIC_CLIENT_ID=your_client_id_here
EPIC_CLIENT_SECRET=your_client_secret_here
EPIC_OAUTH_URL=https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token
EPIC_SCOPES=system/Patient.read system/Observation.read system/Practitioner.read system/Organization.read system/Encounter.read system/Claim.read system/Coverage.read

# Patient Monitoring Configuration (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX/YYY/ZZZ
HEALTHY_MIN_SCORE=75
AVERAGE_MIN_SCORE=45
```

### Option 3: Epic FHIR Sandbox (Client ID Only - May Not Work)

Some Epic sandbox environments might work with just a Client ID:

```env
EPIC_FHIR_ENABLED=true
EPIC_FHIR_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4
EPIC_CLIENT_ID=your_client_id_here
# Leave EPIC_CLIENT_SECRET empty
```

**Note:** Most Epic FHIR instances require full OAuth credentials. This may not work.

## Important Notes

1. **You don't need EPIC_CLIENT_SECRET** - Use `USE_PUBLIC_FHIR=true` instead!
2. **Restart the server** after updating `.env` file for changes to take effect
3. The `.env` file should be in the `backend` directory (same level as `requirements.txt`)
4. Public FHIR server has sample/test data - perfect for development and testing

## Testing the Endpoint

Once configured, test the monitoring endpoint:
```
GET http://localhost:8000/api/v1/monitoring/monitor/{patient_id}
```

Or use the API docs at: http://localhost:8000/docs


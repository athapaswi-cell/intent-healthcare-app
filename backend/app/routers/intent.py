
from fastapi import APIRouter
from backend.app.services.intent_engine import execute

router = APIRouter()

@router.post("/execute")
def run_intent(payload: dict):
    return execute(payload)

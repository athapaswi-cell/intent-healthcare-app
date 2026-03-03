import requests
from backend.app.config import SLACK_WEBHOOK_URL

def alert_slack(msg: str) -> bool:
    """Send alert to Slack webhook"""
    if not SLACK_WEBHOOK_URL:
        return False
    try:
        resp = requests.post(SLACK_WEBHOOK_URL, json={"text": msg}, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")
        return False


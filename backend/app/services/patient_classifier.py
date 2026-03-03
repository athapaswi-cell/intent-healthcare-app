from typing import Dict
from backend.app.config import (
    HEALTHY_MIN_SCORE,
    AVERAGE_MIN_SCORE
)

def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def classify(metrics: dict) -> dict:
    """
    metrics must include:
      - HBA1C (%)
      - LDL (mg/dL)
      - SYS_BP (mmHg)
    """
    hba1c = metrics.get("HBA1C")
    ldl = metrics.get("LDL")
    sysbp = metrics.get("SYS_BP")

    if hba1c is None or ldl is None or sysbp is None:
        return {
            "category": "Unknown",
            "score": 0,
            "reason": "Missing required metrics (HbA1c/LDL/Systolic BP)"
        }

    # Demo scoring functions (replace with clinical model as needed)
    hba1c_score = clamp(100 - ((hba1c - 5.0) / (8.0 - 5.0)) * 100, 0, 100)
    ldl_score = clamp(100 - ((ldl - 70) / (220 - 70)) * 100, 0, 100)
    bp_score = clamp(100 - ((sysbp - 110) / (180 - 110)) * 100, 0, 100)

    score = round((hba1c_score + ldl_score + bp_score) / 3, 2)

    if score >= HEALTHY_MIN_SCORE:
        category = "Healthy"
    elif score >= AVERAGE_MIN_SCORE:
        category = "Average"
    else:
        category = "Poor"

    return {
        "category": category,
        "score": score,
        "details": {
            "hba1c": hba1c, "hba1c_score": round(hba1c_score, 1),
            "ldl": ldl, "ldl_score": round(ldl_score, 1),
            "sysbp": sysbp, "bp_score": round(bp_score, 1),
        }
    }


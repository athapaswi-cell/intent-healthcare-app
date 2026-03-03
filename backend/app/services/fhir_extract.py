from typing import Dict, Optional

LOINC = {
    "HBA1C": "4548-4",      # Hemoglobin A1c/Hemoglobin.total in Blood
    "LDL": "13457-7",       # LDL Cholesterol
    "SYS_BP": "8480-6",     # Systolic blood pressure
    "SPO2": "59408-5",      # Oxygen saturation in Arterial blood by Pulse oximetry
    "HR": "8867-4",         # Heart rate
}

def _get_loinc_codes(obs: dict) -> set:
    codes = set()
    coding = obs.get("code", {}).get("coding", [])
    for c in coding:
        if c.get("system", "").endswith("loinc.org"):
            code = c.get("code")
            if code:
                codes.add(code)
    return codes

def _get_value(obs: dict) -> Optional[float]:
    q = obs.get("valueQuantity")
    if not q:
        return None
    return q.get("value")

def extract_metrics_from_bundle(bundle: dict) -> Dict[str, float]:
    """
    Extract latest values for supported metrics.
    We take the first match per metric due to sorting by date desc.
    """
    metrics: Dict[str, float] = {}
    entries = bundle.get("entry", [])
    for e in entries:
        obs = e.get("resource", {})
        if obs.get("resourceType") != "Observation":
            continue

        loincs = _get_loinc_codes(obs)

        # Blood pressure panel components (85354-9)
        if "85354-9" in loincs:
            for comp in obs.get("component", []):
                comp_codes = set()
                for c in comp.get("code", {}).get("coding", []):
                    if c.get("system", "").endswith("loinc.org"):
                        comp_codes.add(c.get("code"))
                if LOINC["SYS_BP"] in comp_codes and "SYS_BP" not in metrics:
                    val = comp.get("valueQuantity", {}).get("value")
                    if val is not None:
                        metrics["SYS_BP"] = float(val)
            continue

        # Direct observation values
        for key, loinc in LOINC.items():
            if loinc in loincs and key not in metrics:
                val = _get_value(obs)
                if val is not None:
                    metrics[key] = float(val)

        # Stop early if main metrics present
        if all(k in metrics for k in ["HBA1C", "LDL", "SYS_BP"]):
            break

    return metrics


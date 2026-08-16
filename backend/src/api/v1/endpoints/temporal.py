import os
import sys
import asyncio
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../")))

from logging_config import get_logger
from api.v1.endpoints.sandbox import get_calibrated_classifier

logger = get_logger("temporal")
router = APIRouter(tags=["Temporal Analysis"])

TIMELINE_EVENTS = [
    {"date": "2026-07-01", "post": "Had a normal day today. School is ok."},
    {"date": "2026-07-05", "post": "Feeling a bit lonely. My friends went out and didn't invite me. Stress is building up."},
    {"date": "2026-07-10", "post": "I failed my chemistry exam. I hate myself. I feel like a massive failure."},
    {"date": "2026-07-15", "post": "I can't sleep anymore. Everything is hopeless and I wish I wouldn't wake up tomorrow."},
]

def _run_temporal_trajectory(model_choice: str):
    classifier = get_calibrated_classifier(model_choice)
    if classifier is None:
        raise HTTPException(status_code=404, detail="Model weights not found.")

    probs = []
    for ev in TIMELINE_EVENTS:
        prob = classifier.predict_proba(ev["post"])["probabilities"][1]
        probs.append({
            "date": ev["date"],
            "post": ev["post"],
            "probability": prob * 100
        })
    return probs

@router.get("/temporal")
async def get_temporal_trajectory(model_choice: str = "Logistic Regression"):
    try:
        return await asyncio.to_thread(_run_temporal_trajectory, model_choice)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Unexpected error in /temporal (model_choice={model_choice})")
        raise HTTPException(status_code=500, detail="Temporal trend analysis failed due to an internal error.")

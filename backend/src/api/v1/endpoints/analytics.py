import os
import sys
import pickle
import asyncio
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../")))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../../../ai_model/src")))

from config import settings as config
from logging_config import get_logger
from services.fairness_auditor import FairnessAuditor
from api.v1.endpoints.sandbox import get_calibrated_classifier

logger = get_logger("analytics")
router = APIRouter(tags=["Analytics & Audits"])

def _load_pickle_artifact(path, not_found_detail):
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail=not_found_detail)
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        logger.exception(f"Failed to load artifact at {path}")
        raise HTTPException(status_code=500, detail="Stored results could not be read. Try regenerating them.")

def _run_fairness_audit(model_choice: str):
    classifier = get_calibrated_classifier(model_choice)
    if classifier is None:
        raise HTTPException(status_code=404, detail="Model weights not found.")

    def audit_predict(text):
        prob = classifier.predict_proba(text)["probabilities"][1]
        return [1.0 - prob, prob]

    return FairnessAuditor().audit_model(audit_predict)

@router.get("/fairness")
async def fairness_audit_endpoint(model_choice: str = "Logistic Regression"):
    try:
        return await asyncio.to_thread(_run_fairness_audit, model_choice)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Unexpected error in /fairness (model_choice={model_choice})")
        raise HTTPException(status_code=500, detail="Fairness audit failed due to an internal error.")

@router.get("/construct-audit")
async def get_construct_validity_audit():
    path = os.path.join(config.MODELS_DIR, "construct_validity_audit.pkl")
    detail = "Construct-validity audit not found. Run construct_validity_auditor.py to generate it first."
    try:
        return await asyncio.to_thread(_load_pickle_artifact, path, detail)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in /construct-audit")
        raise HTTPException(status_code=500, detail="Could not load the construct-validity audit.")

def _load_model_metrics():
    metric_files = {
        "Logistic Regression": "logistic_regression_metrics.pkl",
        "SVM (Calibrated LinearSVC)": "svm_metrics.pkl",
        "BERT (Fine-tuned)": "bert_metrics.pkl",
        "RoBERTa (Fine-tuned)": "roberta_metrics.pkl",
    }
    rows = []
    for label, filename in metric_files.items():
        path = os.path.join(config.MODELS_DIR, filename)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            rows.append({
                "label": label,
                "accuracy": data["accuracy"],
                "precision": data["precision"],
                "recall": data["recall"],
                "f1_score": data["f1_score"],
            })
        except Exception:
            # One corrupt/unreadable metrics file shouldn't hide the others that are fine.
            logger.exception(f"Error loading metrics for {label}")
    return rows

@router.get("/metrics")
@router.get("/model-metrics")
async def model_metrics_endpoint():
    try:
        return await asyncio.to_thread(_load_model_metrics)
    except Exception:
        logger.exception("Unexpected error in /metrics")
        raise HTTPException(status_code=500, detail="Could not load model comparison metrics.")

from services.drift_detector import compute_model_drift_metrics

@router.get("/robustness")
async def robustness_endpoint():
    path = os.path.join(config.MODELS_DIR, "robustness_metrics.pkl")
    detail = "Robustness metrics not found. Run robustness.py to generate them first."
    try:
        return await asyncio.to_thread(_load_pickle_artifact, path, detail)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in /robustness")
        raise HTTPException(status_code=500, detail="Could not load robustness metrics.")

@router.get("/drift-metrics")
async def model_drift_metrics_endpoint():
    """Computes PSI score, prediction probability distribution shift, and model decay indicators."""
    try:
        return await asyncio.to_thread(compute_model_drift_metrics)
    except Exception:
        logger.exception("Unexpected error in /drift-metrics")
        raise HTTPException(status_code=500, detail="Could not calculate model drift metrics.")


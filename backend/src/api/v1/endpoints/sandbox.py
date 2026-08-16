import os
import sys
import pickle
import asyncio
import numpy as np
from fastapi import APIRouter, HTTPException
from functools import lru_cache
from pydantic import BaseModel
from typing import Literal, List, Dict, Any, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../")))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../../../ai_model/src")))

import db
from calibration import apply_temperature
from logging_config import get_logger
from services.anonymizer import mask_pii
from services.explainability import (
    explain_baseline,
    explain_transformer_loo,
    explain_transformer_shap,
    explain_lime,
    what_if_swap,
    compare_explainers,
)
from services.translation import (
    process_multilingual_analysis,
    align_attributions_to_source,
)
from services.clinical_helper import ClinicalResponseHelper
from services.emotion_analyzer import EmotionAnalyzer
from services.cognitive_distortion_analyzer import analyze_distortions, get_dominant_distortions

logger = get_logger("sandbox")
router = APIRouter(tags=["Sandbox & Analysis"])

ExplanationMethod = Literal["fast", "shap", "lime"]
BASELINE_MODEL_CHOICES = ["Logistic Regression", "SVM (Calibrated LinearSVC)"]

class AnalyzeRequest(BaseModel):
    text: str
    model_choice: str
    anonymize_active: bool = True
    explanation_method: ExplanationMethod = "fast"

class WhatIfRequest(BaseModel):
    text: str
    target_word: str
    replacement_word: str
    model_choice: str

@lru_cache(maxsize=4)
def get_baseline_classifier(model_choice: str):
    from baseline_models import BaselineClassifier
    from config import settings as config
    lr_path = os.path.join(config.MODELS_DIR, "logistic_regression.pkl")
    svm_path = os.path.join(config.MODELS_DIR, "svm_classifier.pkl")
    vec_path = os.path.join(config.MODELS_DIR, "tfidf_vectorizer.pkl")
    if "Logistic" in model_choice:
        if os.path.exists(lr_path) and os.path.exists(vec_path):
            return BaselineClassifier(lr_path, vec_path)
    else:
        if os.path.exists(svm_path) and os.path.exists(vec_path):
            return BaselineClassifier(svm_path, vec_path)
    return None

@lru_cache(maxsize=2)
def get_transformer_classifier(model_type: str):
    from transformer_models import TransformerClassifier
    from config import settings as config
    if model_type == "bert":
        model_dir = os.path.join(config.MODELS_DIR, "bert_model")
    else:
        model_dir = os.path.join(config.MODELS_DIR, "roberta_model")
        if not os.path.exists(model_dir):
            model_dir = os.path.join(config.MODELS_DIR, "roberta-base")
    if not os.path.exists(os.path.join(model_dir, "config.json")):
        return None
    try:
        return TransformerClassifier(model_dir)
    except Exception:
        logger.exception(f"Failed to load transformer classifier from {model_dir}")
        return None

@lru_cache(maxsize=1)
def get_multi_tier_classifier():
    from multi_tier_classifier import MultiTierClassifier
    from config import settings as config
    model_path = os.path.join(config.MODELS_DIR, "multi_tier_classifier.pkl")
    if os.path.exists(model_path):
        return MultiTierClassifier(model_path=model_path)
    lr_clf = get_baseline_classifier("Logistic Regression")
    if lr_clf:
        return MultiTierClassifier(binary_model=lr_clf.model, vectorizer=lr_clf.vectorizer)
    return MultiTierClassifier()

@lru_cache(maxsize=1)
def get_emotion_analyzer():
    return EmotionAnalyzer()

CALIBRATION_FILES = {
    "Logistic Regression": "logistic_regression_calibration.pkl",
    "SVM (Calibrated LinearSVC)": "svm_calibration.pkl",
    "BERT (Fine-tuned)": "bert_metrics_calibration.pkl",
    "RoBERTa (Fine-tuned)": "roberta_metrics_calibration.pkl",
}

OOD_FILES = {
    "BERT (Fine-tuned)": "bert_metrics_ood.pkl",
    "RoBERTa (Fine-tuned)": "roberta_metrics_ood.pkl",
}

@lru_cache(maxsize=4)
def get_calibration(model_choice: str):
    from config import settings as config
    filename = CALIBRATION_FILES.get(model_choice)
    if not filename:
        return None
    path = os.path.join(config.MODELS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

@lru_cache(maxsize=2)
def get_ood_calibration(model_choice: str):
    from config import settings as config
    filename = OOD_FILES.get(model_choice)
    if not filename:
        return None
    path = os.path.join(config.MODELS_DIR, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)

class CalibratedClassifier:
    """Transparent proxy that applies temperature-scaling calibration to a classifier's
    predict_proba() output, while forwarding any other attribute access (e.g. .model,
    .vectorizer, .tokenizer, .device used by explainability/OOD/uncertainty) straight
    through to it."""
    def __init__(self, classifier, temperature):
        self._classifier = classifier
        self._temperature = temperature

    def __getattr__(self, name):
        return getattr(self._classifier, name)

    def predict_proba(self, text):
        res = self._classifier.predict_proba(text)
        p1 = apply_temperature(res["probabilities"][1], self._temperature)
        return {"prediction": 1 if p1 >= 0.5 else 0, "probabilities": [1.0 - p1, p1]}

KNOWN_MODEL_CHOICES = {"Logistic Regression", "SVM (Calibrated LinearSVC)", "BERT (Fine-tuned)", "RoBERTa (Fine-tuned)"}

def get_calibrated_classifier(model_choice):
    """Resolves a model choice to its (calibrated, if available) classifier instance.
    Unrecognized model_choice strings return None rather than silently routing to BERT
    (the `else` branch below only distinguishes RoBERTa from BERT, so anything unknown
    needs to be rejected before reaching it, not after)."""
    if model_choice not in KNOWN_MODEL_CHOICES:
        return None

    if model_choice in BASELINE_MODEL_CHOICES:
        classifier = get_baseline_classifier(model_choice)
    else:
        model_type = "roberta" if "RoBERTa" in model_choice else "bert"
        classifier = get_transformer_classifier(model_type)

    if classifier is None:
        return None

    calibration = get_calibration(model_choice)
    if calibration is None:
        return classifier
    return CalibratedClassifier(classifier, calibration["temperature"])

def _predict_proba_batch(classifier, texts):
    """Adapts a classifier's single-text predict_proba() into the batched
    (list[str]) -> (N, 2) array interface LIME's perturbation sampler expects."""
    return np.array([classifier.predict_proba(t)["probabilities"] for t in texts])

def perform_analysis(text, model_choice, anonymize_active, explanation_method: ExplanationMethod = "fast", include_trust_signals=False):
    """Runs the full analysis pipeline for a single piece of text. Shared by the
    /analyze endpoint (manual sandbox use) and the live monitor feed loop."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    is_baseline = model_choice in BASELINE_MODEL_CHOICES

    if explanation_method == "shap" and is_baseline:
        raise HTTPException(
            status_code=400,
            detail="SHAP explanations are only available for transformer models (BERT/RoBERTa).",
        )

    processed_text = text
    if anonymize_active:
        processed_text = mask_pii(text)

    classifier = get_calibrated_classifier(model_choice)
    if classifier is None:
        raise HTTPException(status_code=404, detail=f"Model weights not found for {model_choice}. Train the model first.")

    res = classifier.predict_proba(processed_text)
    prob_suicide = res["probabilities"][1]

    if explanation_method == "lime":
        word_scores = explain_lime(processed_text, lambda texts: _predict_proba_batch(classifier, texts))
    elif is_baseline:
        word_scores = explain_baseline(processed_text, classifier.model, classifier.vectorizer)
    elif explanation_method == "shap":
        word_scores = explain_transformer_shap(processed_text, classifier.model, classifier.tokenizer, classifier.device)
    else:
        word_scores = explain_transformer_loo(processed_text, classifier)

    multi_tier_clf = get_multi_tier_classifier()
    tier_res = multi_tier_clf.predict_tier(processed_text, prob_suicide)
    tier_num = tier_res["tier"]
    tier_label = tier_res["label"]
    tier_probabilities = tier_res["probabilities"]

    emotion_analyzer = get_emotion_analyzer()
    emotions = emotion_analyzer.analyze_emotions(processed_text)
    dominant_emotion = max(emotions, key=emotions.get)

    distortions = analyze_distortions(processed_text)
    dominant_distortions = get_dominant_distortions(processed_text)

    response_helper = ClinicalResponseHelper()
    draft_res = response_helper.generate_draft(tier_num, dominant_emotion, processed_text, dominant_distortions)

    result = {
        "raw_text": text,
        "processed_text": processed_text,
        "model_choice": model_choice,
        "prob_suicide": prob_suicide,
        "word_scores": word_scores,
        "tier_num": tier_num,
        "tier_label": tier_label,
        "tier_probabilities": tier_probabilities,
        "dominant_emotion": dominant_emotion,
        "emotions": emotions,
        "cognitive_distortions": distortions,
        "dominant_distortions": dominant_distortions,
        "draft_response": draft_res["draft"],
        "ood": None,
        "uncertainty": None,
    }

    # OOD/MC-Dropout are transformer-specific techniques (they need raw logits and real
    # dropout layers, which the TF-IDF baselines don't have a faithful equivalent of) and
    # are relatively expensive (MC-Dropout alone runs config.MC_DROPOUT_PASSES extra forward
    # passes), so they're opt-in and skipped entirely for the high-frequency monitor loop.
    if include_trust_signals and not is_baseline:
        ood_calibration = get_ood_calibration(model_choice)
        energy = classifier.compute_energy(processed_text)
        result["ood"] = {
            "energy": energy,
            "threshold": ood_calibration["threshold"] if ood_calibration else None,
            "is_out_of_distribution": (
                energy > ood_calibration["threshold"] if ood_calibration else None
            ),
        }
        result["uncertainty"] = classifier.predict_with_uncertainty(processed_text)

    return result

def _run_analysis_and_log(req: AnalyzeRequest):
    """Synchronous, CPU/GPU-bound: model inference, explainability, and the sqlite write.
    Called off the event loop via asyncio.to_thread from the async route handler below."""
    result = perform_analysis(req.text, req.model_choice, req.anonymize_active, req.explanation_method, include_trust_signals=True)

    try:
        db.insert_analysis(
            processed_text=result["processed_text"],
            model_choice=req.model_choice,
            prob_suicide=result["prob_suicide"],
            tier_num=result["tier_num"],
            tier_label=result["tier_label"],
            dominant_emotion=result["dominant_emotion"],
            source="manual",
        )
    except Exception:
        # A history-logging failure must not fail the analysis the user is waiting on --
        # they still get their result; we just lose this one row of audit history.
        logger.exception("Failed to log manual analysis to db")

    return result

@router.post("/analyze")
async def analyze_text_endpoint(req: AnalyzeRequest):
    try:
        return await asyncio.to_thread(_run_analysis_and_log, req)
    except HTTPException:
        # Expected, well-formed client errors (empty text, unknown model, unsupported
        # explanation method for this model type) -- pass through as-is.
        raise
    except Exception:
        logger.exception(f"Unexpected error in /analyze (model_choice={req.model_choice})")
        raise HTTPException(status_code=500, detail="Analysis failed due to an internal error.")

def _run_what_if(req: WhatIfRequest):
    classifier = get_calibrated_classifier(req.model_choice)
    if classifier is None:
        raise HTTPException(status_code=404, detail="Model weights not found.")
    return what_if_swap(req.text, req.target_word, req.replacement_word, classifier)

@router.post("/what-if")
async def what_if_endpoint(req: WhatIfRequest):
    try:
        return await asyncio.to_thread(_run_what_if, req)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Unexpected error in /what-if (model_choice={req.model_choice})")
        raise HTTPException(status_code=500, detail="What-if simulation failed due to an internal error.")

class ExplainComparisonRequest(BaseModel):
    text: str
    model_choice: str

@router.post("/explain-comparison")
async def explain_comparison_endpoint(req: ExplainComparisonRequest):
    """Runs SHAP, Integrated Gradients, LIME, and LOO attributions side-by-side with correlation matrix."""
    try:
        classifier = get_calibrated_classifier(req.model_choice)
        if classifier is None:
            raise HTTPException(status_code=404, detail="Model weights not found.")
        
        return await asyncio.to_thread(compare_explainers, req.text, classifier)
    except HTTPException:
        raise
    except Exception:
        logger.exception(f"Unexpected error in /explain-comparison (model_choice={req.model_choice})")
        raise HTTPException(status_code=500, detail="Multi-XAI comparison failed.")

class MultilingualAnalyzeRequest(BaseModel):
    text: str
    model_choice: str
    anonymize_active: bool = True

@router.post("/multilingual-analyze")
async def multilingual_analyze_endpoint(req: MultilingualAnalyzeRequest):
    """Translates non-English text, runs model inference & XAI, and projects attributions back onto native tokens."""
    try:
        multi_info = process_multilingual_analysis(req.text)
        
        # Analyze English translated text
        analysis_res = await asyncio.to_thread(
            perform_analysis,
            multi_info["translated_text"],
            req.model_choice,
            req.anonymize_active,
            "fast",
            True
        )

        # Align attributions to source words
        aligned_attributions = align_attributions_to_source(
            req.text,
            multi_info["translated_text"],
            analysis_res["word_scores"]
        )

        analysis_res["multilingual_meta"] = {
            "is_multilingual": multi_info["is_multilingual"],
            "source_language_code": multi_info["source_language_code"],
            "source_language_name": multi_info["source_language_name"],
            "translated_text": multi_info["translated_text"],
            "source_word_scores": aligned_attributions
        }

        return analysis_res
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error in /multilingual-analyze")
        raise HTTPException(status_code=500, detail="Multilingual analysis failed.")


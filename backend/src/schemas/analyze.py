from pydantic import BaseModel, Field
from typing import Literal, List, Dict, Any, Optional

ExplanationMethod = Literal["fast", "shap", "lime"]

class AnalyzeRequest(BaseModel):
    text: str = Field(..., description="Text payload to analyze for risk")
    model_choice: str = Field(..., description="ML model selection")
    anonymize_active: bool = Field(True, description="Flag to toggle PII masking")
    explanation_method: ExplanationMethod = Field("fast", description="Explainability algorithm")

class AnalyzeResponse(BaseModel):
    prob_suicide: float
    raw_prob: float
    tier_num: int
    tier_label: str
    dominant_emotion: str
    processed_text: str
    anonymized: bool
    word_scores: List[Dict[str, Any]]
    explanation_method: str
    cognitive_distortions: Dict[str, Any]
    draft_response: str

class WhatIfRequest(BaseModel):
    text: str
    target_word: str
    replacement_word: str
    model_choice: str

class WhatIfResponse(BaseModel):
    original_text: str
    modified_text: str
    original_prob: float
    modified_prob: float
    original_tier: Dict[str, Any]
    modified_tier: Dict[str, Any]
    delta_prob: float

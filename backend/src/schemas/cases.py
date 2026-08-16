from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class SearchRequest(BaseModel):
    query: str
    top_n: int = 3

class CaseItem(BaseModel):
    id: str
    post: str
    resolution: str
    tier: str
    emotion: str
    similarity_score: Optional[float] = None

class SearchResponse(BaseModel):
    query: str
    results: List[CaseItem]

class ReportRequest(BaseModel):
    raw_text: str
    processed_text: str
    model_choice: str
    tier_label: str
    prob_suicide: float
    tier_num: int
    dominant_emotion: str
    draft_response: str

class ReportResponse(BaseModel):
    report_id: str
    created_at: str
    content: str

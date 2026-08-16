import os
import sys
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../")))

import db
from logging_config import get_logger
from services.semantic_search import CaseSearchEngine
from services.report_generator import ReportGenerator

logger = get_logger("cases")
router = APIRouter(tags=["Cases & Reports"])

search_engine = CaseSearchEngine()

class SearchRequest(BaseModel):
    query: str
    top_n: int = 3

class ReportRequest(BaseModel):
    raw_text: str
    processed_text: str
    model_choice: str
    tier_label: str
    prob_suicide: float
    tier_num: int
    dominant_emotion: str
    draft_response: str

@router.get("/cases")
async def get_cases():
    try:
        return await asyncio.to_thread(db.get_all_cases)
    except Exception:
        logger.exception("Unexpected error in /cases")
        raise HTTPException(status_code=500, detail="Could not load stored cases.")

@router.post("/search")
async def search_cases_endpoint(req: SearchRequest):
    try:
        return await asyncio.to_thread(search_engine.find_similar_cases, req.query, req.top_n)
    except Exception:
        logger.exception(f"Unexpected error in /search (query={req.query!r})")
        raise HTTPException(status_code=500, detail="Case search failed due to an internal error.")

def _generate_report(req: ReportRequest):
    html_content = ReportGenerator.generate_html_report(
        req.raw_text, req.processed_text, req.model_choice,
        req.tier_label, req.prob_suicide, req.tier_num,
        req.dominant_emotion, req.draft_response
    )
    return {"html": html_content}

@router.post("/report")
async def generate_report_endpoint(req: ReportRequest):
    try:
        return await asyncio.to_thread(_generate_report, req)
    except Exception:
        logger.exception("Unexpected error in /report")
        raise HTTPException(status_code=500, detail="Report generation failed due to an internal error.")

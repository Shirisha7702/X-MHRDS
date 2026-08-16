import os
import sys
import asyncio
from fastapi import APIRouter, HTTPException
from schemas.copilot import (
    CopilotAuditRequest,
    CopilotAuditResponse,
    CopilotDispatchRequest,
    CopilotDispatchResponse,
)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../")))

from logging_config import get_logger
from services.clinical_copilot import ClinicalCopilotEngine
from services.rag_copilot import ClinicalRAGCopilotEngine
from pydantic import BaseModel

logger = get_logger("copilot")
router = APIRouter(tags=["Clinical Safety Copilot"])

class CopilotRagQueryRequest(BaseModel):
    text: str
    prob_suicide: float
    dominant_emotion: str = "distress"

@router.post("/copilot/rag-query")
async def copilot_rag_query_endpoint(req: CopilotRagQueryRequest):
    """Queries grounded DSM-5 diagnostic criteria and C-SSRS protocols for clinical copilot."""
    try:
        return await asyncio.to_thread(
            ClinicalRAGCopilotEngine.query_rag_knowledge,
            text=req.text,
            prob_suicide=req.prob_suicide,
            dominant_emotion=req.dominant_emotion
        )
    except Exception:
        logger.exception("Unexpected error in /copilot/rag-query")
        raise HTTPException(status_code=500, detail="RAG query failed.")

@router.post("/copilot/audit", response_model=CopilotAuditResponse)
async def generate_copilot_audit(req: CopilotAuditRequest):
    try:
        return await asyncio.to_thread(
            ClinicalCopilotEngine.generate_compliance_audit,
            raw_text=req.raw_text,
            processed_text=req.processed_text,
            tier_num=req.tier_num,
            tier_label=req.tier_label,
            prob_suicide=req.prob_suicide,
            dominant_emotion=req.dominant_emotion,
            model_choice=req.model_choice,
        )
    except Exception:
        logger.exception("Unexpected error in /copilot/audit")
        raise HTTPException(status_code=500, detail="Compliance audit generation failed due to an internal error.")

@router.post("/copilot/dispatch-protocol", response_model=CopilotDispatchResponse)
async def dispatch_copilot_protocol(req: CopilotDispatchRequest):
    try:
        return await asyncio.to_thread(
            ClinicalCopilotEngine.dispatch_safety_protocol,
            action_type=req.action_type,
            case_id=req.case_id,
            notes=req.notes,
            user_id=req.user_id,
        )
    except Exception:
        logger.exception(f"Unexpected error in /copilot/dispatch-protocol (action_type={req.action_type})")
        raise HTTPException(status_code=500, detail="Safety-protocol dispatch failed due to an internal error.")


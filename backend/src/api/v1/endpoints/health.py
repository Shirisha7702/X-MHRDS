from fastapi import APIRouter
from typing import Dict

router = APIRouter(tags=["Health & System Status"])

@router.get("/status")
async def status_endpoint() -> Dict[str, str]:
    return {"status": "ok"}

@router.get("/health")
async def health_endpoint() -> Dict[str, str]:
    return {"status": "healthy", "service": "X-MHRDS API v1"}

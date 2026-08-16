import os
import sys
import asyncio
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, Any, List

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../../")))

import db
from logging_config import get_logger
from services.monitor_manager import MonitorService
from services.trend_analyzer import get_all_user_trends
from schemas.monitor import MonitorStartRequest, MonitorStatusResponse
from api.v1.endpoints.sandbox import get_calibrated_classifier, perform_analysis

logger = get_logger("monitor")
router = APIRouter(tags=["Live Monitor"])

monitor_service = MonitorService()

@router.post("/monitor/start")
async def start_monitor_endpoint(req: MonitorStartRequest):
    # The model-availability check involves file I/O and (on a cold cache) loading a
    # transformer checkpoint, so it's offloaded to a thread like any other blocking work.
    # monitor_service.start() itself is NOT offloaded: it calls asyncio.create_task(),
    # which needs to run on the event-loop thread -- calling it via asyncio.to_thread would
    # put it on a worker thread with no running loop, raising "RuntimeError: no running
    # event loop" (that's the bug this route already hit once; see the async def above).
    try:
        classifier = await asyncio.to_thread(get_calibrated_classifier, req.model_choice)
    except Exception:
        logger.exception(f"Error checking model availability for monitor start (model_choice={req.model_choice})")
        raise HTTPException(status_code=500, detail="Could not verify model availability.")

    if classifier is None:
        raise HTTPException(status_code=404, detail=f"Model '{req.model_choice}' not loaded.")

    monitor_service.start(req.model_choice, perform_analysis, db.insert_analysis)
    return monitor_service.status()

@router.post("/monitor/stop")
async def stop_monitor_endpoint():
    await monitor_service.stop()
    return monitor_service.status()

@router.get("/monitor/status")
async def get_monitor_status_endpoint():
    return monitor_service.status()

@router.get("/monitor/users")
async def get_monitor_user_trends_endpoint():
    try:
        return await asyncio.to_thread(get_all_user_trends)
    except Exception:
        logger.exception("Unexpected error in /monitor/users")
        raise HTTPException(status_code=500, detail="Could not load escalation-trend data.")

@router.websocket("/ws/monitor")
async def websocket_monitor_endpoint(websocket: WebSocket):
    await monitor_service.manager.connect(websocket)
    try:
        history = await asyncio.to_thread(db.get_recent_monitor_events, 10)
        await websocket.send_json({"type": "history", "events": list(reversed(history))})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        monitor_service.manager.disconnect(websocket)
    except Exception:
        logger.exception("Unexpected error on /ws/monitor connection")
        monitor_service.manager.disconnect(websocket)

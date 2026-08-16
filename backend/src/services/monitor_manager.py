import asyncio
from services.feed_simulator import get_next_post
from logging_config import get_logger

logger = get_logger("monitor_manager")

FEED_INTERVAL_SECONDS = 6
ALERT_TIER_THRESHOLD = 2


class ConnectionManager:
    """Tracks active WebSocket clients and broadcasts monitor events to all of them."""

    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event):
        stale = []
        for connection in self.active_connections:
            try:
                await connection.send_json(event)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


class MonitorService:
    """Owns the simulated live-feed background task and its running/stopped state."""

    def __init__(self):
        self.manager = ConnectionManager()
        self.running = False
        self.model_choice = None
        self._task = None

    def status(self):
        return {"running": self.running, "model_choice": self.model_choice}

    def start(self, model_choice, analysis_fn, insert_analysis_fn):
        if self.running:
            return
        self.running = True
        self.model_choice = model_choice
        self._task = asyncio.create_task(self._run_loop(analysis_fn, insert_analysis_fn))

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None

    async def _run_loop(self, analysis_fn, insert_analysis_fn):
        try:
            while self.running:
                try:
                    user_id, post = get_next_post()
                    result = await asyncio.to_thread(analysis_fn, post, self.model_choice, False)

                    insert_analysis_fn(
                        processed_text=result["processed_text"],
                        model_choice=self.model_choice,
                        prob_suicide=result["prob_suicide"],
                        tier_num=result["tier_num"],
                        tier_label=result["tier_label"],
                        dominant_emotion=result["dominant_emotion"],
                        source="monitor",
                        user_id=user_id,
                    )

                    event = {
                        "type": "event",
                        "user_id": user_id,
                        "post": result["processed_text"],
                        "model_choice": self.model_choice,
                        "prob_suicide": result["prob_suicide"],
                        "tier_num": result["tier_num"],
                        "tier_label": result["tier_label"],
                        "dominant_emotion": result["dominant_emotion"],
                        "alert": result["tier_num"] >= ALERT_TIER_THRESHOLD,
                    }
                    await self.manager.broadcast(event)
                except Exception as exc:
                    # A single bad post must not wedge monitor_service into reporting
                    # "running: true" forever with no further events. Surface the failure
                    # and stop cleanly instead of dying silently as an orphaned task.
                    logger.exception(f"Monitor loop error, stopping: {exc}")
                    self.running = False
                    await self.manager.broadcast({"type": "error", "detail": str(exc)})
                    break
                await asyncio.sleep(FEED_INTERVAL_SECONDS)
        except asyncio.CancelledError:
            pass

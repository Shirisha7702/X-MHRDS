import os
import sys
import time
import uuid

from dotenv import load_dotenv

# Dynamic PYTHONPATH injection to resolve baseline_models, config, services etc.
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../ai_model/src")))

# Loads GOOGLE_API_KEY (and any other secrets) from the repo-root .env, which is
# gitignored -- see .env.example for the expected keys.
load_dotenv(os.path.join(current_dir, "../../.env"))

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from logging_config import get_logger
import db

logger = get_logger("main")
access_logger = get_logger("access")

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    logger.info("Database initialized, API startup complete.")
    yield
    logger.info("API shutting down.")

app = FastAPI(
    title="X-MHRDS API",
    description="Explainable Mental Health Risk Detection System API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware config to allow React requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Structured access logging: every HTTP request gets a short correlation id (so
    the matching request/response lines -- and any exception logged in between by a
    route handler -- can be tied together), plus method, path, status, and latency.
    Does not apply to the /ws/monitor websocket connection (Starlette's "http"
    middleware type only wraps HTTP request/response scopes)."""
    request_id = uuid.uuid4().hex[:8]
    start_time = time.perf_counter()
    access_logger.info(f"[{request_id}] --> {request.method} {request.url.path}")

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000
        access_logger.exception(f"[{request_id}] <-- {request.method} {request.url.path} raised after {duration_ms:.1f}ms")
        raise

    duration_ms = (time.perf_counter() - start_time) * 1000
    response.headers["X-Request-ID"] = request_id
    access_logger.info(f"[{request_id}] <-- {request.method} {request.url.path} {response.status_code} ({duration_ms:.1f}ms)")
    return response

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Last-resort safety net. Route handlers are expected to catch and translate their
    own expected failures into HTTPException (which this handler never sees -- FastAPI's
    own more specific HTTPException handler takes precedence); this only catches whatever
    slips through unhandled, logs it with a full traceback server-side, and returns a
    generic message so internal details (paths, stack traces, library errors) never leak
    to the client."""
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}: {exc}")
    return JSONResponse(status_code=500, content={"detail": "An internal error occurred. Please try again."})

# Include endpoint routes
app.include_router(router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Explainable Mental Health Risk Detection System API is live."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

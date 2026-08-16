from fastapi import APIRouter
from api.v1.endpoints import sandbox, cases, analytics, temporal, monitor, health, copilot

v1_router = APIRouter()

# Include all modular sub-routers
v1_router.include_router(health.router)
v1_router.include_router(sandbox.router)
v1_router.include_router(cases.router)
v1_router.include_router(analytics.router)
v1_router.include_router(temporal.router)
v1_router.include_router(monitor.router)
v1_router.include_router(copilot.router)

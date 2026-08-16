import os
import sys
from fastapi import APIRouter

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "..")))
sys.path.insert(0, os.path.abspath(os.path.join(current_dir, "../../ai_model/src")))

from api.v1.router import v1_router

# Central API Router exporting all V1 endpoints cleanly
router = APIRouter()
router.include_router(v1_router)

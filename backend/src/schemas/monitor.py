from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class MonitorStartRequest(BaseModel):
    model_choice: str = Field("Logistic Regression", description="Model selected for automated feed monitoring")

class MonitorStatusResponse(BaseModel):
    running: bool
    model_choice: str

class UserTrendItem(BaseModel):
    user_id: str
    n_posts: int
    latest_prob_suicide: float
    latest_tier_num: int
    latest_tier_label: str
    trend_label: str
    change_point: Optional[Dict[str, Any]] = None
    history: List[float]

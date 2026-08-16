from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class CopilotAuditRequest(BaseModel):
    raw_text: str
    processed_text: str
    tier_num: int
    tier_label: str
    prob_suicide: float
    dominant_emotion: str
    model_choice: str

class CopilotAuditResponse(BaseModel):
    compliance_hash: str
    hipaa_masked: bool
    detected_pii_types: List[str]
    triage_priority: str
    recommended_protocol: str
    crisis_hotline: str
    action_items: List[str]
    audit_timestamp: str

class CopilotDispatchRequest(BaseModel):
    action_type: str  # e.g., 'dispatch_988', 'flag_human_review', 'escalate_supervisor'
    case_id: Optional[str] = None
    notes: Optional[str] = None
    user_id: Optional[str] = None

class CopilotDispatchResponse(BaseModel):
    dispatch_id: str
    status: str
    is_simulated: bool = False
    action_type: str
    timestamp: str
    confirmation_message: str

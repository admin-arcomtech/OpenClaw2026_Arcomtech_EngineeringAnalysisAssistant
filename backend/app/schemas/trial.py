from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TrialQueueItem(BaseModel):
    id: str
    trial_action: str
    risk_level: str = "LOW"
    estimated_time_min: int = 30
    historical_success_rate: Optional[float] = None
    destructive: bool = False
    required_tools: List[str] = []
    priority_rank: int = 1
    requires_senior_approval: bool = False
    source: str = "ai"  # ai | similar_case | manual
    skipped: bool = False


class TrialQueueRequest(BaseModel):
    items: List[TrialQueueItem]
    status: str = "DRAFT"  # DRAFT | APPROVED


class TrialPriorityRequest(BaseModel):
    case_id: str
    manual_trial: Optional[dict] = None


class TrialPriorityResponse(BaseModel):
    trial_queue: List[TrialQueueItem]
    all_high_risk: bool = False
    warning: Optional[str] = None


class TrialCreateRequest(BaseModel):
    trial_action: str = Field(..., min_length=1)
    outcome: str  # IMPROVED | NO_CHANGE | WORSENED | INCONCLUSIVE
    observation: str = Field(..., min_length=20)
    improvement_pct: Optional[float] = None
    time_spent_min: Optional[int] = None
    scrap_impact: Optional[str] = None
    scrap_qty: Optional[int] = None
    risk_level: Optional[str] = "LOW"
    destructive: bool = False
    engineer_comment: Optional[str] = None
    queue_item_id: Optional[str] = None
    hypothesis: Optional[str] = None

    @field_validator("observation")
    @classmethod
    def observation_min(cls, v: str) -> str:
        if len(v.strip()) < 20:
            raise ValueError("Observasi minimal 20 karakter")
        return v.strip()

    @field_validator("scrap_qty")
    @classmethod
    def scrap_qty_required(cls, v, info):
        return v


class TrialOut(BaseModel):
    id: str
    case_id: str
    sequence: int
    trial_action: Optional[str]
    observation: Optional[str]
    outcome: Optional[str]
    improvement_pct: Optional[float]
    time_spent_min: Optional[int]
    scrap_impact: Optional[str]
    scrap_qty: Optional[int]
    risk_level: Optional[str]
    destructive: bool
    engineer_comment: Optional[str]
    performed_by_id: Optional[str]
    queue_item_id: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ConfirmRootCauseRequest(BaseModel):
    root_cause: str = Field(..., min_length=10, max_length=2000)


class TimelineEvent(BaseModel):
    id: str
    event_type: str
    title: str
    detail: Optional[str] = None
    actor: Optional[str] = None
    created_at: datetime

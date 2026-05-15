from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class WhyStep(BaseModel):
    level: int
    question: str
    answer: str
    category_4m1e: str = Field(description="Man | Machine | Material | Method")


class WhyWhyDraft(BaseModel):
    why_steps: List[WhyStep] = Field(min_length=5)
    immediate_countermeasure: str
    corrective_action: str
    preventive_action: str
    partial: bool = False
    source: str = "fallback"


class WhyWhyOut(BaseModel):
    id: str
    case_id: str
    draft: Optional[dict] = None
    approved_version: Optional[dict] = None
    status: str
    submitted_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    rejection_comment: Optional[str] = None
    is_readonly: bool = False

    class Config:
        from_attributes = True


class WhyWhyUpdateRequest(BaseModel):
    draft: dict


class WhyWhySubmitRequest(BaseModel):
    note: Optional[str] = None


class WhyWhyApproveRequest(BaseModel):
  approved: bool
  comment: Optional[str] = None


class WhyWhyDraftRequest(BaseModel):
    case_id: str
    notes: Optional[str] = None

from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class SimilarCaseRequest(BaseModel):
    case_id: Optional[str] = None
    text: Optional[str] = None
    threshold: float = 0.5
    limit: int = 10


class SimilarCaseItem(BaseModel):
    case_id: str
    id: str
    similarity_pct: float
    title: str
    model: Optional[str]
    process: Optional[str]
    fatal_error: Optional[str]
    status: str
    root_cause: Optional[str] = None
    countermeasure: Optional[str] = None
    resolution_days: Optional[int] = None
    created_at: datetime


class SimilarCaseResponse(BaseModel):
    items: List[SimilarCaseItem]
    source: str  # 'openclaw' | 'fallback' | 'keyword'
    mode: str  # 'vector' | 'keyword'
    warning: Optional[str] = None
    threshold: float
    total_candidates: int


class RecommendationsRequest(BaseModel):
    case_id: str
    extra_context: Optional[str] = None


class Hypothesis(BaseModel):
    title: str
    confidence: int
    category_4m1e: str
    evidence: List[str]
    suggested_verification: List[str]
    trial_risk: str
    estimated_time_min: int
    similar_case_count: int


class RecommendationsResponse(BaseModel):
    id: str
    case_id: str
    hypotheses: List[Hypothesis]
    source: str
    model_version: str
    created_at: datetime


class FeedbackRequest(BaseModel):
    target_type: str  # 'similar_case' | 'recommendation'
    target_id: str
    rating: str  # 'useful' | 'not_relevant' | 'already_tried'
    note: Optional[str] = None

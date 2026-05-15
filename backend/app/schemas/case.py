from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from app.models.case import CaseStatus, Severity, Shift, ScrapImpact, RiskLevel


class CaseCreateRequest(BaseModel):
    model: str = Field(..., min_length=1, max_length=100, description="Model produk")
    process: str = Field(..., min_length=1, max_length=100, description="Proses produksi")
    line: str = Field(..., min_length=1, max_length=100, description="Lini produksi")
    fatal_error: str = Field(..., min_length=1, max_length=200, description="Error fatal")
    symptom: str = Field(..., min_length=1, max_length=500, description="Gejala / symptom")
    description: str = Field(..., min_length=1, max_length=200, description="Deskripsi singkat")
    severity: Severity = Severity.MEDIUM
    shift: Optional[Shift] = None
    temporary_action: Optional[str] = Field(None, max_length=1000)
    operator_id: Optional[str] = Field(None, max_length=100)
    spc_reference: Optional[str] = Field(None, max_length=200)
    assigned_to_id: Optional[str] = None

    @field_validator("description")
    @classmethod
    def description_max(cls, v: str) -> str:
        if len(v) > 200:
            raise ValueError("Deskripsi maksimal 200 karakter")
        return v

    @field_validator("symptom")
    @classmethod
    def symptom_max(cls, v: str) -> str:
        if len(v) > 500:
            raise ValueError("Symptom maksimal 500 karakter")
        return v


class StatusUpdateRequest(BaseModel):
    status: CaseStatus
    note: Optional[str] = Field(None, max_length=500)


class PhotoOut(BaseModel):
    id: str
    filename: str
    storage_path: str
    mime_type: Optional[str]
    file_size_bytes: Optional[int]
    caption: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    id: str
    employee_id: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class CaseOut(BaseModel):
    id: str
    case_id: str
    title: str
    description: Optional[str]
    model: Optional[str]
    process: Optional[str]
    line: Optional[str]
    fatal_error: Optional[str]
    symptom: Optional[str]
    temporary_action: Optional[str]
    operator_id: Optional[str]
    spc_reference: Optional[str]
    status: CaseStatus
    severity: Optional[Severity]
    shift: Optional[Shift]
    scrap_impact: Optional[ScrapImpact]
    risk_level: Optional[RiskLevel]
    production_line: Optional[str]
    reporter_id: str
    assigned_to_id: Optional[str]
    reporter: Optional[UserBrief] = None
    assigned_to: Optional[UserBrief] = None
    photos: List[PhotoOut] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CaseSummary(BaseModel):
    id: str
    case_id: str
    title: str
    model: Optional[str]
    process: Optional[str]
    line: Optional[str]
    fatal_error: Optional[str]
    status: CaseStatus
    severity: Optional[Severity]
    reporter_id: str
    created_at: datetime

    model_config = {"from_attributes": True}


class CaseListResponse(BaseModel):
    items: List[CaseSummary]
    total: int
    page: int
    page_size: int
    pages: int


class DuplicateWarning(BaseModel):
    has_duplicate: bool
    cases: List[CaseSummary] = []

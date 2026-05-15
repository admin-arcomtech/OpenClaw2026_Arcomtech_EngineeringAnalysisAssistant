import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base
from app.models.user import UserRole  # noqa: F401 — used by can_transition


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    SUSPECTED_CAUSE = "SUSPECTED_CAUSE"
    TRIAL_RUNNING = "TRIAL_RUNNING"
    MONITORING = "MONITORING"
    CONFIRMED = "CONFIRMED"
    ARCHIVED = "ARCHIVED"
    # Legacy aliases kept for DB backward compat during migration
    TRIAL_IN_PROGRESS = "TRIAL_IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Severity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Shift(str, enum.Enum):
    PAGI = "PAGI"
    SIANG = "SIANG"
    MALAM = "MALAM"


class ScrapImpact(str, enum.Enum):
    NONE = "NONE"
    MINOR = "MINOR"
    MAJOR = "MAJOR"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class QueueStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    APPROVED = "APPROVED"


# Sprint 4 — full status machine with role gates
# CONFIRMED and ARCHIVED require SENIOR or MANAGER
ROLE_GATED_TARGETS = {CaseStatus.CONFIRMED, CaseStatus.ARCHIVED}
SENIOR_PLUS = {UserRole.SENIOR, UserRole.MANAGER, UserRole.ADMIN}

VALID_TRANSITIONS: dict[CaseStatus, list[CaseStatus]] = {
    CaseStatus.OPEN: [CaseStatus.INVESTIGATING],
    CaseStatus.INVESTIGATING: [CaseStatus.SUSPECTED_CAUSE, CaseStatus.OPEN],
    CaseStatus.SUSPECTED_CAUSE: [CaseStatus.TRIAL_RUNNING, CaseStatus.INVESTIGATING],
    CaseStatus.TRIAL_RUNNING: [CaseStatus.MONITORING, CaseStatus.INVESTIGATING],
    CaseStatus.MONITORING: [CaseStatus.CONFIRMED, CaseStatus.TRIAL_RUNNING],
    CaseStatus.CONFIRMED: [CaseStatus.ARCHIVED],
    CaseStatus.ARCHIVED: [],
    # Legacy path support
    CaseStatus.TRIAL_IN_PROGRESS: [CaseStatus.MONITORING, CaseStatus.INVESTIGATING],
    CaseStatus.RESOLVED: [CaseStatus.CONFIRMED, CaseStatus.ARCHIVED],
    CaseStatus.CLOSED: [CaseStatus.ARCHIVED],
}


def can_transition(role: UserRole, from_status: CaseStatus, to_status: CaseStatus) -> bool:
    allowed = VALID_TRANSITIONS.get(from_status, [])
    if to_status not in allowed:
        return False
    if to_status in ROLE_GATED_TARGETS and role not in SENIOR_PLUS:
        return False
    return True


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, index=True)
    case_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    model = Column(String(100), nullable=True, index=True)
    process = Column(String(100), nullable=True)
    line = Column(String(100), nullable=True)
    fatal_error = Column(String(200), nullable=True, index=True)
    symptom = Column(Text, nullable=True)
    temporary_action = Column(Text, nullable=True)
    operator_id = Column(String(100), nullable=True)
    spc_reference = Column(String(200), nullable=True)

    status = Column(SAEnum(CaseStatus, name="case_status"), nullable=False, default=CaseStatus.OPEN, index=True)
    severity = Column(SAEnum(Severity, name="severity"), nullable=True, default=Severity.MEDIUM)
    shift = Column(SAEnum(Shift, name="shift"), nullable=True)
    scrap_impact = Column(SAEnum(ScrapImpact, name="scrap_impact"), nullable=True, default=ScrapImpact.NONE)
    risk_level = Column(SAEnum(RiskLevel, name="risk_level"), nullable=True)
    production_line = Column(String(100), nullable=True)

    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Sprint 4 — trial queue (F-004)
    trial_queue = Column(JSON, nullable=True)
    trial_queue_status = Column(SAEnum(QueueStatus, name="queue_status"), nullable=True, default=QueueStatus.DRAFT)

    # Sprint 4 — root cause confirmation (Senior+)
    confirmed_root_cause = Column(Text, nullable=True)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    confirmed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    why_why_eligible = Column(String(10), nullable=True, default="false")

    embedding = Column(Vector(1536), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reporter = relationship("User", back_populates="cases", foreign_keys=[reporter_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])
    photos = relationship("CasePhoto", back_populates="case", order_by="CasePhoto.created_at")
    trials = relationship("Trial", back_populates="case", order_by="Trial.sequence")

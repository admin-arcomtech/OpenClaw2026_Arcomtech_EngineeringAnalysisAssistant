import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey, Integer, Float, Boolean
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class TrialOutcome(str, enum.Enum):
    """Sprint 4 F-005 trial log result."""
    IMPROVED = "IMPROVED"
    NO_CHANGE = "NO_CHANGE"
    WORSENED = "WORSENED"
    INCONCLUSIVE = "INCONCLUSIVE"
    PENDING = "PENDING"


class TrialResult(str, enum.Enum):
    """Legacy enum — kept for backward compatibility."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class Trial(Base):
    __tablename__ = "trials"

    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False, default=1)

    # F-005 fields
    trial_action = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)  # alias kept
    hypothesis = Column(Text, nullable=True)
    observation = Column(Text, nullable=True)
    outcome = Column(SAEnum(TrialOutcome, name="trial_outcome"), nullable=True)
    result = Column(SAEnum(TrialResult, name="trial_result"), nullable=False, default=TrialResult.PENDING)
    improvement_pct = Column(Float, nullable=True)
    time_spent_min = Column(Integer, nullable=True)
    scrap_impact = Column(String(20), nullable=True)
    scrap_qty = Column(Integer, nullable=True)
    risk_level = Column(String(20), nullable=True)
    destructive = Column(Boolean, default=False, nullable=False)
    engineer_comment = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    photo_paths = Column(Text, nullable=True)  # JSON array of storage paths

    performed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    queue_item_id = Column(String(50), nullable=True)  # link back to trial_queue item

    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    case = relationship("Case", back_populates="trials")
    performed_by = relationship("User", foreign_keys=[performed_by_id])

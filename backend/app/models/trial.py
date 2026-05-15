import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class TrialResult(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"


class Trial(Base):
    __tablename__ = "trials"

    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    sequence = Column(Integer, nullable=False, default=1)
    action_taken = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    result = Column(SAEnum(TrialResult, name="trial_result"), nullable=False, default=TrialResult.PENDING)
    notes = Column(Text, nullable=True)
    performed_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    # pgvector embedding — stub for Sprint 3
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    case = relationship("Case", back_populates="trials")
    performed_by = relationship("User", foreign_keys=[performed_by_id])

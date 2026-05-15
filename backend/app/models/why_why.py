import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class WhyWhyStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class WhyWhy(Base):
    __tablename__ = "why_why"

    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, unique=True, index=True)
    draft = Column(JSON, nullable=True)
    approved_version = Column(JSON, nullable=True)
    status = Column(SAEnum(WhyWhyStatus, name="why_why_status"), nullable=False, default=WhyWhyStatus.DRAFT)
    submitted_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    approved_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    rejection_comment = Column(Text, nullable=True)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    embedding = Column(Vector(1536), nullable=True)

    case = relationship("Case", backref="why_why_doc", uselist=False)
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])

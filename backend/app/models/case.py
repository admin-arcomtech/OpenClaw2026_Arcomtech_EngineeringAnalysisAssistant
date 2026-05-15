import enum
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Enum as SAEnum, ForeignKey, Integer
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
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


class Case(Base):
    __tablename__ = "cases"

    id = Column(String(36), primary_key=True, index=True)
    case_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    model = Column(String(100), nullable=True, index=True)
    fatal_error = Column(String(200), nullable=True, index=True)
    status = Column(SAEnum(CaseStatus, name="case_status"), nullable=False, default=CaseStatus.OPEN, index=True)
    severity = Column(SAEnum(Severity, name="severity"), nullable=True)
    shift = Column(SAEnum(Shift, name="shift"), nullable=True)
    scrap_impact = Column(SAEnum(ScrapImpact, name="scrap_impact"), nullable=True, default=ScrapImpact.NONE)
    risk_level = Column(SAEnum(RiskLevel, name="risk_level"), nullable=True)
    production_line = Column(String(100), nullable=True)
    reporter_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_to_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    # pgvector embedding — nullable until AI pipeline is active (Sprint 3)
    embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    reporter = relationship("User", back_populates="cases", foreign_keys=[reporter_id])
    assigned_to = relationship("User", foreign_keys=[assigned_to_id])
    photos = relationship("CasePhoto", back_populates="case")
    trials = relationship("Trial", back_populates="case")

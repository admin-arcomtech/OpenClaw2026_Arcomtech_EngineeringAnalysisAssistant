from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    __table_args__ = {"extend_existing": True}

    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    hypotheses = Column(JSON, nullable=False)
    source = Column(String(50), nullable=False, default="openclaw")
    model_version = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class AIFeedback(Base):
    __tablename__ = "ai_feedback"

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)  # 'similar_case' | 'recommendation'
    target_id = Column(String(100), nullable=False)
    rating = Column(String(50), nullable=False)  # 'useful' | 'not_relevant' | 'already_tried'
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

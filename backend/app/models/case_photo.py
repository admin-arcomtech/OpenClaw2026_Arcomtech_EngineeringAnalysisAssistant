from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from app.core.database import Base


class CasePhoto(Base):
    __tablename__ = "case_photos"

    id = Column(String(36), primary_key=True)
    case_id = Column(String(36), ForeignKey("cases.id"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=True)
    file_size_bytes = Column(BigInteger, nullable=True)
    uploaded_by_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    caption = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="photos")
    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id])

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, JSON
from app.core.database import Base


class ImportJob(Base):
    __tablename__ = "import_jobs"

    id = Column(String(36), primary_key=True)
    filename = Column(String(500), nullable=False)
    status = Column(String(30), nullable=False, default="PENDING")
    dry_run = Column(Boolean, nullable=False, default=False)
    total_rows = Column(Integer, nullable=True)
    imported_rows = Column(Integer, nullable=True)
    skipped_rows = Column(Integer, nullable=True)
    error_rows = Column(JSON, nullable=True)
    created_by_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

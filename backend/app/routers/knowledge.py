from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User, UserRole
from app.services.knowledge_search import kb_metrics, search_knowledge

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/search")
def knowledge_search(
    q: str = Query("", description="Search query"),
    model: Optional[str] = None,
    process: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    df = datetime.fromisoformat(date_from) if date_from else None
    dt = datetime.fromisoformat(date_to) if date_to else None
    items, mode = search_knowledge(db, q, model, process, df, dt, limit)
    return {"items": items, "mode": mode, "total": len(items)}


@router.get("/metrics")
def knowledge_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.MANAGER, UserRole.ADMIN])),
):
    return kb_metrics(db)

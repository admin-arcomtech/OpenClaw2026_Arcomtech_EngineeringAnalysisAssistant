"""Knowledge base semantic + keyword search (F-007 UI backend)."""
import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import or_, text
from sqlalchemy.orm import Session

from app.ai import get_provider
from app.models.case import Case, CaseStatus
from app.models.why_why import WhyWhy, WhyWhyStatus

logger = logging.getLogger(__name__)


def search_knowledge(
    db: Session,
    query: str,
    model: Optional[str] = None,
    process: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = 20,
) -> tuple[List[dict], str]:
    q = db.query(Case).filter(
        Case.status.in_([
            CaseStatus.CONFIRMED, CaseStatus.ARCHIVED,
            CaseStatus.RESOLVED, CaseStatus.CLOSED,
        ])
    )
    if model:
        q = q.filter(Case.model == model)
    if process:
        q = q.filter(Case.process == process)
    if date_from:
        q = q.filter(Case.created_at >= date_from)
    if date_to:
        q = q.filter(Case.created_at <= date_to)

    items: List[Case] = []
    mode = "keyword"
    similarities: dict[str, float] = {}

    if query.strip():
        provider = get_provider()
        vector, source = provider.embed(query)
        mode = "vector"
        try:
            sql = text("""
                SELECT id, 1 - (embedding <=> CAST(:vec AS vector)) AS similarity
                FROM cases
                WHERE embedding IS NOT NULL
                  AND status IN ('CONFIRMED','ARCHIVED','RESOLVED','CLOSED')
                ORDER BY embedding <=> CAST(:vec AS vector)
                LIMIT :lim
            """)
            rows = db.execute(sql, {"vec": str(vector), "lim": limit * 2}).fetchall()
            id_to_sim = {r[0]: float(r[1]) for r in rows}
            if id_to_sim:
                cases_map = {c.id: c for c in db.query(Case).filter(Case.id.in_(list(id_to_sim.keys()))).all()}
                items = [cases_map[i] for i in id_to_sim if i in cases_map][:limit]
                similarities = id_to_sim
        except Exception as exc:
            logger.warning("KB vector search failed: %s", exc)
            mode = "keyword"

    if mode == "keyword" or not items:
        tokens = query.lower().split() if query.strip() else []
        base = q.order_by(Case.updated_at.desc()).limit(limit * 3).all()
        if tokens:
            items = [
                c for c in base
                if any(
                    t in (c.title or "").lower()
                    or t in (c.fatal_error or "").lower()
                    or t in (c.confirmed_root_cause or "").lower()
                    or t in (c.symptom or "").lower()
                    for t in tokens
                )
            ][:limit]
        else:
            items = base[:limit]
        mode = "keyword"

    results = []
    for c in items:
        ww = db.query(WhyWhy).filter(WhyWhy.case_id == c.id, WhyWhy.status == WhyWhyStatus.APPROVED).first()
        results.append({
            "case_id": c.case_id,
            "id": c.id,
            "title": c.title,
            "model": c.model,
            "process": c.process,
            "fatal_error": c.fatal_error,
            "root_cause": c.confirmed_root_cause,
            "status": c.status.value if hasattr(c.status, "value") else str(c.status),
            "similarity_pct": round(similarities.get(c.id, 0.5) * 100, 1) if mode == "vector" else None,
            "has_why_why": ww is not None,
            "archived_at": c.archived_at.isoformat() if c.archived_at else None,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })
    return results, mode


def kb_metrics(db: Session) -> dict:
    indexed = db.query(Case).filter(Case.embedding.isnot(None)).count()
    archived = db.query(Case).filter(Case.status == CaseStatus.ARCHIVED).count()
    approved_ww = db.query(WhyWhy).filter(WhyWhy.status == WhyWhyStatus.APPROVED).count()
    from app.models.import_job import ImportJob
    last_import = db.query(ImportJob).order_by(ImportJob.created_at.desc()).first()
    return {
        "indexed_cases": indexed,
        "archived_cases": archived,
        "approved_why_why": approved_ww,
        "last_import_at": last_import.completed_at.isoformat() if last_import and last_import.completed_at else None,
    }

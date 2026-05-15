"""
Embedding pipeline (Sprint 3 / F-002).

Composes the text representation of a case and writes the embedding back
to `cases.embedding` (pgvector vector(N)).
"""
import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.ai import get_provider
from app.core.database import SessionLocal
from app.models.case import Case

logger = logging.getLogger(__name__)


def _case_text(case: Case) -> str:
    """Input embedding text — matches sprint-03-ai-core.md §3.2 spec."""
    parts = [
        case.symptom or "",
        case.fatal_error or "",
        case.model or "",
        case.process or "",
        case.description or "",
    ]
    return " | ".join(p.strip() for p in parts if p)


def embed_case(case_id: str) -> Optional[str]:
    """
    Generate and persist embedding for a case. Runs in BackgroundTasks.
    Returns the provider source tag ('openclaw' | 'fallback') or None on failure.
    """
    db: Session = SessionLocal()
    try:
        case = db.query(Case).filter(Case.id == case_id).first()
        if not case:
            logger.warning("embed_case: case %s not found", case_id)
            return None

        text = _case_text(case)
        if not text:
            logger.info("embed_case: empty text for %s, skip", case.case_id)
            return None

        provider = get_provider()
        vector, source = provider.embed(text)

        case.embedding = vector
        db.commit()
        logger.info("embed_case: %s embedded via %s", case.case_id, source)
        return source
    except Exception as exc:
        logger.exception("embed_case failed for %s: %s", case_id, exc)
        db.rollback()
        return None
    finally:
        db.close()


def embed_all_pending(limit: int = 100) -> int:
    """Batch embed cases with NULL embedding. Returns count processed."""
    db: Session = SessionLocal()
    try:
        cases = db.query(Case).filter(Case.embedding.is_(None)).limit(limit).all()
        n = 0
        for c in cases:
            text = _case_text(c)
            if not text:
                continue
            provider = get_provider()
            vector, source = provider.embed(text)
            c.embedding = vector
            n += 1
            logger.info("Re-embed %s via %s", c.case_id, source)
        db.commit()
        return n
    finally:
        db.close()

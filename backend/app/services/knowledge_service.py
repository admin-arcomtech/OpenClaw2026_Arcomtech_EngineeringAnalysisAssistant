"""
Knowledge Memory Engine (F-007) — Sprint 4.

Auto-embed on: trial logged, root cause confirmed, case archived.
"""
import logging
from sqlalchemy.orm import Session

from app.ai import get_provider
from app.models.case import Case
from app.models.trial import Trial

logger = logging.getLogger(__name__)


def _normalize(text: str) -> str:
    return " ".join((text or "").lower().split())


def embed_trial(db: Session, trial_id: str) -> str | None:
    trial = db.query(Trial).filter(Trial.id == trial_id).first()
    if not trial:
        return None
    parts = [
        trial.trial_action or trial.action_taken or "",
        trial.observation or trial.notes or "",
        trial.outcome.value if trial.outcome else "",
        trial.hypothesis or "",
    ]
    text = _normalize(" | ".join(p for p in parts if p))
    if not text:
        return None
    provider = get_provider()
    vector, source = provider.embed(text)
    trial.embedding = vector
    db.commit()
    logger.info("Knowledge: trial %s embedded via %s", trial_id, source)
    return source


def embed_root_cause(db: Session, case_id: str) -> str | None:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case or not case.confirmed_root_cause:
        return None
    text = _normalize(
        f"{case.confirmed_root_cause} | {case.fatal_error} | {case.model} | {case.process} | {case.symptom or ''}"
    )
    provider = get_provider()
    vector, source = provider.embed(text)
    case.embedding = vector
    db.commit()
    logger.info("Knowledge: root cause for %s embedded via %s", case.case_id, source)
    return source


def embed_why_why(db: Session, why_why_id: str) -> str | None:
    from app.models.why_why import WhyWhy, WhyWhyStatus
    doc = db.query(WhyWhy).filter(WhyWhy.id == why_why_id).first()
    if not doc or doc.status != WhyWhyStatus.APPROVED:
        return None
    content = doc.approved_version or doc.draft or {}
    steps = content.get("why_steps", [])
    chain = " → ".join(s.get("answer", "") for s in steps[:5])
    text = _normalize(
        f"{chain} | {content.get('corrective_action', '')} | {content.get('preventive_action', '')}"
    )
    if not text.strip():
        return None
    provider = get_provider()
    vector, source = provider.embed(text)
    doc.embedding = vector
    db.commit()
    logger.info("Knowledge: why-why %s embedded via %s", why_why_id, source)
    return source


def embed_archived_case(db: Session, case_id: str) -> str | None:
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None
    trials = db.query(Trial).filter(Trial.case_id == case_id).all()
    trial_summary = " ; ".join(
        f"{t.trial_action}:{t.outcome}" for t in trials if t.trial_action
    )
    text = _normalize(
        f"{case.title} | {case.fatal_error} | {case.symptom} | {case.confirmed_root_cause or ''} | {trial_summary}"
    )
    provider = get_provider()
    vector, source = provider.embed(text)
    case.embedding = vector
    db.commit()
    logger.info("Knowledge: archived case %s embedded via %s", case.case_id, source)
    return source

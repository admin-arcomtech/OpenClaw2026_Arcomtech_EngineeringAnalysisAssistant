"""KPI instrumentation for Sprint 5 / PRD §11."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ai_recommendation import AIFeedback
from app.models.case import Case, CaseStatus
from app.models.why_why import WhyWhy, WhyWhyStatus


def compute_kpis(db: Session) -> dict:
    now = datetime.now(timezone.utc)
    since_90d = now - timedelta(days=90)

    confirmed = (
        db.query(Case)
        .filter(Case.confirmed_at.isnot(None))
        .all()
    )
    ttrc_hours = []
    for c in confirmed:
        if c.confirmed_at and c.created_at:
            delta = (c.confirmed_at - c.created_at).total_seconds() / 3600
            ttrc_hours.append(round(delta, 1))
    avg_ttrc = round(sum(ttrc_hours) / len(ttrc_hours), 1) if ttrc_hours else None

    ww_approved = (
        db.query(WhyWhy)
        .filter(WhyWhy.status == WhyWhyStatus.APPROVED, WhyWhy.approved_at.isnot(None))
        .all()
    )
    ww_hours = []
    for w in ww_approved:
        case = db.query(Case).filter(Case.id == w.case_id).first()
        if case and case.confirmed_at and w.approved_at:
            delta = (w.approved_at - case.confirmed_at).total_seconds() / 3600
            ww_hours.append(round(delta, 1))
    avg_ww_time = round(sum(ww_hours) / len(ww_hours), 1) if ww_hours else None

    total_fb = db.query(AIFeedback).count()
    useful_fb = db.query(AIFeedback).filter(AIFeedback.rating == "USEFUL").count()
    ai_usefulness_pct = round(100 * useful_fb / total_fb, 1) if total_fb else None

    archived_count = db.query(Case).filter(Case.status == CaseStatus.ARCHIVED).count()
    indexed_count = db.query(Case).filter(Case.embedding.isnot(None)).count()

    repeat_cases = 0
    pairs = (
        db.query(Case.model, Case.fatal_error, func.count(Case.id))
        .filter(Case.created_at >= since_90d, Case.model.isnot(None), Case.fatal_error.isnot(None))
        .group_by(Case.model, Case.fatal_error)
        .having(func.count(Case.id) > 1)
        .all()
    )
    repeat_cases = sum(p[2] for p in pairs)

    return {
        "avg_time_to_root_cause_hours": avg_ttrc,
        "avg_why_why_creation_hours": avg_ww_time,
        "ai_usefulness_pct": ai_usefulness_pct,
        "total_feedback": total_fb,
        "kb_archived_cases": archived_count,
        "kb_indexed_cases": indexed_count,
        "repeat_abnormality_cases_90d": repeat_cases,
    }

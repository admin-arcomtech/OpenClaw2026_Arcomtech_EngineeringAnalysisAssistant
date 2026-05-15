"""Case timeline aggregator — Sprint 4 §4.7."""
from sqlalchemy.orm import Session, joinedload
from app.models.audit_log import AuditLog
from app.models.case import Case
from app.models.trial import Trial
from app.schemas.trial import TimelineEvent

EVENT_LABELS = {
    "case.created": "Kasus dibuat",
    "case.status_changed": "Status diubah",
    "case.photo_uploaded": "Foto diupload",
    "case.root_cause_confirmed": "Root cause dikonfirmasi",
    "trial.logged": "Trial dicatat",
    "trial_queue.approved": "Trial queue disetujui",
}


def build_timeline(db: Session, case: Case) -> list[TimelineEvent]:
    events: list[TimelineEvent] = []

    events.append(TimelineEvent(
        id=f"case-created-{case.id}",
        event_type="case.created",
        title="Kasus dibuat",
        detail=case.title,
        actor=case.reporter.full_name if case.reporter else None,
        created_at=case.created_at,
    ))

    trials = (
        db.query(Trial)
        .options(joinedload(Trial.performed_by))
        .filter(Trial.case_id == case.id)
        .order_by(Trial.created_at)
        .all()
    )
    for t in trials:
        outcome = t.outcome.value if t.outcome else "logged"
        events.append(TimelineEvent(
            id=f"trial-{t.id}",
            event_type="trial.logged",
            title=f"Trial #{t.sequence}: {outcome}",
            detail=(t.trial_action or t.observation or "")[:200],
            actor=t.performed_by.full_name if t.performed_by else None,
            created_at=t.created_at,
        ))

    logs = (
        db.query(AuditLog)
        .options(joinedload(AuditLog.user))
        .order_by(AuditLog.created_at.asc())
        .all()
    )
    for log in logs:
        detail = log.detail or {}
        cid = detail.get("case_id")
        if cid and cid != case.case_id:
            continue
        if log.event == "case.created":
            continue
        events.append(TimelineEvent(
            id=log.id,
            event_type=log.event,
            title=EVENT_LABELS.get(log.event, log.event.replace(".", " ").title()),
            detail=str({k: v for k, v in detail.items() if k != "case_id"})[:300] if detail else None,
            actor=log.user.full_name if log.user else None,
            created_at=log.created_at,
        ))

    if case.confirmed_at:
        events.append(TimelineEvent(
            id=f"confirm-{case.id}",
            event_type="case.root_cause_confirmed",
            title="Root cause dikonfirmasi",
            detail=case.confirmed_root_cause,
            actor=case.confirmed_by.full_name if case.confirmed_by else None,
            created_at=case.confirmed_at,
        ))

    events.sort(key=lambda e: e.created_at)
    return events

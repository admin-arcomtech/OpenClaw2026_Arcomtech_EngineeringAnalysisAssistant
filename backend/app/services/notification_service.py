"""
Notification stub — Sprint 2: inserts DB record for HIGH/CRITICAL severity cases.
Delivery UI will be implemented in Sprint 5.
"""
import uuid
import logging
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.notification import Notification

logger = logging.getLogger(__name__)


def notify_high_severity(db: Session, case_id: str, case_display_id: str, severity: str) -> None:
    if severity not in ("HIGH", "CRITICAL"):
        return

    seniors = db.query(User).filter(
        User.role.in_([UserRole.SENIOR, UserRole.MANAGER]),
        User.is_active == True,
    ).all()

    for user in seniors:
        notif = Notification(
            id=str(uuid.uuid4()),
            recipient_id=user.id,
            case_id=case_id,
            event="case.high_severity",
            message=f"Kasus {case_display_id} dengan severity {severity} memerlukan perhatian segera.",
        )
        db.add(notif)

    if seniors:
        db.flush()
        logger.info(
            "Notifikasi HIGH/CRITICAL dikirim ke %d user untuk kasus %s",
            len(seniors), case_display_id,
        )


def notify_why_why_pending(db: Session, case_id: str, case_display_id: str) -> None:
    seniors = db.query(User).filter(
        User.role.in_([UserRole.SENIOR, UserRole.MANAGER]),
        User.is_active == True,
    ).all()
    for user in seniors:
        notif = Notification(
            id=str(uuid.uuid4()),
            recipient_id=user.id,
            case_id=case_id,
            event="why_why.pending_approval",
            message=f"Why-Why kasus {case_display_id} menunggu persetujuan Senior.",
        )
        db.add(notif)
    if seniors:
        db.flush()

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    unread_only: bool = False,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Notification).filter(Notification.recipient_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)
    items = q.order_by(Notification.created_at.desc()).limit(limit).all()
    unread = db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False,
    ).count()
    return {
        "items": [
            {
                "id": n.id,
                "event": n.event,
                "message": n.message,
                "case_id": n.case_id,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None,
            }
            for n in items
        ],
        "unread_count": unread,
    }


@router.post("/{notif_id}/read")
def mark_read(
    notif_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    n = db.query(Notification).filter(
        Notification.id == notif_id,
        Notification.recipient_id == current_user.id,
    ).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notifikasi tidak ditemukan")
    n.is_read = True
    db.commit()
    return {"ok": True}


@router.post("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db.query(Notification).filter(
        Notification.recipient_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"ok": True}

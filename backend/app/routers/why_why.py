import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.case import Case, CaseStatus
from app.models.user import User, UserRole
from app.models.why_why import WhyWhy, WhyWhyStatus
from app.schemas.why_why import WhyWhyApproveRequest, WhyWhyOut, WhyWhySubmitRequest, WhyWhyUpdateRequest
from app.services.audit_service import log_event
from app.services.knowledge_service import embed_why_why
from app.services.notification_service import notify_why_why_pending
from app.services.why_why_service import generate_draft

router = APIRouter(prefix="/api/cases", tags=["why-why"])
logger = logging.getLogger(__name__)


def _case_archived_readonly(case: Case) -> bool:
    return case.status == CaseStatus.ARCHIVED


def _to_out(doc: WhyWhy) -> WhyWhyOut:
    return WhyWhyOut(
        id=doc.id,
        case_id=doc.case_id,
        draft=doc.draft,
        approved_version=doc.approved_version,
        status=doc.status.value,
        submitted_at=doc.submitted_at,
        approved_at=doc.approved_at,
        rejection_comment=doc.rejection_comment,
        is_readonly=doc.status == WhyWhyStatus.APPROVED,
    )


def _load_case(db: Session, case_id: str) -> Case:
    case = db.query(Case).filter((Case.id == case_id) | (Case.case_id == case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    return case


@router.get("/{case_id}/why-why", response_model=WhyWhyOut)
def get_why_why(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _load_case(db, case_id)
    doc = db.query(WhyWhy).filter(WhyWhy.case_id == case.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Why-Why belum dibuat untuk kasus ini")
    return _to_out(doc)


@router.put("/{case_id}/why-why", response_model=WhyWhyOut)
def update_why_why(
    case_id: str,
    body: WhyWhyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _load_case(db, case_id)
    if _case_archived_readonly(case):
        raise HTTPException(status_code=403, detail="Kasus diarsipkan — hanya baca")
    doc = db.query(WhyWhy).filter(WhyWhy.case_id == case.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Why-Why belum dibuat")
    if doc.status == WhyWhyStatus.APPROVED:
        raise HTTPException(status_code=403, detail="Why-Why sudah disetujui — hanya baca")
    doc.draft = body.draft
    doc.status = WhyWhyStatus.DRAFT
    doc.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _to_out(doc)


@router.post("/{case_id}/why-why/submit", response_model=WhyWhyOut)
def submit_why_why(
    case_id: str,
    body: WhyWhySubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _load_case(db, case_id)
    if _case_archived_readonly(case):
        raise HTTPException(status_code=403, detail="Kasus diarsipkan — hanya baca")
    doc = db.query(WhyWhy).filter(WhyWhy.case_id == case.id).first()
    if not doc or not doc.draft:
        raise HTTPException(status_code=400, detail="Draft Why-Why kosong")
    if doc.status == WhyWhyStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Sudah disetujui")
    steps = doc.draft.get("why_steps", [])
    if len(steps) < 5:
        raise HTTPException(status_code=400, detail="Minimal 5 level Why diperlukan")
    doc.status = WhyWhyStatus.PENDING_APPROVAL
    doc.submitted_by_id = current_user.id
    doc.submitted_at = datetime.now(timezone.utc)
    notify_why_why_pending(db, case.id, case.case_id)
    log_event(db, event="why_why.submitted", user_id=current_user.id, detail={"case_id": case.case_id})
    db.commit()
    return _to_out(doc)


@router.post("/{case_id}/why-why/approve", response_model=WhyWhyOut)
def approve_why_why(
    case_id: str,
    body: WhyWhyApproveRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.SENIOR, UserRole.MANAGER, UserRole.ADMIN])),
):
    case = _load_case(db, case_id)
    doc = db.query(WhyWhy).filter(WhyWhy.case_id == case.id).first()
    if not doc or doc.status != WhyWhyStatus.PENDING_APPROVAL:
        raise HTTPException(status_code=400, detail="Why-Why tidak dalam status menunggu persetujuan")
    if body.approved:
        doc.status = WhyWhyStatus.APPROVED
        doc.approved_version = doc.draft
        doc.approved_by_id = current_user.id
        doc.approved_at = datetime.now(timezone.utc)
        doc.rejection_comment = None
        log_event(db, event="why_why.approved", user_id=current_user.id, detail={"case_id": case.case_id})
        db.commit()
        background.add_task(embed_why_why, doc.id)
    else:
        doc.status = WhyWhyStatus.REJECTED
        doc.rejection_comment = body.comment or "Ditolak oleh Senior"
        log_event(db, event="why_why.rejected", user_id=current_user.id, detail={"case_id": case.case_id, "comment": body.comment})
        db.commit()
    return _to_out(doc)

import logging
import math
import os
import shutil
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.case import Case, CaseStatus, VALID_TRANSITIONS
from app.models.case_photo import CasePhoto
from app.models.user import User, UserRole
from app.schemas.case import (
    CaseCreateRequest,
    CaseListResponse,
    CaseOut,
    CaseSummary,
    DuplicateWarning,
    StatusUpdateRequest,
)
from app.services.audit_service import log_event
from app.services.case_id import generate_case_id
from app.services.notification_service import notify_high_severity

router = APIRouter(prefix="/api/cases", tags=["cases"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/arcom_uploads")
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_PHOTOS_PER_CASE = 5


def _load_case(db: Session, case_id: str) -> Case:
    case = (
        db.query(Case)
        .options(
            joinedload(Case.reporter),
            joinedload(Case.assigned_to),
            joinedload(Case.photos),
        )
        .filter(Case.id == case_id)
        .first()
    )
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    return case


# ── POST /api/cases ───────────────────────────────────────────────────────────

@router.post("", response_model=CaseOut, status_code=status.HTTP_201_CREATED)
def create_case(
    body: CaseCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assigned_to_id = body.assigned_to_id
    # Junior can only assign to themselves
    if current_user.role == UserRole.JUNIOR:
        assigned_to_id = current_user.id

    # Verify assignee exists
    if assigned_to_id and assigned_to_id != current_user.id:
        if not db.query(User).filter(User.id == assigned_to_id).first():
            raise HTTPException(status_code=400, detail="Investigator tidak ditemukan")

    case_display_id = generate_case_id(db)
    title = f"{body.model} — {body.fatal_error}"

    case = Case(
        id=str(uuid.uuid4()),
        case_id=case_display_id,
        title=title,
        description=body.description,
        model=body.model,
        process=body.process,
        line=body.line,
        fatal_error=body.fatal_error,
        symptom=body.symptom,
        temporary_action=body.temporary_action,
        operator_id=body.operator_id,
        spc_reference=body.spc_reference,
        status=CaseStatus.OPEN,
        severity=body.severity,
        shift=body.shift,
        reporter_id=current_user.id,
        assigned_to_id=assigned_to_id or current_user.id,
    )
    db.add(case)

    notify_high_severity(db, case.id, case_display_id, body.severity.value)

    log_event(
        db,
        event="case.created",
        user_id=current_user.id,
        detail={"case_id": case_display_id, "severity": body.severity.value},
    )
    db.commit()
    db.refresh(case)

    logger.info("Kasus dibuat: %s oleh %s", case_display_id, current_user.employee_id)
    return _load_case(db, case.id)


# ── GET /api/cases ────────────────────────────────────────────────────────────

@router.get("", response_model=CaseListResponse)
def list_cases(
    status: Optional[CaseStatus] = Query(None),
    model: Optional[str] = Query(None),
    process: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Case)
    if status:
        q = q.filter(Case.status == status)
    if model:
        q = q.filter(Case.model.ilike(f"%{model}%"))
    if process:
        q = q.filter(Case.process.ilike(f"%{process}%"))
    if severity:
        q = q.filter(Case.severity == severity)

    total = q.count()
    items = (
        q.order_by(Case.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return CaseListResponse(
        items=[CaseSummary.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


# ── GET /api/cases/:id ────────────────────────────────────────────────────────

@router.get("/{case_id}", response_model=CaseOut)
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = (
        db.query(Case)
        .options(
            joinedload(Case.reporter),
            joinedload(Case.assigned_to),
            joinedload(Case.photos),
        )
        .filter((Case.id == case_id) | (Case.case_id == case_id))
        .first()
    )
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    return case


# ── PATCH /api/cases/:id/status ───────────────────────────────────────────────

@router.patch("/{case_id}/status", response_model=CaseOut)
def update_status(
    case_id: str,
    body: StatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter((Case.id == case_id) | (Case.case_id == case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    allowed = VALID_TRANSITIONS.get(case.status, [])
    if body.status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Transisi dari '{case.status}' ke '{body.status}' tidak diizinkan. Transisi valid: {allowed}",
        )

    old_status = case.status
    case.status = body.status
    case.updated_at = datetime.now(timezone.utc)

    log_event(
        db,
        event="case.status_changed",
        user_id=current_user.id,
        detail={
            "case_id": case.case_id,
            "from": old_status,
            "to": body.status,
            "note": body.note,
        },
    )
    db.commit()
    return _load_case(db, case.id)


# ── GET /api/cases/:id/duplicate-check ───────────────────────────────────────

@router.get("/{case_id}/duplicate-check", response_model=DuplicateWarning)
def duplicate_check(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check for similar cases (same model + fatal_error) in the last 24 hours."""
    case = db.query(Case).filter((Case.id == case_id) | (Case.case_id == case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    dupes = (
        db.query(Case)
        .filter(
            Case.model == case.model,
            Case.fatal_error == case.fatal_error,
            Case.created_at >= since,
            Case.id != case.id,
        )
        .all()
    )
    return DuplicateWarning(has_duplicate=bool(dupes), cases=dupes)


# ── POST /api/cases/check-duplicate (pre-create) ─────────────────────────────

@router.post("/check-duplicate", response_model=DuplicateWarning)
def pre_create_duplicate_check(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    model = body.get("model")
    fatal_error = body.get("fatal_error")
    if not model or not fatal_error:
        return DuplicateWarning(has_duplicate=False)

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    dupes = (
        db.query(Case)
        .filter(
            Case.model == model,
            Case.fatal_error == fatal_error,
            Case.created_at >= since,
        )
        .all()
    )
    return DuplicateWarning(has_duplicate=bool(dupes), cases=dupes)


# ── POST /api/cases/:id/photos ────────────────────────────────────────────────

@router.post("/{case_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_photo(
    case_id: str,
    file: UploadFile = File(...),
    caption: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = db.query(Case).filter((Case.id == case_id) | (Case.case_id == case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")

    # Max photos check
    photo_count = db.query(CasePhoto).filter(CasePhoto.case_id == case.id).count()
    if photo_count >= MAX_PHOTOS_PER_CASE:
        raise HTTPException(
            status_code=400,
            detail=f"Maksimal {MAX_PHOTOS_PER_CASE} foto per kasus.",
        )

    # MIME validation
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME:
        raise HTTPException(
            status_code=415,
            detail="Format file tidak didukung. Gunakan JPG, PNG, atau WebP.",
        )

    # Read and size check
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="Ukuran file melebihi 10MB. Compress dulu sebelum upload.",
        )

    # Save to storage
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    stored_name = f"{uuid.uuid4()}.{ext}"
    storage_path = os.path.join(UPLOAD_DIR, stored_name)
    with open(storage_path, "wb") as f:
        f.write(content)

    photo = CasePhoto(
        id=str(uuid.uuid4()),
        case_id=case.id,
        filename=file.filename or stored_name,
        storage_path=f"/uploads/{stored_name}",
        mime_type=content_type,
        file_size_bytes=len(content),
        uploaded_by_id=current_user.id,
        caption=caption,
    )
    db.add(photo)
    log_event(
        db,
        event="case.photo_uploaded",
        user_id=current_user.id,
        detail={"case_id": case.case_id, "filename": file.filename},
    )
    db.commit()
    db.refresh(photo)
    return photo

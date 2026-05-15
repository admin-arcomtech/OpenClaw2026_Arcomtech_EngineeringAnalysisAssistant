"""
Trial Logging API (F-005) — Sprint 4.
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.dependencies import get_current_user
from app.models.case import Case, CaseStatus
from app.models.trial import Trial, TrialOutcome, TrialResult
from app.models.user import User
from app.schemas.trial import TrialCreateRequest, TrialOut
from app.services.audit_service import log_event
from app.services.knowledge_service import embed_trial

router = APIRouter(tags=["trials"])
logger = logging.getLogger(__name__)

UPLOAD_DIR = __import__("os").environ.get("UPLOAD_DIR", "/tmp/arcom_uploads")
ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
MAX_TRIAL_PHOTOS = 3


def _get_case(db: Session, case_id: str) -> Case:
    case = db.query(Case).filter((Case.id == case_id) | (Case.case_id == case_id)).first()
    if not case:
        raise HTTPException(status_code=404, detail="Kasus tidak ditemukan")
    return case


def _trial_to_out(t: Trial) -> TrialOut:
    return TrialOut(
        id=t.id,
        case_id=t.case_id,
        sequence=t.sequence,
        trial_action=t.trial_action or t.action_taken,
        observation=t.observation,
        outcome=t.outcome.value if t.outcome else None,
        improvement_pct=t.improvement_pct,
        time_spent_min=t.time_spent_min,
        scrap_impact=t.scrap_impact,
        scrap_qty=t.scrap_qty,
        risk_level=t.risk_level,
        destructive=t.destructive or False,
        engineer_comment=t.engineer_comment,
        performed_by_id=t.performed_by_id,
        queue_item_id=t.queue_item_id,
        created_at=t.created_at,
    )


@router.get("/api/cases/{case_id}/trials", response_model=List[TrialOut])
def list_trials(
    case_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _get_case(db, case_id)
    trials = (
        db.query(Trial)
        .filter(Trial.case_id == case.id)
        .order_by(Trial.sequence.asc(), Trial.created_at.asc())
        .all()
    )
    return [_trial_to_out(t) for t in trials]


@router.post("/api/cases/{case_id}/trials", response_model=TrialOut, status_code=status.HTTP_201_CREATED)
def create_trial(
    case_id: str,
    body: TrialCreateRequest,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _get_case(db, case_id)

    # Scrap qty required when scrap_impact indicates scrap
    if body.scrap_impact and body.scrap_impact.upper() in ("YES", "MINOR", "MAJOR") and body.scrap_qty is None:
        raise HTTPException(status_code=400, detail="scrap_qty wajib diisi jika ada dampak scrap")

    # Duplicate warning — same action within 1 hour
    from datetime import timedelta
    since = datetime.now(timezone.utc) - timedelta(hours=1)
    dup = (
        db.query(Trial)
        .filter(
            Trial.case_id == case.id,
            Trial.trial_action == body.trial_action,
            Trial.created_at >= since,
        )
        .first()
    )
    if dup:
        logger.warning("Duplicate trial log for case %s action %s", case.case_id, body.trial_action)

    max_seq = db.query(Trial).filter(Trial.case_id == case.id).count()
    try:
        outcome = TrialOutcome(body.outcome.upper())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"outcome tidak valid: {body.outcome}")

    trial = Trial(
        id=str(uuid.uuid4()),
        case_id=case.id,
        sequence=max_seq + 1,
        trial_action=body.trial_action,
        action_taken=body.trial_action,
        hypothesis=body.hypothesis,
        observation=body.observation,
        outcome=outcome,
        result=_map_outcome_to_result(outcome),
        improvement_pct=body.improvement_pct,
        time_spent_min=body.time_spent_min,
        scrap_impact=body.scrap_impact,
        scrap_qty=body.scrap_qty,
        risk_level=body.risk_level,
        destructive=body.destructive,
        engineer_comment=body.engineer_comment,
        performed_by_id=current_user.id,
        queue_item_id=body.queue_item_id,
    )
    db.add(trial)

    # Auto-advance status on meaningful outcomes
    if outcome in (TrialOutcome.IMPROVED, TrialOutcome.WORSENED):
        if case.status in (CaseStatus.SUSPECTED_CAUSE, CaseStatus.TRIAL_RUNNING, CaseStatus.TRIAL_IN_PROGRESS):
            case.status = CaseStatus.TRIAL_RUNNING
    elif case.status == CaseStatus.SUSPECTED_CAUSE:
        case.status = CaseStatus.TRIAL_RUNNING

    log_event(
        db,
        event="trial.logged",
        user_id=current_user.id,
        detail={
            "case_id": case.case_id,
            "trial_id": trial.id,
            "outcome": outcome.value,
            "duplicate_warning": dup is not None,
        },
    )
    db.commit()
    db.refresh(trial)

    background.add_task(embed_trial, trial.id)

    return _trial_to_out(trial)


@router.post("/api/cases/{case_id}/trials/{trial_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_trial_photo(
    case_id: str,
    trial_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    case = _get_case(db, case_id)
    trial = db.query(Trial).filter(Trial.id == trial_id, Trial.case_id == case.id).first()
    if not trial:
        raise HTTPException(status_code=404, detail="Trial tidak ditemukan")

    existing = json.loads(trial.photo_paths or "[]")
    if len(existing) >= MAX_TRIAL_PHOTOS:
        raise HTTPException(status_code=400, detail=f"Maksimal {MAX_TRIAL_PHOTOS} foto per trial")

    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail="Format file tidak didukung. Gunakan JPG, PNG, atau WebP.")

    import os
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Ukuran file melebihi 10MB. Compress dulu sebelum upload.")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    stored_name = f"trial_{uuid.uuid4()}.{ext}"
    path = os.path.join(UPLOAD_DIR, stored_name)
    with open(path, "wb") as f:
        f.write(content)

    storage_path = f"/uploads/{stored_name}"
    existing.append(storage_path)
    trial.photo_paths = json.dumps(existing)
    db.commit()
    return {"path": storage_path, "count": len(existing)}


def _map_outcome_to_result(outcome: TrialOutcome) -> TrialResult:
    mapping = {
        TrialOutcome.IMPROVED: TrialResult.SUCCESS,
        TrialOutcome.NO_CHANGE: TrialResult.PARTIAL,
        TrialOutcome.WORSENED: TrialResult.FAILED,
        TrialOutcome.INCONCLUSIVE: TrialResult.PENDING,
    }
    return mapping.get(outcome, TrialResult.PENDING)

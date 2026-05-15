import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.audit_log import AuditLog
from app.models.import_job import ImportJob
from app.models.user import User, UserRole
from app.services.import_service import run_import
from app.services.kpi_service import compute_kpis

router = APIRouter(prefix="/api/admin", tags=["admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    employee_id: str
    full_name: str
    email: Optional[str] = None
    division: Optional[str] = None
    role: UserRole = UserRole.JUNIOR
    password: str = "changeme123"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    division: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: str
    employee_id: str
    full_name: str
    email: Optional[str]
    division: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    users = db.query(User).order_by(User.employee_id).all()
    return [
        UserOut(
            id=u.id, employee_id=u.employee_id, full_name=u.full_name,
            email=u.email, division=u.division,
            role=u.role.value, is_active=u.is_active,
        )
        for u in users
    ]


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    body: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    if db.query(User).filter(User.employee_id == body.employee_id).first():
        raise HTTPException(status_code=400, detail="Employee ID sudah terdaftar")
    user = User(
        id=str(uuid.uuid4()),
        employee_id=body.employee_id,
        full_name=body.full_name,
        email=body.email,
        division=body.division,
        role=body.role,
        hashed_password=pwd_context.hash(body.password),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id, employee_id=user.employee_id, full_name=user.full_name,
        email=user.email, division=user.division, role=user.role.value, is_active=user.is_active,
    )


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    body: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.email is not None:
        user.email = body.email
    if body.division is not None:
        user.division = body.division
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id, employee_id=user.employee_id, full_name=user.full_name,
        email=user.email, division=user.division, role=user.role.value, is_active=user.is_active,
    )


@router.get("/audit")
def list_audit(
    event: Optional[str] = None,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    q = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if event:
        q = q.filter(AuditLog.event.contains(event))
    logs = q.limit(limit).all()
    return {
        "items": [
            {
                "id": l.id,
                "event": l.event,
                "user_id": l.user_id,
                "detail": l.detail,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ]
    }


@router.post("/import")
async def batch_import(
    file: UploadFile = File(...),
    dry_run: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    if not file.filename or not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Format harus CSV")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File terlalu besar (max 10MB)")
    job = run_import(db, content, file.filename, current_user.id, dry_run=dry_run)
    return {
        "job_id": job.id,
        "status": job.status,
        "dry_run": job.dry_run,
        "total_rows": job.total_rows,
        "imported_rows": job.imported_rows,
        "skipped_rows": job.skipped_rows,
        "errors": job.error_rows,
    }


@router.get("/import/jobs")
def list_import_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN])),
):
    jobs = db.query(ImportJob).order_by(ImportJob.created_at.desc()).limit(20).all()
    return [
        {
            "id": j.id,
            "filename": j.filename,
            "status": j.status,
            "dry_run": j.dry_run,
            "total_rows": j.total_rows,
            "imported_rows": j.imported_rows,
            "skipped_rows": j.skipped_rows,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in jobs
    ]


@router.get("/kpis")
def admin_kpis(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.MANAGER, UserRole.ADMIN])),
):
    return compute_kpis(db)

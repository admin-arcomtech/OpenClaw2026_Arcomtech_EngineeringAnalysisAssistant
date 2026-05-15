import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut, MessageResponse
from app.services.audit_service import log_event
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_id == body.employee_id).first()
    ip = request.client.host if request.client else None
    ua = request.headers.get("User-Agent")

    if not user or not verify_password(body.password, user.hashed_password):
        log_event(
            db,
            event="auth.login_failed",
            detail={"employee_id": body.employee_id},
            ip_address=ip,
            user_agent=ua,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Employee ID atau password salah",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akun tidak aktif")

    token = create_access_token({"sub": user.id, "role": user.role.value})
    log_event(
        db,
        event="auth.login_success",
        user_id=user.id,
        detail={"employee_id": user.employee_id, "role": user.role.value},
        ip_address=ip,
        user_agent=ua,
    )
    logger.info("Login berhasil: %s (%s)", user.employee_id, user.role.value)
    return TokenResponse(
        access_token=token,
        expires_in_hours=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS,
    )


@router.post("/logout", response_model=MessageResponse)
def logout(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ip = request.client.host if request.client else None
    log_event(
        db,
        event="auth.logout",
        user_id=current_user.id,
        detail={"employee_id": current_user.employee_id},
        ip_address=ip,
    )
    logger.info("Logout: %s", current_user.employee_id)
    return MessageResponse(message="Berhasil logout")


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

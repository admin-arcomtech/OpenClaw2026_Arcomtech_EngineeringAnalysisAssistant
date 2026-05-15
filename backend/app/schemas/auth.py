from pydantic import BaseModel
from app.models.user import UserRole


class LoginRequest(BaseModel):
    employee_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_hours: int


class UserOut(BaseModel):
    id: str
    employee_id: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str

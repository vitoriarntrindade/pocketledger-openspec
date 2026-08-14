from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserOut
from app.services import auth_service

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserOut:
    user = auth_service.register_user(db, payload.name, payload.email, payload.password)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    token = auth_service.authenticate_user(db, payload.email, payload.password)
    return TokenResponse(access_token=token)

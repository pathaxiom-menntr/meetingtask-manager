from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest
from app.schemas.user import UserCreate
from app.services.auth import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login")
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    return AuthService.login(
        db,
        login_data
    )


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    return AuthService.register(
        db,
        user
    )

@router.post("/refresh")
def refresh(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    return AuthService.refresh(
        db,
        request
    )

@router.get("/me")
def me(
    current_user: User = Depends(get_current_user)
):
    return current_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user
from app.core.pagination import PaginationParams
from app.models.user import User
from app.services.user import UserService
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UpdateProfileRequest,
    UpdatePasswordRequest,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/", response_model=list[UserResponse])
def get_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return UserService.get_users(db, current_user.team_code, pagination.skip, pagination.limit)


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.put("/me", response_model=UserResponse)
def update_profile(
    data: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return UserService.update_profile(db, current_user, data)


@router.post("/update-password", status_code=200)
def update_password(
    data: UpdatePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    UserService.update_password(db, current_user, data)
    return {"message": "Password updated successfully"}


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return UserService.get_user_by_id(db, user_id)

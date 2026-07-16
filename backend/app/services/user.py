from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UpdateProfileRequest, UpdatePasswordRequest
from app.core.security import hash_password, verify_password


class UserService:

    @staticmethod
    def create_user(
        db: Session,
        user_data: UserCreate
    ):
        existing_user = (
            db.query(User)
            .filter(User.email == user_data.email)
            .first()
        )

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )


        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hash_password(user_data.password)
)

        try:
            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except Exception:
            db.rollback()
            raise

    @staticmethod
    def get_users(
        db: Session,
        team_code: str,
        skip: int = 0,
        limit: int = 20
    ):
        return (
            db.query(User)
            .filter(User.team_code == team_code)
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_user_by_id(
        db: Session,
        user_id: int
    ):
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return user

    @staticmethod
    def update_profile(
        db: Session,
        current_user: User,
        data: UpdateProfileRequest
    ) -> User:
        current_user.full_name = data.full_name
        db.commit()
        db.refresh(current_user)
        return current_user

    @staticmethod
    def update_password(
        db: Session,
        current_user: User,
        data: UpdatePasswordRequest
    ) -> None:
        if not verify_password(data.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="Current password is incorrect"
            )
        if len(data.new_password) < 6:
            raise HTTPException(
                status_code=422,
                detail="New password must be at least 6 characters"
            )
        current_user.password_hash = hash_password(data.new_password)
        db.commit()
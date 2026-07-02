from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


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
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.auth import LoginRequest, RefreshRequest

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

logger = get_logger(__name__)

class AuthService:

    @staticmethod
    def register(
        db: Session,
        user_data: UserCreate
    ):
        existing_user = (
            db.query(User)
            .filter(
                User.email == user_data.email,
                User.team_code == user_data.team_code
            )
            .first()
        )

        if existing_user:
            logger.warning(
                "Register failed — email already exists in team: %s / %s",
                user_data.email, user_data.team_code
            )
            raise HTTPException(
                status_code=400,
                detail="Email already registered in this team"
            )

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            team_code=user_data.team_code
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info("User registered: id=%s email=%s", user.id, user.email)
        return user

    @staticmethod
    def login(
        db: Session,
        login_data: LoginRequest
    ):
        user = (
            db.query(User)
            .filter(
                User.email == login_data.email,
                User.team_code == login_data.team_code
            )
            .first()
        )

        if not user:
            logger.warning(
                "Login failed — user not found: %s / team: %s",
                login_data.email, login_data.team_code
            )
            raise HTTPException(
                status_code=401,
                detail="Invalid email, team code, or password"
            )

        if not verify_password(
            login_data.password,
            user.password_hash
        ):
            logger.warning("Login failed — wrong password: %s", login_data.email)
            raise HTTPException(
                status_code=401,
                detail="Invalid email, team code, or password"
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        logger.info("User logged in: id=%s email=%s", user.id, user.email)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def refresh(
        db: Session,
        request: RefreshRequest
    ):
        payload = decode_refresh_token(
            request.refresh_token
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id)
            }
        )

        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id)
            }
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_current_user(
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
import hashlib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.core.config import settings
from app.models.user import User
from app.models.refresh_token import RefreshToken
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


def _hash_token(token: str) -> str:
    """Return SHA-256 hex digest of a raw JWT string."""
    return hashlib.sha256(token.encode()).hexdigest()


def _store_refresh_token(db: Session, user_id: int, token: str) -> None:
    """Persist a new refresh token record (hashed) to the DB."""
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    record = RefreshToken(
        token_hash=_hash_token(token),
        user_id=user_id,
        is_revoked=False,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()


def _revoke_refresh_token(db: Session, token: str) -> None:
    """Mark a stored refresh token as revoked."""
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == _hash_token(token))
        .first()
    )
    if record:
        record.is_revoked = True
        db.commit()


def _validate_refresh_token(db: Session, token: str) -> None:
    """
    Raise 401 if the token is not in the DB, already revoked, or expired.
    """
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == _hash_token(token))
        .first()
    )
    if not record:
        raise HTTPException(status_code=401, detail="Refresh token not recognised")
    if record.is_revoked:
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")
    if record.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token has expired")


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

        if not verify_password(login_data.password, user.password_hash):
            logger.warning("Login failed — wrong password: %s", login_data.email)
            raise HTTPException(
                status_code=401,
                detail="Invalid email, team code, or password"
            )

        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        # Store refresh token hash so it can be revoked later
        _store_refresh_token(db, user.id, refresh_token)

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
        # 1. Decode & verify the JWT signature / expiry
        payload = decode_refresh_token(request.refresh_token)

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # 2. Verify the token is in our DB and hasn't been revoked
        _validate_refresh_token(db, request.refresh_token)

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 3. Rotate — revoke old token, issue a fresh pair
        _revoke_refresh_token(db, request.refresh_token)

        access_token = create_access_token(data={"sub": str(user.id)})
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

        _store_refresh_token(db, user.id, new_refresh_token)

        logger.info("Token rotated: user_id=%s", user.id)
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def logout(
        db: Session,
        refresh_token: str
    ):
        """Revoke the provided refresh token so it can no longer be used."""
        _revoke_refresh_token(db, refresh_token)
        logger.info("Refresh token revoked on logout")
        return {"message": "Logged out successfully"}

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
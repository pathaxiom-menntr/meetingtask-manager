from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func

from app.db.database import Base


class RefreshToken(Base):
    """
    Stores issued refresh tokens so they can be individually revoked.
    On every /auth/refresh call the old token is revoked and a new one is issued
    (token rotation) — this limits the damage of a stolen refresh token.
    """
    __tablename__ = "refresh_tokens"

    __table_args__ = (
        Index("ix_refresh_tokens_token_hash", "token_hash"),
        Index("ix_refresh_tokens_user_id", "user_id"),
    )

    id = Column(Integer, primary_key=True)

    # We store the SHA-256 hash of the token, not the raw JWT, so a DB leak
    # cannot be used to directly impersonate users.
    token_hash = Column(String(64), nullable=False, unique=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    is_revoked = Column(Boolean, nullable=False, default=False)

    expires_at = Column(TIMESTAMP, nullable=False)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

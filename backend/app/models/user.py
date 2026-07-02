from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, UniqueConstraint
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("email", "team_code", name="uq_users_email_team_code"),
    )

    id = Column(Integer, primary_key=True)

    full_name = Column(
        String(100),
        nullable=False
    )

    password_hash = Column(
        Text,
        nullable=False
    )

    email = Column(
        String(255),
        nullable=False      # unique=True removed — uniqueness now enforced by (email, team_code)
    )

    team_code = Column(
        String(50),
        nullable=False,
        server_default="default",
        index=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    ForeignKey
)
from sqlalchemy.sql import func

from app.db.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(Text)

    status = Column(
        String(20),
        nullable=False,
        default="pending"
    )

    assignee_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    assigned_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    meeting_id = Column(
        Integer,
        ForeignKey("meetings.id"),
        nullable=True
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

    completed_at = Column(
        TIMESTAMP,
        nullable=True
    )
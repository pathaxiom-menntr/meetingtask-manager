from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    TIMESTAMP,
    ForeignKey
)
from sqlalchemy.sql import func

from app.db.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)

    # e.g. "task_assigned", "task_completed"
    type = Column(String(50), nullable=False, default="task_assigned")

    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True
    )

    is_read = Column(Boolean, nullable=False, default=False)

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )

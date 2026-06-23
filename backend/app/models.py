from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    transcript = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text)

    status = Column(String(20), default="pending")

    assignee_id = Column(Integer, ForeignKey("users.id"))
    assigned_by = Column(Integer, ForeignKey("users.id"))
    meeting_id = Column(Integer, ForeignKey("meetings.id"))

    created_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP)
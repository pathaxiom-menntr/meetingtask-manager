from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

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
    unique=True,
    nullable=False
)

    

    created_at = Column(
        TIMESTAMP,
        server_default=func.now()
    )
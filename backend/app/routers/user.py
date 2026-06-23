from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserCreate

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/")
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    db_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=user.password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
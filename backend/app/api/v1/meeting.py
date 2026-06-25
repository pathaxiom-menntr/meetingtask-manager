from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User

from app.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse
)

from app.services.meeting import MeetingService


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"]
)


@router.post(
    "/",
    response_model=MeetingResponse
)
def create_meeting(
    meeting: MeetingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MeetingService.create_meeting(
        db,
        meeting,
        current_user
    )


@router.get(
    "/",
    response_model=list[MeetingResponse]
)
def get_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MeetingService.get_meetings(db)


@router.get(
    "/{meeting_id}",
    response_model=MeetingResponse
)
def get_meeting_by_id(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MeetingService.get_meeting_by_id(
        db,
        meeting_id
    )
    
@router.put(
    "/{meeting_id}",
    response_model=MeetingResponse
)
def update_meeting(
    meeting_id: int,
    meeting_data: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MeetingService.update_meeting(
        db,
        meeting_id,
        meeting_data,
        current_user
    )
    
@router.delete(
    "/{meeting_id}",
    response_model=dict
)
def delete_meeting(
    meeting_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MeetingService.delete_meeting(
        db,
        meeting_id,
        current_user
    )   

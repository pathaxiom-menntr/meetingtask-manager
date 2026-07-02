from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File
)
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.pagination import PaginationParams
from app.db.database import get_db

from app.models.user import User

from app.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate,
    MeetingResponse
)

from app.services.meeting import MeetingService
from app.utils.transcript import extract_text
from app.schemas.meeting_ai import MeetingUploadResponse
from app.services.ai import AIService
from app.services.task import TaskService




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
        db=db,
        title=meeting.title,
        transcript=meeting.transcript,
        current_user=current_user
    )


@router.post(
    "/upload",
    response_model=MeetingUploadResponse,
    status_code=201
)
def upload_transcript(
    title: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Step 1: Extract transcript
    transcript = extract_text(file)

    # Step 2: Save meeting
    meeting = MeetingService.create_meeting(
        db=db,
        title=title,
        transcript=transcript,
        current_user=current_user
    )

    # Step 3: Generate AI tasks
    ai_tasks = AIService.generate_tasks(transcript)

    # Step 4: Save generated tasks
    result = TaskService.create_ai_tasks(
        db=db,
        meeting_id=meeting.id,
        ai_tasks=ai_tasks,
        current_user=current_user
    )

    # Step 5: Return everything
    return {
        "meeting": meeting,
        "tasks": result["created"],
        "skipped": result["skipped"],
        "auto_assigned_tasks": result["auto_assigned_tasks"],
    }

@router.get(
    "/",
    response_model=list[MeetingResponse]
)
def get_meetings(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return MeetingService.get_meetings(db, current_user, pagination.skip, pagination.limit)


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
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.user import User

from app.schemas.meeting import (
    MeetingCreate,
    MeetingUpdate
)

class MeetingService:

    @staticmethod
    def create_meeting(
        db: Session,
        meeting_data: MeetingCreate,
        current_user: User
):
        meeting = Meeting(
            title=meeting_data.title,
            transcript=meeting_data.transcript,
            uploaded_by=current_user.id
    )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        return meeting
    
    @staticmethod
    def get_meetings(
        db: Session
    ):
        return db.query(Meeting).all()
    
    @staticmethod
    def get_meeting_by_id(
        db: Session,
        meeting_id: int
    ):
        print("DEBUG MEETING ID:", meeting_id)

        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )



        print("DEBUG MEETING:", meeting)

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found"
            )

        return meeting
    
    @staticmethod
    def update_meeting(
        db: Session,
        meeting_id: int,
        meeting_data: MeetingUpdate,
        current_user: User
):
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
    )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found"
        )

    # Only the creator can update
        if meeting.uploaded_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the meeting creator can update this meeting"
        )

        if meeting_data.title is not None:
            meeting.title = meeting_data.title

        if meeting_data.transcript is not None:
            meeting.transcript = meeting_data.transcript

        db.commit()
        db.refresh(meeting)

        return meeting
    
    @staticmethod
    def delete_meeting(
        db: Session,
        meeting_id: int,
        current_user: User
):
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
    )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found"
        )

    # Only the creator can delete
        if meeting.uploaded_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the meeting creator can delete this meeting"
        )

        db.delete(meeting)
        db.commit()

        return {
            "message": "Meeting deleted successfully"
    }
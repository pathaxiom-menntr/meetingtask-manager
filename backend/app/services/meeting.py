from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.meeting import Meeting
from app.models.user import User

from app.schemas.meeting import (
    MeetingUpdate
)

logger = get_logger(__name__)



class MeetingService:

    @staticmethod
    def create_meeting(
        db: Session,
        title: str,
        transcript: str,
        current_user: User
    ):
        """
        Create a new meeting.
        Used by:
        - Manual meeting creation
        - Transcript upload
        - Future audio transcription
        """

        meeting = Meeting(
            title=title,
            transcript=transcript,
            uploaded_by=current_user.id
        )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        logger.info("Meeting created: id=%s title=%r user_id=%s", meeting.id, meeting.title, current_user.id)
        return meeting

    @staticmethod
    def get_meetings(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20
    ):
        return (
            db.query(Meeting)
            .filter(Meeting.uploaded_by == current_user.id)
            .order_by(Meeting.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_meeting_by_id(
        db: Session,
        meeting_id: int,
        current_user: User
    ):
        meeting = (
            db.query(Meeting)
            .join(User, User.id == Meeting.uploaded_by)
            .filter(
                Meeting.id == meeting_id,
                User.team_code == current_user.team_code
            )
            .first()
        )

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
        meeting = MeetingService.get_meeting_by_id(db, meeting_id, current_user)

        # Only creator can update
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

        logger.info("Meeting updated: id=%s user_id=%s", meeting_id, current_user.id)
        return meeting

    @staticmethod
    def delete_meeting(
        db: Session,
        meeting_id: int,
        current_user: User
    ):
        meeting = MeetingService.get_meeting_by_id(db, meeting_id, current_user)

        # Only creator can delete
        if meeting.uploaded_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the meeting creator can delete this meeting"
            )

        db.delete(meeting)
        db.commit()

        logger.info("Meeting deleted: id=%s user_id=%s", meeting_id, current_user.id)
        return {
            "message": "Meeting deleted successfully"
        }
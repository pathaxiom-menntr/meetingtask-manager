from pydantic import BaseModel

from app.schemas.meeting import MeetingResponse
from app.schemas.task import TaskResponse


class SkippedTask(BaseModel):
    title: str | None = None
    assignee_name: str | None = None
    reason: str


class MeetingUploadResponse(BaseModel):
    meeting: MeetingResponse
    tasks: list[TaskResponse]
    skipped: list[SkippedTask]
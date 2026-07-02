from pydantic import BaseModel

from app.schemas.meeting import MeetingResponse
from app.schemas.task import TaskResponse


class SkippedTask(BaseModel):
    title: str | None = None
    assignee_name: str | None = None
    reason: str
    auto_assigned: bool = False
    auto_assigned_to: str | None = None


class AutoAssignedTask(BaseModel):
    """A task that was created but whose assignee was chosen automatically."""
    task: TaskResponse
    auto_assigned: bool
    auto_assigned_to: str | None = None


class MeetingUploadResponse(BaseModel):
    meeting: MeetingResponse
    tasks: list[TaskResponse]
    skipped: list[SkippedTask]
    auto_assigned_tasks: list[AutoAssignedTask] = []
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: str
    assignee_id: int
    assigned_by: int
    meeting_id: int


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    assignee_id: int
    assigned_by: int
    meeting_id: int
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True
        
class TaskUpdate(BaseModel):
    title: str
    description: str
    assignee_id: int
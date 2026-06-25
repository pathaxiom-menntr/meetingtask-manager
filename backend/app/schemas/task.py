from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int 
    meeting_id: int | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    assignee_id: int
    assigned_by: int
    meeting_id: int | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True
        

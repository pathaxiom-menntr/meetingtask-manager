from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int 
    meeting_id: int | None = None
    priority: str = "medium"
    due_date: str | None = None  # ISO date string e.g. "2025-07-01"

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    priority: str | None = None
    due_date: str | None = None
    
class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    status: str
    priority: str
    assignee_id: int
    assigned_by: int
    meeting_id: int | None
    due_date: date | None
    created_at: datetime
    completed_at: datetime | None

    class Config:
        from_attributes = True
        

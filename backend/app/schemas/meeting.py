from pydantic import BaseModel
from datetime import datetime


class MeetingCreate(BaseModel):
    title: str
    transcript: str
    
class MeetingUpdate(BaseModel):
    title: str | None = None
    transcript: str | None = None


class MeetingResponse(BaseModel):
    id: int
    title: str
    transcript: str
    uploaded_by: int
    created_at: datetime

    class Config:
        from_attributes = True
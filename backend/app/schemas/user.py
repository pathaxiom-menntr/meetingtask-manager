from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    team_code: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    team_code: str

    class Config:
        from_attributes = True

from fastapi import FastAPI

from app.api.v1.user import router as user_router
from app.api.v1.auth import router as auth_router
from app.api.v1.meeting import router as meeting_router
from app.api.v1.task import router as task_router

app = FastAPI(
    title="Meeting Task Manager API"
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(meeting_router)
app.include_router(task_router)


@app.get("/")
def root():
    return {
        "message": "Meeting Task Manager API Running"
    }
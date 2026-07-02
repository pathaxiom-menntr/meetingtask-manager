from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import get_logger
from app.db.database import engine, Base

# Import all models so SQLAlchemy registers them before create_all
import app.models.user          # noqa: F401
import app.models.meeting       # noqa: F401
import app.models.task          # noqa: F401
import app.models.notification  # noqa: F401

from app.api.v1.user import router as user_router
from app.api.v1.auth import router as auth_router
from app.api.v1.meeting import router as meeting_router
from app.api.v1.task import router as task_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.notification import router as notification_router

app = FastAPI(
    title="Meeting Task Manager API"
)

logger = get_logger(__name__)

# Allow frontend dev servers to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",# React / Next.js
        "http://localhost:5173",   # Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(auth_router)
app.include_router(meeting_router)
app.include_router(task_router)
app.include_router(dashboard_router)
app.include_router(notification_router)


@app.get("/")
def root():
    return {
        "message": "Meeting Task Manager API Running"
    }


@app.on_event("startup")
def on_startup():
    # Create any missing tables (safe — skips tables that already exist)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")
    logger.info("Meeting Task Manager API started")
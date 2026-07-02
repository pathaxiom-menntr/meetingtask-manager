from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logger import get_logger
from app.core.config import settings

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

# Parse allowed origins from config (comma-separated in .env for production)
_raw_origins = getattr(settings, "ALLOWED_ORIGINS", None)
if _raw_origins:
    allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
else:
    # Development fallback
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
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
    # Schema is managed exclusively by Alembic migrations.
    # Do NOT call Base.metadata.create_all() here — it bypasses migration history.
    logger.info("Meeting Task Manager API started")
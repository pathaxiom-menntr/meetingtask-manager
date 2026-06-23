from fastapi import FastAPI
from app.routers.user import router as user_router

app = FastAPI(
    title="Meeting Task Manager API"
)

app.include_router(user_router)


@app.get("/")
def root():
    return {
        "message": "Meeting Task Manager API Running"
    }
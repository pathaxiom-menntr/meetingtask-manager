from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.task import (
    TaskCreate,
    TaskResponse,
    TaskUpdate
)

from app.services.task import TaskService


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)


@router.post(
    "/",
    response_model=TaskResponse
)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    return TaskService.create_task(
        db,
        task
    )


@router.get(
    "/",
    response_model=list[TaskResponse]
)
def get_tasks(
    db: Session = Depends(get_db)
):
    return TaskService.get_tasks(db)


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db)
):
    return TaskService.get_task_by_id(
        db,
        task_id
    )

@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse
)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    return TaskService.complete_task(
        db,
        task_id
    )
    
@router.get(
    "/user/{user_id}",
    response_model=list[TaskResponse]
)
def get_tasks_by_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    return TaskService.get_tasks_by_user(
        db,
        user_id
    )
    
@router.get(
    "/meeting/{meeting_id}",
    response_model=list[TaskResponse]
)
def get_tasks_by_meeting(
    meeting_id: int,
    db: Session = Depends(get_db)
):
    return TaskService.get_tasks_by_meeting(
        db,
        meeting_id
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    return TaskService.update_task(
        db,
        task_id,
        task_data
    )

@router.delete(
    "/{task_id}",
    response_model=dict
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    return TaskService.delete_task(
        db,
        task_id
    )
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.core.pagination import PaginationParams
from app.db.database import get_db

from app.models.user import User

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.create_task(
        db,
        task,
        current_user
    )


@router.get(
    "/",
    response_model=list[TaskResponse]
)
def get_tasks(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.get_tasks(db, current_user, pagination.skip, pagination.limit)


@router.get(
    "/{task_id}",
    response_model=TaskResponse
)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.get_task_by_id(
        db,
        task_id,
        current_user
    )


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse
)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.complete_task(
        db,
        task_id,
        current_user
    )


@router.get(
    "/user/{user_id}",
    response_model=list[TaskResponse]
)
def get_tasks_by_user(
    user_id: int,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.get_tasks_by_user(db, user_id, current_user, pagination.skip, pagination.limit)


@router.get(
    "/meeting/{meeting_id}",
    response_model=list[TaskResponse]
)
def get_tasks_by_meeting(
    meeting_id: int,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.get_tasks_by_meeting(db, meeting_id, current_user, pagination.skip, pagination.limit)


@router.put(
    "/{task_id}",
    response_model=TaskResponse
)
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.update_task(
        db,
        task_id,
        task_data,
        current_user
    )


@router.delete(
    "/{task_id}",
    response_model=dict
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return TaskService.delete_task(
        db,
        task_id,
        current_user
    )
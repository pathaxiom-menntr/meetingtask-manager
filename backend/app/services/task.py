from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:

    @staticmethod
    def create_task(
        db: Session,
        task_data: TaskCreate,
        current_user: User
    ):
        assignee = (
            db.query(User)
            .filter(User.id == task_data.assignee_id)
            .first()
        )

        if not assignee:
            raise HTTPException(
                status_code=404,
                detail="Assignee not found"
            )

        if task_data.meeting_id is not None:
            meeting = (
                db.query(Meeting)
                .filter(Meeting.id == task_data.meeting_id)
                .first()
            )

            if not meeting:
                raise HTTPException(
                    status_code=404,
                    detail="Meeting not found"
                )

        task = Task(
            title=task_data.title,
            description=task_data.description,
            status="pending",
            assignee_id=task_data.assignee_id,
            assigned_by=current_user.id,
            meeting_id=task_data.meeting_id
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def get_tasks(
        db: Session
    ):
        return db.query(Task).all()

    @staticmethod
    def get_task_by_id(
        db: Session,
        task_id: int
    ):
        task = (
            db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        return task

    @staticmethod
    def get_tasks_by_user(
        db: Session,
        user_id: int
    ):
        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        return (
            db.query(Task)
            .filter(Task.assignee_id == user_id)
            .all()
        )

    @staticmethod
    def get_tasks_by_meeting(
        db: Session,
        meeting_id: int
    ):
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found"
            )

        return (
            db.query(Task)
            .filter(Task.meeting_id == meeting_id)
            .all()
        )

    @staticmethod
    def complete_task(
        db: Session,
        task_id: int,
        current_user: User
    ):
        task = (
            db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Only the assignee can complete the task
        if task.assignee_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only complete your own tasks"
            )

        task.status = "completed"
        task.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        task_data: TaskUpdate,
        current_user: User
    ):
        task = (
            db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Only assigner or assignee can update
        if (
            task.assigned_by != current_user.id
            and task.assignee_id != current_user.id
        ):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to update this task"
            )

        if task_data.title is not None:
            task.title = task_data.title

        if task_data.description is not None:
            task.description = task_data.description

        if task_data.assignee_id is not None:
            assignee = (
                db.query(User)
                .filter(User.id == task_data.assignee_id)
                .first()
            )

            if not assignee:
                raise HTTPException(
                    status_code=404,
                    detail="Assignee not found"
                )

            task.assignee_id = task_data.assignee_id

        db.commit()
        db.refresh(task)

        return task

    @staticmethod
    def delete_task(
        db: Session,
        task_id: int,
        current_user: User
    ):
        task = (
            db.query(Task)
            .filter(Task.id == task_id)
            .first()
        )

        if not task:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        # Only assigner can delete
        if task.assigned_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only the assigner can delete this task"
            )

        db.delete(task)
        db.commit()

        return {
            "message": "Task deleted successfully"
        }
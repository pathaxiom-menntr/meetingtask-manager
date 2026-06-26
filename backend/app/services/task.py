from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.meeting import Meeting
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate

logger = get_logger(__name__)



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

        logger.info(
            "Task created: id=%s title=%r assignee_id=%s assigned_by=%s meeting_id=%s",
            task.id, task.title, task.assignee_id, task.assigned_by, task.meeting_id
        )
        return task

    @staticmethod
    def get_tasks(
        db: Session,
        current_user: User,
        skip: int = 0,
        limit: int = 20
    ):
        return (
            db.query(Task)
            .filter(Task.assignee_id == current_user.id)
            .offset(skip)
            .limit(limit)
            .all()
        )

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
        user_id: int,
        skip: int = 0,
        limit: int = 20
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
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_tasks_by_meeting(
        db: Session,
        meeting_id: int,
        skip: int = 0,
        limit: int = 20
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
            .offset(skip)
            .limit(limit)
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

        # Prevent re-completing an already completed task
        if task.status == "completed":
            raise HTTPException(
                status_code=400,
                detail="Task is already completed"
            )

        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(task)

        logger.info("Task completed: id=%s user_id=%s", task_id, current_user.id)
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

        logger.info("Task updated: id=%s user_id=%s", task_id, current_user.id)
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

        logger.info("Task deleted: id=%s user_id=%s", task_id, current_user.id)
        return {
            "message": "Task deleted successfully"
        }
    
    @staticmethod
    def create_ai_tasks(
        db: Session,
        meeting_id: int,
        ai_tasks: list[dict],
        current_user: User
    ):
        """
        Create tasks generated by Azure OpenAI.
    
        Returns:
        {
            "created": [...],
            "skipped": [...]
        }
        """
    
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
    
        created_tasks = []
        skipped_tasks = []
    
        for ai_task in ai_tasks:
        
            title = ai_task.get("title")
            description = ai_task.get("description")
    
            # Supports both "assignee_name" and "assignee"
            assignee_name = (
                ai_task.get("assignee_name")
                or ai_task.get("assignee")
            )
    
            # Skip tasks without a title
            if not title:
                skipped_tasks.append(
                    {
                        "title": None,
                        "assignee_name": assignee_name,
                        "reason": "Task title missing"
                    }
                )
                continue
            
            # Skip if GPT couldn't determine the assignee
            if not assignee_name:
                skipped_tasks.append(
                    {
                        "title": title,
                        "assignee_name": None,
                        "reason": "No assignee found"
                    }
                )
                continue
            
            # Case-insensitive user lookup using full_name
            assignee = (
                db.query(User)
                .filter(User.full_name.ilike(f"%{assignee_name}%"))
                .first()
            )
    
            if not assignee:
                skipped_tasks.append(
                    {
                        "title": title,
                        "assignee_name": assignee_name,
                        "reason": "User not found"
                    }
                )
                continue
            
            task = Task(
                title=title,
                description=description,
                status="pending",
                assignee_id=assignee.id,
                assigned_by=current_user.id,
                meeting_id=meeting_id
            )
    
            db.add(task)
            created_tasks.append(task)
    
        # Commit all created tasks together
        db.commit()
    
        # Refresh to get generated IDs and timestamps
        for task in created_tasks:
            db.refresh(task)

        logger.info(
            "AI tasks for meeting_id=%s: %s created, %s skipped",
            meeting_id, len(created_tasks), len(skipped_tasks)
        )
        for s in skipped_tasks:
            logger.warning(
                "AI task skipped — reason=%r title=%r assignee=%r",
                s["reason"], s["title"], s["assignee_name"]
            )
    
        return {
            "created": created_tasks,
            "skipped": skipped_tasks

        }
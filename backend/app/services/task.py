from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.logger import get_logger
from app.models.meeting import Meeting
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.services.notification import NotificationService

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

        from datetime import date as date_type
        due = None
        if task_data.due_date:
            try:
                due = date_type.fromisoformat(task_data.due_date)
            except ValueError:
                pass

        task = Task(
            title=task_data.title,
            description=task_data.description,
            status="pending",
            priority=task_data.priority or "medium",
            assignee_id=task_data.assignee_id,
            assigned_by=current_user.id,
            meeting_id=task_data.meeting_id,
            due_date=due
        )

        db.add(task)
        db.commit()
        db.refresh(task)

        # Always notify the assignee
        assigner_name = current_user.full_name or "Someone"
        if task.assignee_id == current_user.id:
            notif_title = "You assigned a task to yourself"
            notif_msg = f"You created: \"{task.title}\""
        else:
            notif_title = "New task assigned to you"
            notif_msg = f"{assigner_name} assigned you: \"{task.title}\""

        NotificationService.create(
            db,
            user_id=task.assignee_id,
            title=notif_title,
            message=notif_msg,
            type="task_assigned",
            task_id=task.id
        )

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
            .filter(
                (Task.assignee_id == current_user.id)
                | (Task.assigned_by == current_user.id)
            )
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
                detail="Only the assignee can mark this task as complete"
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

        if task_data.priority is not None:
            task.priority = task_data.priority

        if task_data.due_date is not None:
            from datetime import date as date_type
            try:
                task.due_date = date_type.fromisoformat(task_data.due_date)
            except ValueError:
                pass

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
            
            from datetime import date as date_type
            priority = ai_task.get("priority", "medium") or "medium"
            if priority not in ("low", "medium", "high", "critical"):
                priority = "medium"

            due_date_raw = ai_task.get("due_date")
            due_date = None
            if due_date_raw:
                try:
                    due_date = date_type.fromisoformat(due_date_raw)
                except (ValueError, TypeError):
                    pass

            task = Task(
                title=title,
                description=description,
                status="pending",
                priority=priority,
                assignee_id=assignee.id,
                assigned_by=current_user.id,
                meeting_id=meeting_id,
                due_date=due_date
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

        # Send one notification per unique assignee (skip self-assignments)
        assigner_name = current_user.full_name or "Someone"
        notified_users: set[int] = set()
        for task in created_tasks:
            if task.assignee_id != current_user.id and task.assignee_id not in notified_users:
                task_count = sum(1 for t in created_tasks if t.assignee_id == task.assignee_id)
                NotificationService.create(
                    db,
                    user_id=task.assignee_id,
                    title=f"{task_count} task{'s' if task_count > 1 else ''} assigned to you",
                    message=f"{assigner_name} assigned you {task_count} task{'s' if task_count > 1 else ''} from a meeting.",
                    type="task_assigned",
                    task_id=task.id
                )
                notified_users.add(task.assignee_id)
    
        return {
            "created": created_tasks,
            "skipped": skipped_tasks

        }
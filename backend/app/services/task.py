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
            .filter(
                User.id == task_data.assignee_id,
                User.team_code == current_user.team_code
            )
            .first()
        )

        if not assignee:
            raise HTTPException(
                status_code=404,
                detail="Assignee not found or not in your team"
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

        # Notify the assignee only when it's a different person from the assigner
        if task.assignee_id != current_user.id:
            NotificationService.create(
                db,
                user_id=task.assignee_id,
                title="New task assigned to you",
                message=f"{current_user.full_name or 'Someone'} assigned you: \"{task.title}\"",
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
        task_id: int,
        current_user: User
    ):
        # Join to users table on assignee to verify the task belongs to this team
        task = (
            db.query(Task)
            .join(User, User.id == Task.assignee_id)
            .filter(
                Task.id == task_id,
                User.team_code == current_user.team_code
            )
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
        current_user: User,
        skip: int = 0,
        limit: int = 20
    ):
        # Ensure the requested user belongs to the same team
        user = (
            db.query(User)
            .filter(
                User.id == user_id,
                User.team_code == current_user.team_code
            )
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
        current_user: User,
        skip: int = 0,
        limit: int = 20
    ):
        # Verify the meeting belongs to this team
        from app.models.meeting import Meeting as MeetingModel
        meeting = (
            db.query(MeetingModel)
            .join(User, User.id == MeetingModel.uploaded_by)
            .filter(
                MeetingModel.id == meeting_id,
                User.team_code == current_user.team_code
            )
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
                .filter(
                    User.id == task_data.assignee_id,
                    User.team_code == current_user.team_code
                )
                .first()
            )

            if not assignee:
                raise HTTPException(
                    status_code=404,
                    detail="Assignee not found or not in your team"
                )

            old_assignee_id = task.assignee_id
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

        # Notify new assignee if assignee was changed (and it's a different person)
        if task_data.assignee_id is not None and task_data.assignee_id != old_assignee_id:
            if task.assignee_id != current_user.id:
                NotificationService.create(
                    db,
                    user_id=task.assignee_id,
                    title="Task reassigned to you",
                    message=f"{current_user.full_name or 'Someone'} reassigned you: \"{task.title}\"",
                    type="task_assigned",
                    task_id=task.id
                )

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
    def _get_least_loaded_user(db: Session, team_code: str) -> User | None:
        """
        Return the team member with the fewest pending tasks.
        Only considers users belonging to the given team_code.
        """
        from sqlalchemy import func

        counts = (
            db.query(User.id, func.count(Task.id).label("task_count"))
            .filter(User.team_code == team_code)          # ← team-scoped
            .outerjoin(Task, (Task.assignee_id == User.id) & (Task.status == "pending"))
            .group_by(User.id)
            .order_by(func.count(Task.id).asc())
            .first()
        )

        if not counts:
            return None

        return db.query(User).filter(User.id == counts[0]).first()

    @staticmethod
    def create_ai_tasks(
        db: Session,
        meeting_id: int,
        ai_tasks: list[dict],
        current_user: User
    ):
        """
        Create tasks generated by Azure OpenAI.

        When no assignee can be resolved from the transcript, the task is
        automatically assigned to the team member who currently has the fewest
        pending tasks.  The response includes an ``auto_assigned`` flag so the
        frontend can surface an informational notice.
    
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

        if not ai_tasks:
            ai_tasks = []
    
        created_tasks = []
        skipped_tasks = []
        # Keeps (task, auto_assigned_to_name) pairs for tasks that were
        # auto-assigned so we can attach the right notice later.
        auto_assigned_info: dict[int, str] = {}  # index in created_tasks -> user name

        from datetime import date as date_type
    
        for ai_task in ai_tasks:
        
            title = ai_task.get("title")
            description = ai_task.get("description")
    
            # Supports both "assignee_name" and "assignee"
            assignee_name = (
                ai_task.get("assignee_name")
                or ai_task.get("assignee")
            )
            
            assigner_name = (
                ai_task.get("assigner_name")
                or ai_task.get("assigner")
            )
    
            # Skip tasks without a title — we can't do anything useful here
            if not title:
                skipped_tasks.append(
                    {
                        "title": None,
                        "assignee_name": assignee_name,
                        "reason": "Task title missing",
                        "auto_assigned": False,
                        "auto_assigned_to": None,
                    }
                )
                continue

            assignee = None
            auto_assigned = False

            if assignee_name:
                # Case-insensitive user lookup using full_name
                assignee = (
                    db.query(User)
                    .filter(User.full_name.ilike(f"%{assignee_name}%"))
                    .first()
                )

            # If we still have no assignee (name missing OR user not in DB),
            # fall back to the least-loaded team member.
            if not assignee:
                assignee = TaskService._get_least_loaded_user(db, current_user.team_code)
                auto_assigned = True

            # If there are genuinely no users in the system, skip.
            if not assignee:
                skipped_tasks.append(
                    {
                        "title": title,
                        "assignee_name": assignee_name,
                        "reason": "No users available to assign",
                        "auto_assigned": False,
                        "auto_assigned_to": None,
                    }
                )
                continue
                
            assigner_id = current_user.id
            if assigner_name:
                assigner_user = (
                    db.query(User)
                    .filter(User.full_name.ilike(f"%{assigner_name}%"))
                    .first()
                )
                if assigner_user:
                    assigner_id = assigner_user.id
            
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
                assigned_by=assigner_id,
                meeting_id=meeting_id,
                due_date=due_date
            )
    
            db.add(task)
            task_index = len(created_tasks)
            created_tasks.append(task)

            if auto_assigned:
                auto_assigned_info[task_index] = assignee.full_name or assignee.email

                if assignee_name:
                    logger.warning(
                        "AI task auto-assigned (user '%s' not found) — "
                        "title=%r → assigned to '%s' (least loaded)",
                        assignee_name, title, assignee.full_name
                    )
                else:
                    logger.warning(
                        "AI task auto-assigned (no assignee in transcript) — "
                        "title=%r → assigned to '%s' (least loaded)",
                        title, assignee.full_name
                    )
    
        # Commit all created tasks together
        db.commit()
    
        # Refresh to get generated IDs and timestamps
        for task in created_tasks:
            db.refresh(task)

        # Build the enriched task list that the API will return so the frontend
        # can tell which ones were auto-assigned and to whom.
        created_payload = []
        for i, task in enumerate(created_tasks):
            auto_to = auto_assigned_info.get(i)
            created_payload.append(
                {
                    "task": task,
                    "auto_assigned": auto_to is not None,
                    "auto_assigned_to": auto_to,
                }
            )

        logger.info(
            "AI tasks for meeting_id=%s: %s created (%s auto-assigned), %s skipped",
            meeting_id,
            len(created_tasks),
            len(auto_assigned_info),
            len(skipped_tasks),
        )
        for s in skipped_tasks:
            logger.warning(
                "AI task skipped — reason=%r title=%r assignee=%r",
                s["reason"], s["title"], s["assignee_name"]
            )

        # Send one notification per task to the assignee (skip self-assignments)
        assigner_name = current_user.full_name or "Someone"
        for i, task in enumerate(created_tasks):
            if task.assignee_id != current_user.id:
                auto_to = auto_assigned_info.get(i)
                if auto_to:
                    notif_title = "Task auto-assigned to you"
                    notif_msg = (
                        f"{assigner_name} could not identify an assignee for "
                        f'"{task.title}" — it was automatically assigned to you '
                        f"as you have the fewest tasks."
                    )
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

        return {
            "created": created_tasks,
            "skipped": skipped_tasks,
            "auto_assigned_tasks": created_payload,
        }
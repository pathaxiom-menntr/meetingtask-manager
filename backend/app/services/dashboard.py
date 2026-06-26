from sqlalchemy.orm import Session

from app.models.meeting import Meeting
from app.models.task import Task
from app.models.user import User


class DashboardService:

    @staticmethod
    def get_dashboard(db: Session, current_user: User):

        total_meetings = (
            db.query(Meeting)
            .filter(Meeting.uploaded_by == current_user.id)
            .count()
        )

        total_tasks = (
            db.query(Task)
            .filter(Task.assignee_id == current_user.id)
            .count()
        )

        pending_tasks = (
            db.query(Task)
            .filter(
                Task.assignee_id == current_user.id,
                Task.status == "pending"
            )
            .count()
        )

        completed_tasks = (
            db.query(Task)
            .filter(
                Task.assignee_id == current_user.id,
                Task.status == "completed"
            )
            .count()
        )

        if total_tasks == 0:
            completion_rate = 0.0
        else:
            completion_rate = round(
                (completed_tasks / total_tasks) * 100,
                2
            )

        return {
            "total_meetings": total_meetings,
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "completion_rate": completion_rate
        }
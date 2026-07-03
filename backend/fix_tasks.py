import os
import sys

# Setup environment to load models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.meeting import Meeting

def fix_tasks():
    db: Session = SessionLocal()
    try:
        # Get all tasks that have a meeting_id
        tasks = db.query(Task).filter(Task.meeting_id.isnot(None)).all()
        
        fixed_count = 0
        for task in tasks:
            meeting = db.query(Meeting).filter(Meeting.id == task.meeting_id).first()
            if not meeting:
                continue
                
            uploader = db.query(User).filter(User.id == meeting.uploaded_by).first()
            if not uploader:
                continue
                
            true_team = uploader.team_code
            
            assignee = db.query(User).filter(User.id == task.assignee_id).first()
            assigner = db.query(User).filter(User.id == task.assigned_by).first()
            
            needs_update = False
            
            # Fix assignee
            if assignee and assignee.team_code != true_team:
                print(f"Task {task.id}: Assignee {assignee.full_name} is from team '{assignee.team_code}', expected '{true_team}'")
                
                # First, check if there's a user in the true team with EXACT same name
                correct_user = db.query(User).filter(User.full_name == assignee.full_name, User.team_code == true_team).first()
                if correct_user:
                    task.assignee_id = correct_user.id
                else:
                    task.assignee_id = uploader.id
                needs_update = True
                
            # Fix assigner
            if assigner and assigner.team_code != true_team:
                print(f"Task {task.id}: Assigner {assigner.full_name} is from team '{assigner.team_code}', expected '{true_team}'")
                
                correct_user = db.query(User).filter(User.full_name == assigner.full_name, User.team_code == true_team).first()
                if correct_user:
                    task.assigned_by = correct_user.id
                else:
                    task.assigned_by = uploader.id
                needs_update = True
                
            if needs_update:
                fixed_count += 1
                
        db.commit()
        print(f"Fixed {fixed_count} tasks!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_tasks()

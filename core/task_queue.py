import uuid

from core.database import SessionLocal
from core.task_model import Task


class TaskQueueManager:
    """
    Manages the shared task board for agent communication.
    """

    def add_task(self, ticket_name, description, priority=3, assignee=None, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            task = Task(
                task_id=str(uuid.uuid4()),
                ticket_name=ticket_name,
                description=description,
                priority=priority,
                status="BACKLOG",
                assignee=assignee,
            )
            managed_db.add(task)
            managed_db.commit()
            return task
        finally:
            if close_db:
                managed_db.close()

    def get_pending_tasks(self, status="PENDING", db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            return (
                managed_db.query(Task)
                .filter(Task.status == status)
                .order_by(Task.priority.asc())
                .all()
            )
        finally:
            if close_db:
                managed_db.close()

    def update_task_status(self, task_id, status, notes=None, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            task = managed_db.query(Task).filter(Task.task_id == task_id).first()
            if task:
                task.status = status
                if notes:
                    task.notes = notes
                managed_db.commit()
            return task
        finally:
            if close_db:
                managed_db.close()

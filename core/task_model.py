from sqlalchemy import Column, DateTime, Integer, String

from core.database import Base, utcnow


class Task(Base):
    """Shared task-board row used by the dashboard and trigger scripts."""

    __tablename__ = "task_board"

    task_id = Column(String, primary_key=True)
    ticket_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    priority = Column(Integer, default=3)
    status = Column(String, nullable=False, default="BACKLOG")
    assignee = Column(String)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

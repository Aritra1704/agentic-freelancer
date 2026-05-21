import datetime
import os
from enum import Enum

from dotenv import load_dotenv
from sqlalchemy import JSON, Column, DateTime, String, Text, UniqueConstraint, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()


def utcnow():
    return datetime.datetime.now(datetime.UTC)


class PipelineStatus(str, Enum):
    NEW = "new"
    SCRAPED = "scraped"
    REFINING = "refining"
    REFINED = "refined"
    REFINEMENT_FAILED = "refinement_failed"
    STRATEGIZING = "strategizing"
    STRATEGIZED = "strategized"
    APPLIED = "applied"
    WON = "won"
    LOST = "lost"
    ERROR = "error"


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://aritrarpal@localhost/freelance_os")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True)
    platform = Column(String)
    title = Column(String)
    url = Column(String, unique=True)
    budget = Column(String)
    description = Column(Text)
    raw_data = Column(JSON)
    status = Column(String, default=PipelineStatus.NEW.value)
    technical_doubts = Column(JSON)
    suggested_stack = Column(JSON)
    hld_code = Column(Text)
    lld_code = Column(Text)
    milestones = Column(JSON)
    quotation = Column(JSON)
    pitch_content = Column(Text)
    user_feedback = Column(JSON)
    notion_lead_page_id = Column(String)
    notion_strategy_page_id = Column(String)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    last_updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    __table_args__ = (UniqueConstraint("url", name="_url_uc"),)


class VerbatimLog(Base):
    """
    MemPalace Concept: Verbatim Storage for Critical Data.
    Stores raw LLM outputs and original states to prevent information loss.
    """

    __tablename__ = "verbatim_logs"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow)
    category = Column(String)
    interaction_type = Column(String)
    original_content = Column(Text)
    interaction_metadata = Column(JSON)


def init_db():
    from core.task_model import Task  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _ensure_lead_columns()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _ensure_lead_columns():
    inspector = inspect(engine)
    if "leads" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("leads")}
    column_ddl = {
        "technical_doubts": "ALTER TABLE leads ADD COLUMN technical_doubts JSON",
        "suggested_stack": "ALTER TABLE leads ADD COLUMN suggested_stack JSON",
        "hld_code": "ALTER TABLE leads ADD COLUMN hld_code TEXT",
        "lld_code": "ALTER TABLE leads ADD COLUMN lld_code TEXT",
        "milestones": "ALTER TABLE leads ADD COLUMN milestones JSON",
        "quotation": "ALTER TABLE leads ADD COLUMN quotation JSON",
        "pitch_content": "ALTER TABLE leads ADD COLUMN pitch_content TEXT",
        "user_feedback": "ALTER TABLE leads ADD COLUMN user_feedback JSON",
        "notion_lead_page_id": "ALTER TABLE leads ADD COLUMN notion_lead_page_id VARCHAR",
        "notion_strategy_page_id": "ALTER TABLE leads ADD COLUMN notion_strategy_page_id VARCHAR",
        "error_message": "ALTER TABLE leads ADD COLUMN error_message TEXT",
        "last_updated_at": "ALTER TABLE leads ADD COLUMN last_updated_at TIMESTAMP",
    }

    with engine.begin() as connection:
        for column_name, ddl in column_ddl.items():
            if column_name not in existing_columns:
                connection.execute(text(ddl))
        if "last_updated_at" not in existing_columns:
            connection.execute(text("UPDATE leads SET last_updated_at = created_at WHERE last_updated_at IS NULL"))

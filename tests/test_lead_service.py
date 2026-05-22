from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base, Lead, PipelineStatus
from core.lead_service import approve_lead, list_inbox_leads, reject_lead
from core.task_model import Task  # noqa: F401


def build_session():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return Session()


def make_lead(**overrides):
    payload = {
        "id": overrides.pop("id", "lead-1"),
        "platform": overrides.pop("platform", "Upwork"),
        "title": overrides.pop("title", "Ship a lead inbox"),
        "url": overrides.pop("url", "https://example.com/jobs/lead-1"),
        "budget": overrides.pop("budget", "$5,500"),
        "description": overrides.pop("description", "Build a dashboard flow for manual lead review."),
        "raw_data": overrides.pop("raw_data", {}),
        "status": overrides.pop("status", PipelineStatus.REFINED.value),
        "technical_doubts": overrides.pop(
            "technical_doubts",
            [
                "What system should own the approved task lifecycle?",
                "Which auth boundary protects the dashboard routes?",
                "What is the expected turnaround for manual vetting?",
            ],
        ),
        "suggested_stack": overrides.pop("suggested_stack", ["Next.js", "Python", "Postgres"]),
    }
    payload.update(overrides)
    return Lead(**payload)


def test_approve_lead_promotes_it_to_task_board():
    session = build_session()
    lead = make_lead()
    session.add(lead)
    session.commit()

    result = approve_lead(lead.id, db=session)
    created_task = session.query(Task).filter(Task.task_id == result["task"]["task_id"]).first()

    assert result["ok"] is True
    assert result["action"] == "approve"
    assert result["lead"]["status"] == "approved"
    assert result["task"]["status"] == "BACKLOG"
    assert created_task is not None
    assert created_task.ticket_name == lead.title
    assert "Promoted from lead inbox" in (created_task.notes or "")


def test_reject_lead_archives_it_without_creating_task():
    session = build_session()
    lead = make_lead(id="lead-2", url="https://example.com/jobs/lead-2")
    session.add(lead)
    session.commit()

    result = reject_lead(lead.id, db=session)

    assert result["ok"] is True
    assert result["action"] == "reject"
    assert result["lead"]["status"] == "archived"
    assert session.query(Task).count() == 0


def test_list_inbox_leads_hides_approved_and_archived_rows():
    session = build_session()
    session.add(make_lead(id="lead-visible", url="https://example.com/jobs/lead-visible"))
    session.add(make_lead(id="lead-approved", url="https://example.com/jobs/lead-approved", status="approved"))
    session.add(make_lead(id="lead-archived", url="https://example.com/jobs/lead-archived", status="archived"))
    session.commit()

    payload = list_inbox_leads(db=session)

    assert payload["counts"]["total"] == 1
    assert [lead["id"] for lead in payload["leads"]] == ["lead-visible"]

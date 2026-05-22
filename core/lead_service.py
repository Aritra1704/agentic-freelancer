import json
import re
import uuid
from collections import Counter

from core.database import Lead, PipelineStatus, SessionLocal, utcnow
from core.task_board_service import serialize_task
from core.task_model import Task


INBOX_HIDDEN_STATUSES = {
    PipelineStatus.APPLIED.value,
    PipelineStatus.WON.value,
    PipelineStatus.LOST.value,
    "approved",
    "archived",
}


class LeadActionError(ValueError):
    """Raised when a lead cannot be promoted or archived from the inbox."""


def serialize_lead(lead):
    raw_data = lead.raw_data or {}
    return {
        "id": lead.id,
        "platform": lead.platform,
        "title": lead.title,
        "url": lead.url,
        "budget": lead.budget,
        "description": lead.description,
        "status": lead.status,
        "technical_doubts": lead.technical_doubts or [],
        "suggested_stack": lead.suggested_stack or [],
        "qualification_notes": raw_data.get("qualification_notes"),
        "opportunity_score": raw_data.get("opportunity_score"),
        "tags": raw_data.get("tags") or [],
        "task_board_task_id": raw_data.get("task_board_task_id"),
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "last_updated_at": lead.last_updated_at.isoformat() if lead.last_updated_at else None,
    }


def list_inbox_leads(db=None):
    managed_db = db or SessionLocal()
    close_db = db is None
    try:
        leads = (
            managed_db.query(Lead)
            .filter(~Lead.status.in_(tuple(INBOX_HIDDEN_STATUSES)))
            .order_by(Lead.last_updated_at.desc(), Lead.created_at.desc())
            .all()
        )

        serialized = [serialize_lead(lead) for lead in leads]
        status_counts = Counter(lead["status"] or "unknown" for lead in serialized)
        platform_counts = Counter(lead["platform"] or "Unknown" for lead in serialized)

        return {
            "leads": serialized,
            "counts": {
                "total": len(serialized),
                "by_status": dict(status_counts),
                "by_platform": dict(platform_counts),
            },
            "updated_at": utcnow().isoformat(),
        }
    finally:
        if close_db:
            managed_db.close()


def approve_lead(lead_id, db=None):
    managed_db = db or SessionLocal()
    close_db = db is None
    try:
        lead = managed_db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise LeadActionError(f"Lead '{lead_id}' was not found.")

        _assert_lead_actionable(lead, action="approve")

        raw_data = dict(lead.raw_data or {})
        if raw_data.get("task_board_task_id"):
            raise LeadActionError(f"Lead '{lead_id}' has already been promoted to the task board.")

        task = Task(
            task_id=str(uuid.uuid4()),
            ticket_name=(lead.title or "Untitled lead").strip(),
            description=_build_task_description(lead),
            priority=_derive_priority(lead.budget),
            status="BACKLOG",
            assignee="freelance-os",
            notes=_build_task_notes(lead),
        )
        managed_db.add(task)

        promoted_at = utcnow()
        raw_data["task_board_task_id"] = task.task_id
        raw_data["promoted_at"] = promoted_at.isoformat()
        raw_data["promotion_source"] = "lead_inbox"
        lead.raw_data = raw_data
        lead.status = "approved"
        lead.last_updated_at = promoted_at

        managed_db.commit()
        managed_db.refresh(task)

        return {
            "ok": True,
            "action": "approve",
            "lead": serialize_lead(lead),
            "task": serialize_task(task),
        }
    finally:
        if close_db:
            managed_db.close()


def reject_lead(lead_id, db=None):
    managed_db = db or SessionLocal()
    close_db = db is None
    try:
        lead = managed_db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise LeadActionError(f"Lead '{lead_id}' was not found.")

        _assert_lead_actionable(lead, action="reject")

        archived_at = utcnow()
        raw_data = dict(lead.raw_data or {})
        raw_data["archived_at"] = archived_at.isoformat()
        raw_data["archived_from"] = "lead_inbox"
        lead.raw_data = raw_data
        lead.status = "archived"
        lead.last_updated_at = archived_at

        managed_db.commit()

        return {
            "ok": True,
            "action": "reject",
            "lead": serialize_lead(lead),
        }
    finally:
        if close_db:
            managed_db.close()


def _assert_lead_actionable(lead, action):
    status = (lead.status or "").lower()
    if status == "approved":
        raise LeadActionError(f"Lead '{lead.id}' is already approved.")
    if status == "archived":
        raise LeadActionError(f"Lead '{lead.id}' is already archived.")
    if status in {
        PipelineStatus.APPLIED.value,
        PipelineStatus.WON.value,
        PipelineStatus.LOST.value,
    }:
        raise LeadActionError(
            f"Lead '{lead.id}' cannot be {action}d from the inbox once it has reached '{status}'."
        )


def _build_task_description(lead):
    description = (lead.description or "").strip()
    if description:
        return description
    return f"Manual review promotion from {lead.platform or 'unknown'} lead inbox."


def _build_task_notes(lead):
    lines = [
        f"Promoted from lead inbox on {utcnow().isoformat(timespec='seconds')}.",
        f"Platform: {lead.platform or 'Unknown'}",
        f"Budget: {lead.budget or 'Unknown'}",
    ]

    if lead.url:
        lines.append(f"Source: {lead.url}")

    if lead.suggested_stack:
        lines.append(f"Suggested stack: {', '.join(str(item) for item in lead.suggested_stack)}")

    if lead.technical_doubts:
        lines.append("Technical doubts:")
        lines.extend(f"- {question}" for question in lead.technical_doubts[:5])

    qualification_notes = (lead.raw_data or {}).get("qualification_notes")
    if qualification_notes:
        lines.append(f"Qualification notes: {qualification_notes}")

    return "\n".join(lines)


def _derive_priority(budget_text):
    if not budget_text:
        return 3

    matches = re.findall(r"\d[\d,]*", budget_text)
    amounts = [int(match.replace(",", "")) for match in matches]
    if not amounts:
        return 3

    highest_budget = max(amounts)
    if highest_budget >= 10000:
        return 1
    if highest_budget >= 5000:
        return 2
    if highest_budget >= 1500:
        return 3
    if highest_budget >= 500:
        return 4
    return 5


def print_json(payload):
    print(json.dumps(payload, indent=2))

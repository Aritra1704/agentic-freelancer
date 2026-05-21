import json

from core.database import SessionLocal, utcnow
from core.task_model import Task


STATUS_ORDER = [
    "BACKLOG",
    "LEGAL_REVIEW",
    "PENDING",
    "IN_PROGRESS",
    "COMPLIANCE_CHECK",
    "READY_FOR_DELIVERY",
    "COMPLETED",
    "BLOCKED",
]

CONTRACT_RISK_KEYWORDS = [
    "unlimited liability",
    "non-compete",
    "non compete",
    "indemnify",
    "exclusive ownership in perpetuity",
]

COMPLIANCE_RISK_KEYWORDS = [
    "api key",
    "secret",
    "password",
    "private key",
    "token",
    "ssn",
    "credit card",
    "pii",
]


def serialize_task(task):
    return {
        "task_id": task.task_id,
        "ticket_name": task.ticket_name,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "assignee": task.assignee,
        "notes": task.notes,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def list_tasks(db=None):
    managed_db = db or SessionLocal()
    close_db = db is None
    try:
        tasks = (
            managed_db.query(Task)
            .order_by(Task.priority.asc(), Task.updated_at.desc(), Task.created_at.desc())
            .all()
        )
        return [serialize_task(task) for task in tasks]
    finally:
        if close_db:
            managed_db.close()


def append_note(existing_notes, entry):
    timestamp = utcnow().isoformat(timespec="seconds")
    line = f"[{timestamp}] {entry}"
    return f"{existing_notes}\n{line}".strip() if existing_notes else line


def contains_risk(text, keywords):
    lowered = (text or "").lower()
    return [keyword for keyword in keywords if keyword in lowered]


def run_sales_scan(db=None):
    managed_db = db or SessionLocal()
    close_db = db is None
    try:
        backlog_tasks = (
            managed_db.query(Task)
            .filter(Task.status == "BACKLOG")
            .order_by(Task.priority.asc(), Task.created_at.asc())
            .all()
        )
        delivery_tasks = (
            managed_db.query(Task)
            .filter(Task.status == "READY_FOR_DELIVERY")
            .order_by(Task.priority.asc(), Task.updated_at.asc())
            .all()
        )

        moved_to_legal = 0
        completed = 0

        for task in backlog_tasks:
            task.status = "LEGAL_REVIEW"
            task.assignee = "legal_agent"
            task.notes = append_note(task.notes, "Sales scan packaged scope and forwarded to legal review.")
            moved_to_legal += 1

        for task in delivery_tasks:
            task.status = "COMPLETED"
            task.assignee = "freelance-os"
            task.notes = append_note(task.notes, "Sales scan marked the task delivered to the client.")
            completed += 1

        managed_db.commit()
        return {
            "agent": "sales",
            "moved_to_legal_review": moved_to_legal,
            "marked_completed": completed,
            "total_processed": moved_to_legal + completed,
            "run_at": utcnow().isoformat(),
        }
    finally:
        if close_db:
            managed_db.close()


def run_legal_review(db=None):
    managed_db = db or SessionLocal()
    close_db = db is None
    try:
        legal_review_tasks = (
            managed_db.query(Task)
            .filter(Task.status == "LEGAL_REVIEW")
            .order_by(Task.priority.asc(), Task.created_at.asc())
            .all()
        )
        compliance_tasks = (
            managed_db.query(Task)
            .filter(Task.status == "COMPLIANCE_CHECK")
            .order_by(Task.priority.asc(), Task.updated_at.asc())
            .all()
        )

        approved_for_dev = 0
        approved_for_delivery = 0
        blocked = 0

        for task in legal_review_tasks:
            risk_hits = contains_risk(" ".join(filter(None, [task.description, task.notes])), CONTRACT_RISK_KEYWORDS)
            if risk_hits:
                task.status = "BLOCKED"
                task.assignee = "freelance-os"
                task.notes = append_note(
                    task.notes,
                    f"Legal review blocked the task due to contract risks: {', '.join(risk_hits)}.",
                )
                blocked += 1
                continue

            task.status = "PENDING"
            task.assignee = "localclaw"
            task.notes = append_note(task.notes, "Legal review approved the scope for development.")
            approved_for_dev += 1

        for task in compliance_tasks:
            risk_hits = contains_risk(" ".join(filter(None, [task.description, task.notes])), COMPLIANCE_RISK_KEYWORDS)
            if risk_hits:
                task.status = "BLOCKED"
                task.assignee = "localclaw"
                task.notes = append_note(
                    task.notes,
                    f"Compliance review blocked delivery due to hygiene risks: {', '.join(risk_hits)}.",
                )
                blocked += 1
                continue

            task.status = "READY_FOR_DELIVERY"
            task.assignee = "freelance-os"
            task.notes = append_note(task.notes, "Compliance review cleared the deliverable for client delivery.")
            approved_for_delivery += 1

        managed_db.commit()
        return {
            "agent": "legal",
            "approved_for_dev": approved_for_dev,
            "approved_for_delivery": approved_for_delivery,
            "blocked": blocked,
            "total_processed": approved_for_dev + approved_for_delivery + blocked,
            "run_at": utcnow().isoformat(),
        }
    finally:
        if close_db:
            managed_db.close()


def snapshot_payload():
    tasks = list_tasks()
    counts = {status: 0 for status in STATUS_ORDER}
    columns = {status: [] for status in STATUS_ORDER}

    for task in tasks:
        status = task["status"]
        counts.setdefault(status, 0)
        columns.setdefault(status, [])
        counts[status] += 1
        columns[status].append(task)

    return {
        "statuses": STATUS_ORDER,
        "counts": counts,
        "tasks": tasks,
        "columns": columns,
        "updated_at": utcnow().isoformat(),
    }


def print_json(payload):
    print(json.dumps(payload, indent=2))

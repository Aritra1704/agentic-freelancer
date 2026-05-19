from fastapi import FastAPI
from sqlalchemy import func

from core.database import Lead, SessionLocal


app = FastAPI(title="Freelance-OS Control Tower")


def serialize_lead(lead):
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
        "hld_code": lead.hld_code,
        "lld_code": lead.lld_code,
        "milestones": lead.milestones or [],
        "quotation": lead.quotation,
        "pitch_content": lead.pitch_content,
        "user_feedback": lead.user_feedback,
        "error_message": lead.error_message,
        "created_at": lead.created_at.isoformat() if lead.created_at else None,
        "last_updated_at": lead.last_updated_at.isoformat() if lead.last_updated_at else None,
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/leads")
def list_leads():
    db = SessionLocal()
    try:
        leads = db.query(Lead).order_by(Lead.last_updated_at.desc()).all()
        return [serialize_lead(lead) for lead in leads]
    finally:
        db.close()


@app.get("/leads/{lead_id}")
def get_lead(lead_id: str):
    db = SessionLocal()
    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        return serialize_lead(lead) if lead else {"ok": False, "reason": "lead_not_found"}
    finally:
        db.close()


@app.get("/strategies")
def list_strategies():
    db = SessionLocal()
    try:
        leads = (
            db.query(Lead)
            .filter(Lead.pitch_content.isnot(None))
            .order_by(Lead.last_updated_at.desc())
            .all()
        )
        return [serialize_lead(lead) for lead in leads]
    finally:
        db.close()


@app.get("/dashboard/summary")
def dashboard_summary():
    db = SessionLocal()
    try:
        counts = {
            status: count
            for status, count in db.query(Lead.status, func.count(Lead.id)).group_by(Lead.status).all()
        }
        recent = db.query(Lead).order_by(Lead.last_updated_at.desc()).limit(5).all()
        return {
            "counts": counts,
            "recent": [serialize_lead(lead) for lead in recent],
        }
    finally:
        db.close()

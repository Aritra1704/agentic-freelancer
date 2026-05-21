import uuid

from core.database import Lead, PipelineStatus, SessionLocal, utcnow
from core.memory_manager import MemoryManager


class Stitcher:
    """
    State machine for the lead pipeline.
    Ensures transitions are explicit, queryable, and resumable.
    """

    ALLOWED_TRANSITIONS = {
        PipelineStatus.NEW.value: {PipelineStatus.SCRAPED.value, PipelineStatus.ERROR.value},
        PipelineStatus.SCRAPED.value: {PipelineStatus.REFINING.value, PipelineStatus.ERROR.value},
        PipelineStatus.REFINING.value: {
            PipelineStatus.REFINED.value,
            PipelineStatus.REFINEMENT_FAILED.value,
            PipelineStatus.ERROR.value,
        },
        PipelineStatus.REFINEMENT_FAILED.value: {
            PipelineStatus.REFINING.value,
            PipelineStatus.ERROR.value,
        },
        PipelineStatus.REFINED.value: {
            PipelineStatus.REFINEMENT_FAILED.value,
            PipelineStatus.STRATEGIZING.value,
            PipelineStatus.ERROR.value,
        },
        PipelineStatus.STRATEGIZING.value: {PipelineStatus.STRATEGIZED.value, PipelineStatus.ERROR.value},
        PipelineStatus.STRATEGIZED.value: {
            PipelineStatus.APPLIED.value,
            PipelineStatus.WON.value,
            PipelineStatus.LOST.value,
            PipelineStatus.ERROR.value,
        },
        PipelineStatus.APPLIED.value: {PipelineStatus.WON.value, PipelineStatus.LOST.value, PipelineStatus.ERROR.value},
        PipelineStatus.WON.value: set(),
        PipelineStatus.LOST.value: set(),
        PipelineStatus.ERROR.value: {
            PipelineStatus.SCRAPED.value,
            PipelineStatus.REFINEMENT_FAILED.value,
            PipelineStatus.REFINED.value,
            PipelineStatus.STRATEGIZED.value,
        },
    }

    def transition(self, lead_id, new_status, error_message=None, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            lead = managed_db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                raise ValueError(f"Lead '{lead_id}' not found.")

            next_status = self._normalize_status(new_status)
            current_status = self._normalize_status(lead.status)
            if next_status != current_status and next_status not in self.ALLOWED_TRANSITIONS.get(current_status, set()):
                raise ValueError(f"Invalid transition from '{current_status}' to '{next_status}'.")

            lead.status = next_status
            lead.last_updated_at = utcnow()
            if next_status not in {PipelineStatus.ERROR.value, PipelineStatus.REFINEMENT_FAILED.value}:
                lead.error_message = None
            elif error_message:
                lead.error_message = error_message

            managed_db.commit()
            return lead
        finally:
            if close_db:
                managed_db.close()

    def create_lead(self, platform, title, url, budget, description, raw_data=None, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            lead = Lead(
                id=str(uuid.uuid4()),
                platform=platform,
                title=title,
                url=url,
                budget=budget,
                description=description,
                raw_data=raw_data or {},
                status=PipelineStatus.SCRAPED.value,
                last_updated_at=utcnow(),
            )
            managed_db.add(lead)
            managed_db.commit()
            managed_db.refresh(lead)
            return lead
        finally:
            if close_db:
                managed_db.close()

    def mark_error(self, lead_id, stage, error_message, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            lead = self.transition(
                lead_id=lead_id,
                new_status=PipelineStatus.ERROR.value,
                error_message=error_message,
                db=managed_db,
            )
            MemoryManager.remember_verbatim(
                category=MemoryManager.ROOM_TECH_BLOCKED,
                interaction_type="pipeline_error",
                content=error_message,
                metadata={
                    "lead_id": lead_id,
                    "lead_title": lead.title if lead else None,
                    "stage": stage,
                    "status": PipelineStatus.ERROR.value,
                },
            )
            return lead
        finally:
            if close_db:
                managed_db.close()

    def mark_refinement_failed(self, lead_id, error_message, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            lead = self.transition(
                lead_id=lead_id,
                new_status=PipelineStatus.REFINEMENT_FAILED.value,
                error_message=error_message,
                db=managed_db,
            )
            MemoryManager.remember_verbatim(
                category=MemoryManager.ROOM_TECH_BLOCKED,
                interaction_type="refinement_failed",
                content=error_message,
                metadata={
                    "lead_id": lead_id,
                    "lead_title": lead.title if lead else None,
                    "stage": "refining",
                    "status": PipelineStatus.REFINEMENT_FAILED.value,
                },
            )
            return lead
        finally:
            if close_db:
                managed_db.close()

    def get_pending_tasks(self, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            return {
                PipelineStatus.SCRAPED.value: managed_db.query(Lead).filter(Lead.status == PipelineStatus.SCRAPED.value).all(),
                PipelineStatus.REFINEMENT_FAILED.value: managed_db.query(Lead).filter(
                    Lead.status == PipelineStatus.REFINEMENT_FAILED.value
                ).all(),
                PipelineStatus.REFINED.value: managed_db.query(Lead).filter(Lead.status == PipelineStatus.REFINED.value).all(),
                PipelineStatus.ERROR.value: managed_db.query(Lead).filter(Lead.status == PipelineStatus.ERROR.value).all(),
            }
        finally:
            if close_db:
                managed_db.close()

    def claim_for_refinement(self, limit=None, db=None):
        return self._claim_batch(
            [PipelineStatus.SCRAPED.value, PipelineStatus.REFINEMENT_FAILED.value],
            PipelineStatus.REFINING.value,
            limit=limit,
            db=db,
        )

    def claim_for_strategy(self, limit=None, db=None):
        return self._claim_batch(PipelineStatus.REFINED.value, PipelineStatus.STRATEGIZING.value, limit=limit, db=db)

    def _claim_batch(self, current_status, next_status, limit=None, db=None):
        managed_db = db or SessionLocal()
        close_db = db is None
        try:
            if isinstance(current_status, (list, tuple, set)):
                query = managed_db.query(Lead).filter(Lead.status.in_(list(current_status))).order_by(Lead.created_at.asc())
            else:
                query = managed_db.query(Lead).filter(Lead.status == current_status).order_by(Lead.created_at.asc())
            leads = query.limit(limit).all() if limit else query.all()
            claimed = []
            for lead in leads:
                lead.status = next_status
                lead.last_updated_at = utcnow()
                claimed.append(lead)
            managed_db.commit()
            return claimed
        finally:
            if close_db:
                managed_db.close()

    def _normalize_status(self, status):
        return status.value if isinstance(status, PipelineStatus) else str(status).lower()

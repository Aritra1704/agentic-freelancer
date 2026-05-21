from core.database import PipelineStatus
from core.orchestrator import Stitcher


class FakeLead:
    def __init__(self, lead_id="lead-1", status=PipelineStatus.SCRAPED.value):
        self.id = lead_id
        self.title = "Lead"
        self.status = status
        self.error_message = None
        self.last_updated_at = None
        self.created_at = None


class FakeFilterResult:
    def __init__(self, lead):
        self.lead = lead

    def first(self):
        return self.lead

    def all(self):
        return [self.lead] if self.lead else []

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, value):
        return self


class FakeQuery:
    def __init__(self, lead):
        self.lead = lead

    def filter(self, *args, **kwargs):
        return FakeFilterResult(self.lead)

    def order_by(self, *args, **kwargs):
        return FakeFilterResult(self.lead)


class FakeSession:
    def __init__(self, lead):
        self.lead = lead
        self.committed = False

    def query(self, model):
        return FakeQuery(self.lead)

    def commit(self):
        self.committed = True

    def close(self):
        pass

    def add(self, value):
        self.lead = value

    def refresh(self, value):
        pass


def test_transition_updates_status_and_commits():
    lead = FakeLead(status=PipelineStatus.SCRAPED.value)
    session = FakeSession(lead)
    stitcher = Stitcher()

    updated = stitcher.transition(lead.id, PipelineStatus.REFINING.value, db=session)

    assert session.committed is True
    assert updated.status == PipelineStatus.REFINING.value


def test_invalid_transition_raises():
    lead = FakeLead(status=PipelineStatus.SCRAPED.value)
    session = FakeSession(lead)
    stitcher = Stitcher()

    try:
        stitcher.transition(lead.id, PipelineStatus.STRATEGIZED.value, db=session)
    except ValueError as exc:
        assert "Invalid transition" in str(exc)
    else:
        raise AssertionError("Expected invalid transition to raise ValueError.")


def test_mark_refinement_failed_sets_explicit_status(monkeypatch):
    lead = FakeLead(status=PipelineStatus.REFINING.value)
    session = FakeSession(lead)
    captured = {}

    monkeypatch.setattr(
        "core.orchestrator.MemoryManager.remember_verbatim",
        lambda **kwargs: captured.update(kwargs),
    )

    stitcher = Stitcher()
    updated = stitcher.mark_refinement_failed(lead.id, "Missing technical doubts.", db=session)

    assert session.committed is True
    assert updated.status == PipelineStatus.REFINEMENT_FAILED.value
    assert updated.error_message == "Missing technical doubts."
    assert captured["interaction_type"] == "refinement_failed"
    assert captured["metadata"]["status"] == PipelineStatus.REFINEMENT_FAILED.value

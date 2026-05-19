import datetime

from agents.strategist_agent import StrategistAgent
from core.memory_manager import MemoryManager


class FakeSession:
    def __init__(self):
        self.added = []
        self.committed = False
        self.closed = False

    def add(self, value):
        self.added.append(value)

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class FakeQuery:
    def __init__(self, logs):
        self.logs = list(logs)
        self._limit = None

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, value):
        self._limit = value
        return self

    def all(self):
        if self._limit is None:
            return list(self.logs)
        return list(self.logs)[: self._limit]


class FakeReadSession:
    def __init__(self, logs):
        self.logs = logs
        self.closed = False

    def query(self, model):
        return FakeQuery(self.logs)

    def close(self):
        self.closed = True


class FakeLog:
    def __init__(self, category, metadata, original_content, timestamp=None):
        self.category = category
        self.interaction_metadata = metadata
        self.original_content = original_content
        self.timestamp = timestamp or datetime.datetime.now(datetime.UTC)


def test_learn_from_failure_stores_structured_metadata(monkeypatch):
    session = FakeSession()
    captured = {}

    class FakeOllamaBridge:
        def __init__(self, model="llama3"):
            captured["model"] = model

        def generate_code(self, prompt):
            captured["prompt"] = prompt
            return "Verify the client budget and scope constraints before drafting the next proposal."

    monkeypatch.setattr("core.memory_manager.SessionLocal", lambda: session)
    monkeypatch.setattr("core.memory_manager.OllamaBridge", FakeOllamaBridge)

    learning = MemoryManager.learn_from_failure(
        stage="Strategist",
        observation="The client rejected the proposal because the budget was too low for the requested scope.",
    )

    assert captured["model"] == "mistral"
    assert session.committed is True
    assert session.closed is True
    assert len(session.added) == 1
    assert session.added[0].category == MemoryManager.ROOM_BUSINESS_FRICTION
    assert learning["room"] == MemoryManager.ROOM_BUSINESS_FRICTION
    assert learning["stage"] == "strategist"
    assert learning["interaction_id"] == session.added[0].id
    assert "budget" in learning["context_tags"]
    assert learning["pre_mortem_advice"].endswith(".")


def test_pre_flight_check_formats_negative_constraints(monkeypatch):
    monkeypatch.setattr(
        "agents.strategist_agent.MemoryManager.find_relevant_failures",
        lambda job_data, limit=5: [
            {
                "context_tag": "playwright / cloudflare",
                "matched_tags": ["playwright", "cloudflare"],
                "stage": "scout",
                "pre_mortem_advice": "Use a persistent browser profile and anti-bot validation before scraping.",
                "timestamp": datetime.datetime.now(datetime.UTC),
            }
        ],
    )

    strategist = StrategistAgent.__new__(StrategistAgent)
    constraints = strategist.pre_flight_check(
        {
            "title": "Playwright scraping for startup leads",
            "description": "Need scraping for a startup using Playwright.",
        }
    )

    assert constraints.startswith("Negative Constraints:")
    assert "playwright / cloudflare" in constraints
    assert "Do not repeat" in constraints


def test_detect_patterns_returns_alert_block_for_repeated_niche(monkeypatch):
    logs = [
        FakeLog(
            MemoryManager.ROOM_BUSINESS_FRICTION,
            {
                "context_tags": ["startup", "budget"],
                "observation": "Budget mismatch on startup lead.",
                "pre_mortem_advice": "Confirm budget fit before presenting the delivery plan.",
            },
            "Budget mismatch on startup lead.",
        )
        for _ in range(4)
    ]
    session = FakeReadSession(logs)
    monkeypatch.setattr("core.memory_manager.SessionLocal", lambda: session)

    result = MemoryManager.detect_patterns()

    assert session.closed is True
    assert result["should_alert"] is True
    assert result["niche"] == "startup"
    assert result["count"] == 4
    assert "Alert:" in result["alert_block"]
    assert "Guardrail:" in result["alert_block"]


def test_strategist_prompt_includes_conversion_guidelines(monkeypatch, tmp_path):
    captured = {}

    class FakeResponse:
        content = "proposal"

    class FakeLLM:
        def invoke(self, prompt):
            captured["prompt"] = prompt
            return FakeResponse()

    monkeypatch.setattr(
        "agents.strategist_agent.MemoryManager.get_room_context",
        lambda room, limit=3: "prior strategies",
    )
    monkeypatch.setattr(
        "agents.strategist_agent.MemoryManager.remember_verbatim",
        lambda **kwargs: None,
    )

    portfolio_path = tmp_path / "portfolio.md"
    portfolio_path.write_text("portfolio context", encoding="utf-8")

    strategist = StrategistAgent.__new__(StrategistAgent)
    strategist.llm = FakeLLM()
    strategist.portfolio_path = str(portfolio_path)
    strategist.conversion_playbook = "Use persuasion ethically and make ROI concrete."
    strategist.canva_skill = type(
        "DummyCanvaSkill",
        (),
        {"create_deliverables": staticmethod(lambda strategy_data: {})},
    )()
    strategist.notion_skill = type(
        "DummyNotionSkill",
        (),
        {"scaffold_client_portal": staticmethod(lambda **kwargs: "portal")},
    )()
    strategist.notion_service = type(
        "DummyNotionService",
        (),
        {
            "add_strategy": staticmethod(lambda **kwargs: {"ok": True, "lead_page_id": None}),
            "update_lead_status": staticmethod(lambda **kwargs: {"ok": True}),
        },
    )()
    strategist.pre_flight_check = lambda job_data: "No historical negative constraints found."

    strategist.analyze_lead(
        {
            "title": "AI agent project",
            "description": "Build an agent.",
            "url": "https://example.com/job",
        }
    )

    assert "### EXPERT CONVERSION GUIDELINES" in captured["prompt"]
    assert "Use persuasion ethically and make ROI concrete." in captured["prompt"]

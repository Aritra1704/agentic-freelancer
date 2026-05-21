from agents.pricing_predictor import PricingPredictor
from agents.proposal_engine import ProposalEngine
from core.agent_manager import AgentRegistry
from core.localclaw_adapter import LocalClawAdapter


class FakeLocalClawClient:
    def __init__(self):
        self.actions = []

    def execute_action(self, action):
        self.actions.append(action)
        return {"ok": True, "action": action}


def test_orchestrator_agent_localclaw_flow():
    AgentRegistry.clear()
    AgentRegistry.register("proposal_engine", ProposalEngine(llm=None))
    AgentRegistry.register("pricing_predictor", PricingPredictor())

    proposal = AgentRegistry.get("proposal_engine").execute(
        "generate_proposal",
        {
            "job_title": "Marketplace automation build",
            "job_description": "Build an automation agent with API integrations and dashboard reporting.",
            "freelancer_context": "Engineer with automation and API architecture experience.",
            "technical_doubts": [
                "What system triggers the workflow?",
                "Which portal must the agent operate against?",
                "What level of observability is required?",
            ],
        },
    )
    pricing = AgentRegistry.get("pricing_predictor").execute(
        "estimate_price",
        {
            "job_description": "Build an automation agent with API integrations and dashboard reporting.",
            "budget": "$3,000",
            "technical_doubts": [
                "What system triggers the workflow?",
                "Which portal must the agent operate against?",
                "What level of observability is required?",
            ],
            "suggested_stack": ["Python", "Playwright"],
        },
    )

    client = FakeLocalClawClient()
    adapter = LocalClawAdapter(client)
    dispatch = adapter.execute_text_artifact(
        proposal["artifact"],
        selector="#proposal-cover-letter",
        metadata={"price_estimate": pricing["artifact"]["content"]["recommended_price"]},
    )

    assert proposal["status"] == "success"
    assert pricing["status"] == "success"
    assert dispatch["ok"] is True
    assert client.actions[0]["type"] == "type_text"
    assert client.actions[0]["selector"] == "#proposal-cover-letter"
    assert "Proposal for Marketplace automation build" in client.actions[0]["value"]

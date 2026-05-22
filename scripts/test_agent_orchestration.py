import sys
from pathlib import Path

# Add parent directory to sys.path to allow imports.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agents.pricing_predictor import PricingPredictor
from agents.proposal_agent import ProposalAgent
from core.agent_manager import AgentRegistry
from agents.proposal_engine import ProposalEngine


def test_orchestration():
    AgentRegistry.clear()
    AgentRegistry.register("proposal_engine", ProposalEngine(llm=None))
    AgentRegistry.register("pricing_predictor", PricingPredictor())

    proposal_agent = ProposalAgent()
    input_data = {
        "job_title": "Build a React Dashboard",
        "job_description": "Need a dashboard to track agent tasks.",
        "budget": 1000,
        "freelancer_context": "Senior dev with 10 years experience.",
    }

    response = proposal_agent.execute("generate_proposal", input_data)

    print("Agent Response:")
    print(response)

    assert response["status"] == "success"
    print("\n✅ Orchestration Test Passed!")


if __name__ == "__main__":
    test_orchestration()

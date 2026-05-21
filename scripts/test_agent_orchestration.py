import sys
import os

# Add parent directory to sys.path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent_manager import AgentRegistry
from agents.proposal_engine import ProposalEngine
from agents.pricing_predictor import PricingPredictor
from agents.proposal_agent import ProposalAgent

def test_orchestration():
    # 1. Register agents
    AgentRegistry.register("proposal_engine", ProposalEngine())
    AgentRegistry.register("pricing_predictor", PricingPredictor())
    
    # 2. Instantiate orchestrator
    proposal_agent = ProposalAgent()
    
    # 3. Dummy input
    input_data = {
        "job_title": "Build a React Dashboard",
        "job_description": "Need a dashboard to track agent tasks.",
        "budget": 1000,
        "freelancer_context": "Senior dev with 10 years experience."
    }
    
    # 4. Execute
    response = proposal_agent.execute("generate_proposal", input_data)
    
    print("Agent Response:")
    print(response)
    
    assert response["status"] == "success"
    print("\n✅ Orchestration Test Passed!")

if __name__ == "__main__":
    test_orchestration()

# freelance-os/agents/strategist_agent.py
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from core.llm_factory import LLMFactory

class StrategistAgent:
    """
    The Strategist: Analyzes leads and drafts winning technical proposals.
    Fundamental: 'grill-me' - Identifies risks before proposing solutions.
    """
    def __init__(self):
        self.llm = LLMFactory.get_model_instance("pro")
        self.portfolio_path = "context/portfolio.md"

    def analyze_lead(self, job_data):
        """
        Performs an 'Internal Grill' and generates a technical proposal.
        """
        with open(self.portfolio_path, "r") as f:
            portfolio = f.read()

        prompt = (
            f"As a Senior AI Architect at a Global Bank (DBS), analyze this job: {job_data['title']}. \n"
            f"Description: {job_data.get('description', 'N/A')} \n\n"
            f"My Portfolio Context: {portfolio} \n\n"
            "Generate a HIGH-VALUE TECHNICAL PROPOSAL. Follow this structure strictly:\n\n"
            "1. THE ALIGNMENT (Grill-Me): Start by asking the client 3 high-signal technical questions that prove you've spotted hidden complexities in their request.\n"
            "2. THE PROACTIVE WORKFLOW: Provide a 'Day 1 to Day 3' roadmap. Explain how we use TDD and AI-Native orchestration to deliver an architecturally sound MVP faster than a traditional team.\n"
            "3. THE TECHNICAL EDGE: Explain how the 'Bridge' (Gemini + Local Ollama) will be used to ensure privacy, cost-efficiency, and rapid iteration.\n"
            "4. THE LONG-TERM VALUE: Mention the 'Context Memory Layer' we include with every handoff, so the code remains maintainable by any future agent or human.\n"
            "5. THE PITCH: A concluding summary that emphasizes why choosing a Senior DBS Engineer with an AI-Native workflow is their lowest-risk, highest-ROI choice."
        )

        response = self.llm.invoke(prompt)
        return response.content

if __name__ == "__main__":
    # Test lead for verification
    test_job = {
        "title": "LLM Specialist needed for RAG Pipeline",
        "description": "We need to connect our internal PDF database to a chatbot."
    }
    strategist = StrategistAgent()
    print("--- The Strategist is analyzing lead ---")
    print(strategist.analyze_lead(test_job))

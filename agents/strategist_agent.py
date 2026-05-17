# freelance-os/agents/strategist_agent.py
from core.llm_factory import LLMFactory
from core.memory_manager import MemoryManager
from core.notion_service import NotionService
from core.skill_loader import load_playbook

class StrategistAgent:
    """
    The Strategist: Analyzes leads and drafts winning technical proposals.
    Fundamental: 'grill-me' - Identifies risks before proposing solutions.
    Integrated: 'MemPalace' - Verbatim storage and Spatial context.
    """
    def __init__(self):
        self.llm = LLMFactory.get_model_instance("pro")
        self.portfolio_path = "context/portfolio.md"
        self.notion_service = NotionService()
        self.conversion_playbook = load_playbook("marketing-psychology", max_chars=5000)

    def pre_flight_check(self, job_data):
        """
        Looks for prior failure patterns relevant to the lead's stack or
        client type and converts them into prompt guardrails.
        """
        relevant_failures = MemoryManager.find_relevant_failures(job_data, limit=5)
        if not relevant_failures:
            return "No historical negative constraints found."

        lines = []
        for failure in relevant_failures:
            context_label = failure["context_tag"] or ", ".join(failure["matched_tags"])
            lines.append(
                "- Do not repeat the "
                f"{context_label} failure pattern from the {failure['stage']} stage: "
                f"{failure['pre_mortem_advice']}"
            )

        return "Negative Constraints:\n" + "\n".join(lines)

    def analyze_lead(self, job_data):
        """
        Performs an 'Internal Grill' and generates a technical proposal.
        """
        with open(self.portfolio_path, "r") as f:
            portfolio = f.read()

        # MemPalace: Prioritized Context Loading (Spatial Organization)
        # Load previous winning strategy context from the 'strategy' Room
        previous_strategies = MemoryManager.get_room_context(MemoryManager.ROOM_STRATEGY, limit=3)
        negative_constraints = self.pre_flight_check(job_data)
        conversion_guidelines = self.conversion_playbook or "No conversion playbook available."

        prompt = (
            f"As a Senior AI Architect, analyze this job: {job_data['title']}. \n"
            f"Description: {job_data.get('description', 'N/A')} \n\n"
            f"My Portfolio Context: {portfolio} \n\n"
            f"Historical Strategy Context (MemPalace): {previous_strategies} \n\n"
            f"Historical Failure Guardrails (Negative Constraints): {negative_constraints} \n\n"
            f"### EXPERT CONVERSION GUIDELINES\n{conversion_guidelines}\n\n"
            "Generate a HIGH-VALUE TECHNICAL PROPOSAL. Follow this structure strictly:\n\n"
            "1. THE ALIGNMENT (Grill-Me): Start by asking the client 3 high-signal technical questions that prove you've spotted hidden complexities in their request.\n"
            "2. THE PROACTIVE WORKFLOW: Provide a 'Day 1 to Day 3' roadmap.\n"
            "3. THE TECHNICAL EDGE: Explain the 'Bridge' (Gemini + Local Ollama).\n"
            "4. THE LONG-TERM VALUE: Mention the 'Context Memory Layer' (MemPalace-inspired).\n"
            "5. THE PITCH: Summary of ROI."
        )

        response = self.llm.invoke(prompt)
        proposal_content = response.content

        # MemPalace: Verbatim Storage for Critical Data
        # Save the full generated proposal verbatim for future learning
        MemoryManager.remember_verbatim(
            category=MemoryManager.ROOM_STRATEGY,
            interaction_type="proposal_draft",
            content=proposal_content,
            metadata={"job_url": job_data.get("url"), "job_title": job_data["title"]}
        )

        try:
            strategy_sync = self.notion_service.add_strategy(
                lead_title=job_data["title"],
                lead_url=job_data.get("url"),
                proposal_content=proposal_content,
                suggested_stack=(job_data.get("suggested_stack") or [])[:10],
                quotation=job_data.get("quotation"),
                status="Draft",
            )
            self.notion_service.update_lead_status(
                link=job_data.get("url"),
                title=job_data["title"],
                status="Strategized",
                page_id=job_data.get("notion_page_id") or strategy_sync.get("lead_page_id"),
            )
        except Exception as notion_exc:
            print(f"⚠️ Notion strategy sync failed for '{job_data['title']}': {notion_exc}")

        return proposal_content

if __name__ == "__main__":
    # Test lead for verification
    test_job = {
        "title": "LLM Specialist needed for RAG Pipeline",
        "description": "We need to connect our internal PDF database to a chatbot."
    }
    strategist = StrategistAgent()
    print("--- The Strategist is analyzing lead ---")
    print(strategist.analyze_lead(test_job))

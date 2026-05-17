# freelance-os/main.py
import asyncio
import argparse
import warnings

# Suppress Pydantic/Python 3.14 compatibility warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from agents.scout_agent import ScoutAgent
from agents.lead_processor import LeadProcessor
from agents.strategist_agent import StrategistAgent
from agents.builder_agent import BuilderAgent
from core.memory_manager import MemoryManager

class FreelanceOS:
    """
    The Orchestrator: Connects the Scout, Strategist, and Builder.
    """
    def __init__(self):
        print("🚀 Initializing Freelance-OS: AI-Native Edition")
        self.scout = ScoutAgent()
        self.processor = LeadProcessor()
        self.strategist = StrategistAgent()

    async def run_hunt(self):
        """Phase 1: Scout for new leads."""
        print("\n🔍 Phase 1: Scouting for leads...")
        await self.scout.hunt()
        self.processor.refine_new_leads()
        print("✅ Hunting and refinement complete.")

    def run_strategy(self):
        """Phase 2: Analyze leads and draft proposals."""
        print("\n🧠 Phase 2: Strategizing and drafting proposals...")
        from core.database import SessionLocal, Lead
        db = SessionLocal()
        try:
            # Get refined leads
            leads = db.query(Lead).filter(Lead.status == "refined").all()
            
            if not leads:
                print("ℹ️ No refined leads found. Run 'hunt' first.")
                return

            for lead in leads[:2]:  # Focus on top 2 leads
                # Convert DB model to dict for strategist
                lead_dict = {
                    "title": lead.title,
                    "url": lead.url,
                    "budget": lead.budget,
                    "description": lead.description,
                    "notion_page_id": (lead.raw_data or {}).get("notion_page_id"),
                    "suggested_stack": (lead.raw_data or {}).get("tags", []),
                    "quotation": (lead.raw_data or {}).get("quotation"),
                }
                proposal = self.strategist.analyze_lead(lead_dict)
                print(f"\n--- Proposal for: {lead.title} ---")
                print(proposal)
                
                # Optionally mark as 'applied' or 'strategized'
                lead.status = "strategized"
            
            db.commit()
        except Exception as e:
            print(f"❌ Error in strategy phase: {e}")
        finally:
            db.close()

    def run_build(self, project_name, feature):
        """Phase 3: Execute a project using TDD."""
        print(f"\n🛠 Phase 3: Building project '{project_name}'...")
        builder = BuilderAgent(project_name)
        builder.design_and_build(feature)
        print("✅ Project build complete.")

    @staticmethod
    def run_learn():
        """
        Phase 4: Capture a blameless post-mortem and store it as future guardrail
        advice.
        """
        print("\n🧠 Phase 4: Learning from failure...")
        try:
            observation = input("What went wrong? ").strip()
            stage = input("What stage was this? ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Learning cancelled.")
            return

        if not observation or not stage:
            print("❌ Error: both answers are required for learning.")
            return

        learning = MemoryManager.learn_from_failure(stage=stage, observation=observation)
        pattern_alert = MemoryManager.detect_patterns()
        print("\n✅ Learning captured.")
        print(f"Room: {learning['room']}")
        print(f"Advice: {learning['pre_mortem_advice']}")
        if pattern_alert["should_alert"]:
            print("\n📣 Pattern Alert")
            print(pattern_alert["alert_block"])

async def main():
    parser = argparse.ArgumentParser(description="Freelance-OS CLI")
    parser.add_argument("command", choices=["hunt", "strategize", "build", "full-cycle", "learn"])
    parser.add_argument("--name", help="Project name for building")
    parser.add_argument("--feature", help="Feature description for building")
    
    args = parser.parse_args()

    if args.command == "learn":
        FreelanceOS.run_learn()
        return

    os_instance = FreelanceOS()

    if args.command == "hunt":
        await os_instance.run_hunt()
    elif args.command == "strategize":
        os_instance.run_strategy()
    elif args.command == "build":
        if not args.name or not args.feature:
            print("❌ Error: --name and --feature are required for build command.")
        else:
            os_instance.run_build(args.name, args.feature)
    elif args.command == "full-cycle":
        await os_instance.run_hunt()
        os_instance.run_strategy()

if __name__ == "__main__":
    asyncio.run(main())

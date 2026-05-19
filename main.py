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
from core.database import PipelineStatus, init_db
from core.memory_manager import MemoryManager
from core.orchestrator import Stitcher

class FreelanceOS:
    """
    The Orchestrator: Connects the Scout, Strategist, and Builder.
    """
    def __init__(self, platform="Upwork"):
        print("🚀 Initializing Freelance-OS: AI-Native Edition")
        self.platform = platform
        self.scout = ScoutAgent(platform=platform)
        self.processor = LeadProcessor()
        self.strategist = StrategistAgent()
        self.stitcher = Stitcher()

    async def run_hunt(self, refine=False):
        """Phase 1: Scout for new leads."""
        print(f"\n🔍 Phase 1: Scouting for leads on {self.platform}...")
        await self.scout.hunt()
        if refine:
            self.processor.refine_new_leads()
            print("✅ Hunting and refinement complete.")
        else:
            print("✅ Hunting complete.")

    def run_strategy(self):
        """Phase 2: Analyze leads and draft proposals."""
        print("\n🧠 Phase 2: Strategizing and drafting proposals...")
        try:
            results = self.strategist.strategize_refined_leads(limit=2)
            for lead, proposal in results:
                print(f"\n--- Proposal for: {lead.title} ---")
                print(proposal)
        except Exception as e:
            print(f"❌ Error in strategy phase: {e}")

    def run_build(self, project_name, feature):
        """Phase 3: Execute a project using TDD."""
        print(f"\n🛠 Phase 3: Building project '{project_name}'...")
        builder = BuilderAgent(project_name)
        builder.design_and_build(feature)
        print("✅ Project build complete.")

    async def run_orchestrator(self):
        """
        Executes the stitched pipeline based on current DB state.
        """
        print("\n🪡 Running Stitch Orchestrator...")
        pending = self.stitcher.get_pending_tasks()
        if not pending[PipelineStatus.SCRAPED.value] and not pending[PipelineStatus.REFINED.value]:
            await self.run_hunt(refine=False)
            pending = self.stitcher.get_pending_tasks()

        if pending[PipelineStatus.SCRAPED.value]:
            self.processor.refine_new_leads()
            pending = self.stitcher.get_pending_tasks()

        if pending[PipelineStatus.REFINED.value]:
            self.run_strategy()

        if pending[PipelineStatus.ERROR.value]:
            print(f"⚠️ {len(pending[PipelineStatus.ERROR.value])} leads remain in error state.")
        else:
            print("✅ Stitch orchestrator completed without pending errors.")

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
    parser.add_argument("command", choices=["hunt", "strategize", "build", "full-cycle", "learn", "run-orchestrator"])
    parser.add_argument("--name", help="Project name for building")
    parser.add_argument("--feature", help="Feature description for building")
    parser.add_argument("--platform", default="Upwork", help="Lead platform to scout (Upwork, Fiverr, Contra, Freelancer)")
    parser.add_argument("--refine", action="store_true", help="Immediately refine leads after hunting")
    
    args = parser.parse_args()
    init_db()

    if args.command == "learn":
        FreelanceOS.run_learn()
        return

    os_instance = FreelanceOS(platform=args.platform)

    if args.command == "hunt":
        await os_instance.run_hunt(refine=args.refine)
    elif args.command == "strategize":
        os_instance.run_strategy()
    elif args.command == "build":
        if not args.name or not args.feature:
            print("❌ Error: --name and --feature are required for build command.")
        else:
            os_instance.run_build(args.name, args.feature)
    elif args.command == "full-cycle":
        await os_instance.run_hunt(refine=True)
        os_instance.run_strategy()
    elif args.command == "run-orchestrator":
        await os_instance.run_orchestrator()

if __name__ == "__main__":
    asyncio.run(main())

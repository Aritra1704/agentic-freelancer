# freelance-os/main.py
import asyncio
import argparse
import sys
import os
import json
import warnings

# Suppress Pydantic/Python 3.14 compatibility warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from agents.scout_agent import ScoutAgent
from agents.lead_processor import LeadProcessor
from agents.strategist_agent import StrategistAgent
from agents.builder_agent import BuilderAgent

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
        self.processor.refine("leads/active_leads.json")
        print("✅ Hunting and refinement complete.")

    def run_strategy(self):
        """Phase 2: Analyze leads and draft proposals."""
        print("\n🧠 Phase 2: Strategizing and drafting proposals...")
        try:
            with open("leads/refined_leads.json", "r") as f:
                leads = json.load(f)
            
            for lead in leads[:2]:  # Focus on top 2 leads
                proposal = self.strategist.analyze_lead(lead)
                print(f"\n--- Proposal for: {lead['title']} ---")
                print(proposal)
        except Exception as e:
            print(f"❌ Error in strategy phase: {e}")

    def run_build(self, project_name, feature):
        """Phase 3: Execute a project using TDD."""
        print(f"\n🛠 Phase 3: Building project '{project_name}'...")
        builder = BuilderAgent(project_name)
        builder.design_and_build(feature)
        print("✅ Project build complete.")

async def main():
    parser = argparse.ArgumentParser(description="Freelance-OS CLI")
    parser.add_argument("command", choices=["hunt", "strategize", "build", "full-cycle"])
    parser.add_argument("--name", help="Project name for building")
    parser.add_argument("--feature", help="Feature description for building")
    
    args = parser.parse_args()
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

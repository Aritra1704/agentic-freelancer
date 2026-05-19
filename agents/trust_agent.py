# freelance-os/agents/trust_agent.py
import os
from skills.canva_skill import CanvaSkill
from skills.notion_skill import NotionSkill

class TrustAgent:
    """
    The Trust Agent: Ensures transparency and professional delivery.
    Uses Notion for project tracking and Canva for visual communication.
    """
    def __init__(self, project_name):
        self.project_name = project_name
        self.portal_url = f"https://notion.so/client-portals/{project_name}"
        self.notion_skill = NotionSkill()
        self.canva_skill = CanvaSkill()

    def generate_client_onboarding(self, deliverables=None):
        """
        Drafts the structure for the Notion Client Portal.
        """
        print(f"--- Preparing Notion Client Portal for {self.project_name} ---")
        roadmap = [
            "Phase 1: TDD & Architectural Alignment (Day 1)",
            "Phase 2: Core Logic Implementation & API Specs (Day 2)",
            "Phase 3: Integration & Final Refinement (Day 3)"
        ]
        return self.notion_skill.scaffold_client_portal(
            project_name=self.project_name,
            roadmap=roadmap,
            deliverables=deliverables,
        )

    def create_canva_brief(self, requirements):
        """
        Generates a text-based brief that can be fed into Canva's 'Magic Design'.
        """
        print(f"--- Generating Canva Wireflow Brief ---")
        brief = (
            f"Visual Wireflow for {self.project_name}:\n"
            f"1. Hero Section showing {requirements.get('main_feature')}\n"
            f"2. Dashboard with real-time tracking metrics\n"
            f"3. API Integration diagram using modern architecture symbols"
        )
        return brief

    def prepare_dockerfile(self):
        """
        Generates a standard Dockerfile for the project.
        """
        print(f"--- Generating Docker Deployment Config ---")
        docker_content = (
            "FROM python:3.9-slim\n"
            "WORKDIR /app\n"
            "COPY . /app\n"
            "RUN pip install -r requirements.txt\n"
            "CMD ['python', 'src/logic.py']"
        )
        return docker_content

if __name__ == "__main__":
    trust = TrustAgent("LegalSearchAI")
    print(trust.generate_client_onboarding())
    print(trust.prepare_dockerfile())

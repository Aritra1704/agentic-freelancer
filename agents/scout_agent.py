# freelance-os/agents/scout_agent.py
import asyncio
import json
import os
from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile
from core.llm_factory import LLMFactory
from core.memory_manager import MemoryManager
from core.notion_service import NotionService
from core.skill_loader import load_playbook
from agents.upwork_scout_playwright import UpworkScoutPlaywright

class ScoutAgent:
    def __init__(self, platform="Upwork"):
        self.platform = platform
        self.llm = LLMFactory.get_model_instance("flash")
        self.output_path = "leads/active_leads.json"
        os.makedirs("leads", exist_ok=True)
        self.market_sizing_playbook = load_playbook("market-sizing-analysis", max_chars=4000)
        self.market_opportunity_playbook = load_playbook(
            "startup-business-analyst-market-opportunity",
            max_chars=4000,
        )
        self.notion_service = NotionService()
        
        # Configure persistent browser via BrowserProfile
        self.profile = BrowserProfile(
            user_data_dir="./browser-use-user-data-dir-local"
        )
        self.browser = Browser(
            headless=False,
            browser_profile=self.profile,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )

    def pre_flight_check(self, keywords):
        """
        Queries failure memory for platform and search-keyword-related guardrails
        before the scout opens a target marketplace.
        """
        relevant_failures = MemoryManager.find_relevant_failures(
            {
                "title": " ".join(keywords),
                "description": " ".join(keywords),
                "platform": self.platform,
                "client_type": self.platform,
            },
            limit=5,
        )
        if not relevant_failures:
            return "No historical scouting guardrails found."

        lines = []
        for failure in relevant_failures:
            context_label = failure["context_tag"] or ", ".join(failure["matched_tags"])
            lines.append(
                "- Avoid repeating the "
                f"{context_label} issue from the {failure['stage']} stage: "
                f"{failure['pre_mortem_advice']}"
            )
        return "Scout Guardrails:\n" + "\n".join(lines)

    async def hunt(self, keywords=["Python AI Agent", "LLM Integration", "RAG"]):
        print(f"--- The Scout is starting a hunt on {self.platform} ---")
        negative_constraints = self.pre_flight_check(keywords)
        
        if self.platform.lower() == "upwork":
            playwright_scout = UpworkScoutPlaywright(user_data_dir="./browser-use-user-data-dir-local")
            result = await playwright_scout.hunt(
                keywords=keywords,
                negative_constraints=negative_constraints,
            )
            return result
        
        # Generic browser-use fallback for other platforms
        task = (
            f"Go to {self.platform}.com. You should already be logged in. "
            f"Search for '{', '.join(keywords)}'. "
            f"Historical failure guardrails: {negative_constraints}. "
            "Use the following expert lead-qualification guidelines when deciding which listings are worth capturing. "
            f"### MARKET SIZING GUIDELINES\n{self.market_sizing_playbook or 'No market sizing playbook available.'}\n\n"
            f"### MARKET OPPORTUNITY GUIDELINES\n{self.market_opportunity_playbook or 'No market opportunity playbook available.'}\n\n"
            "Apply those guardrails before retrying any anti-bot, login, or extraction step. "
            "Read the first 5 job listings to find the title, budget, description snippet, and job URL. "
            "IMPORTANT: Once you have the data, you MUST call the 'done' tool and pass the raw JSON array of the jobs as the 'text' argument. "
        )

        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser,
        )

        result = await agent.run()
        leads = self._parse_and_save_to_db(result)
        await self.browser.stop()
        return leads

    def _parse_and_save_to_db(self, result):
        """
        Parses agent result and saves new leads to the database.
        """
        from core.database import SessionLocal, Lead
        import hashlib
        
        content = result.final_result() if hasattr(result, 'final_result') and result.final_result() else "[]"
        
        # Clean markdown
        if content.startswith("```json"): content = content[7:-3].strip()
        elif content.startswith("```"): content = content[3:-3].strip()
        
        try:
            jobs = json.loads(content)
            db = SessionLocal()
            new_count = 0
            created_leads = []
            for job in jobs:
                url = job.get("url", "")
                if not url: continue
                
                # Check duplicate
                if db.query(Lead).filter(Lead.url == url).first():
                    continue
                
                lead_id = hashlib.md5(url.encode()).hexdigest()
                new_lead = Lead(
                    id=lead_id,
                    platform=self.platform,
                    title=job.get("title", "N/A"),
                    url=url,
                    budget=job.get("budget", "Unknown"),
                    description=job.get("description", "N/A"),
                    raw_data=job,
                    status="new"
                )
                db.add(new_lead)
                created_leads.append(new_lead)
                new_count += 1
            
            db.commit()
            self._sync_new_leads_to_notion(db, created_leads)
            db.close()
            print(f"✅ Added {new_count} new leads from {self.platform} to DB.")
            return jobs
        except Exception as e:
            print(f"❌ Error parsing/saving leads: {e}")
            return []

    def _sync_new_leads_to_notion(self, db, created_leads):
        """
        Best-effort Notion sync for newly created leads.
        """
        for lead in created_leads:
            try:
                result = self.notion_service.add_lead(
                    title=lead.title,
                    platform=lead.platform,
                    budget=lead.budget,
                    link=lead.url,
                    status="Scraped",
                    match_score=(lead.raw_data or {}).get("opportunity_score"),
                )
                if result.get("ok") and result.get("page_id"):
                    lead.raw_data = dict(lead.raw_data or {})
                    lead.raw_data["notion_page_id"] = result["page_id"]
            except Exception as exc:
                print(f"⚠️ Notion sync failed for lead '{lead.title}': {exc}")

        if created_leads:
            db.commit()

if __name__ == "__main__":
    scout = ScoutAgent()
    asyncio.run(scout.hunt())

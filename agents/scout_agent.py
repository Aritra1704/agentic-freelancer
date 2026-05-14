# freelance-os/agents/scout_agent.py
import asyncio
import json
import os
from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile
from core.llm_factory import LLMFactory

class ScoutAgent:
    def __init__(self, platform="Upwork"):
        self.platform = platform
        self.llm = LLMFactory.get_model_instance("flash")
        self.output_path = "leads/active_leads.json"
        os.makedirs("leads", exist_ok=True)
        
        # Configure persistent browser via BrowserProfile
        self.profile = BrowserProfile(
            user_data_dir="./browser_data"
        )
        self.browser = Browser(
            headless=False,
            browser_profile=self.profile,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )

    async def hunt(self):
        print(f"--- The Scout is starting a hunt on {self.platform} ---")
        task = (
            f"Go to {self.platform}.com. You should already be logged in. "
            "Search for 'Python AI Agent', 'LLM Integration', and 'RAG'. "
            "Extract the first 5 job listings: title, budget, description snippet, and job URL. "
            "Return ONLY a raw JSON array of objects representing these jobs, without any markdown formatting."
        )

        agent = Agent(
            task=task,
            llm=self.llm,
            browser=self.browser,
        )

        result = await agent.run()
        self._save_leads(result)
        await self.browser.stop()
        return result

    def _save_leads(self, result):
        """
        Parses and saves the leads to the local filesystem.
        """
        print(f"--- The Scout is saving leads to {self.output_path} ---")
        try:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            # Extract final text output from the agent if available
            content = result.final_result() if hasattr(result, 'final_result') and result.final_result() else "[]"
            
            # Clean markdown formatting if present
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            with open(self.output_path, "w") as f:
                f.write(content)
        except Exception as e:
            print(f"Error saving leads: {e}")

if __name__ == "__main__":
    scout = ScoutAgent()
    asyncio.run(scout.hunt())

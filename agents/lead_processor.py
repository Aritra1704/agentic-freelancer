# freelance-os/agents/lead_processor.py
import re
import json
from core.ollama_bridge import OllamaBridge
from core.database import SessionLocal, Lead
from core.notion_service import NotionService
from core.skill_loader import load_playbook

class LeadProcessor:
    """
    Refines raw data from The Scout into clean, structured JSON using Ollama,
    and updates the database.
    """
    def __init__(self):
        self.bridge = OllamaBridge(model="llama3")
        self.notion_service = NotionService()
        self.market_sizing_playbook = load_playbook("market-sizing-analysis", max_chars=3000)
        self.market_opportunity_playbook = load_playbook(
            "startup-business-analyst-market-opportunity",
            max_chars=3000,
        )

    def _extract_json(self, text):
        """
        Robustly extracts a JSON object from text that may contain conversational filler.
        """
        # Remove any potential markdown code blocks first
        text = re.sub(r"```json", "", text)
        text = re.sub(r"```", "", text)
        
        # Look for the first { and the last }
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            json_str = match.group(1).strip()
            # If there's extra data after the main JSON object, try to truncate it
            # This handles cases where LLM output has a JSON object followed by "Here is your JSON"
            try:
                # Basic bracket counting to find the actual end of the object
                count = 0
                for i, char in enumerate(json_str):
                    if char == "{":
                        count += 1
                    elif char == "}":
                        count -= 1
                        if count == 0:
                            return json_str[:i+1]
            except Exception:
                pass
            return json_str
        return text.strip()

    def refine_new_leads(self):
        """
        Processes all leads with status 'new' from the database.
        """
        db = SessionLocal()
        new_leads = db.query(Lead).filter(Lead.status == "new").all()
        
        if not new_leads:
            print("ℹ️ No new leads to refine.")
            db.close()
            return

        print(f"--- Refining {len(new_leads)} new leads ---")
        
        for lead in new_leads:
            print(f"Refining: {lead.title}")
            
            prompt = (
                "You are a data cleaner. Below is raw text from a web scraper. "
                "Extract a valid JSON object for this job. "
                "Required fields: 'title', 'budget', 'url'. "
                "Optional fields: 'opportunity_score' (0-100 integer), 'qualification_notes' (one sentence). "
                "If budget is missing, use 'Unknown'. Return ONLY the JSON. "
                f"### MARKET SIZING GUIDELINES\n{self.market_sizing_playbook or 'No market sizing playbook available.'}\n\n"
                f"### MARKET OPPORTUNITY GUIDELINES\n{self.market_opportunity_playbook or 'No market opportunity playbook available.'}\n\n"
                f"RAW TEXT: {lead.description}"
            )

            response = self.bridge.generate_code(prompt)
            clean_json_str = self._extract_json(response)
            
            try:
                clean_data = json.loads(clean_json_str)
                # Update lead in DB
                lead.title = clean_data.get("title", lead.title)
                lead.budget = clean_data.get("budget", lead.budget)
                merged_raw_data = dict(lead.raw_data or {})
                if "opportunity_score" in clean_data:
                    merged_raw_data["opportunity_score"] = clean_data["opportunity_score"]
                if "qualification_notes" in clean_data:
                    merged_raw_data["qualification_notes"] = clean_data["qualification_notes"]
                
                # Check for Notion page ID if missing in DB but exists in Notion
                if not merged_raw_data.get("notion_page_id"):
                    notion_page = self.notion_service.find_lead_page(link=lead.url, title=lead.title)
                    if notion_page:
                        merged_raw_data["notion_page_id"] = notion_page["id"]

                lead.raw_data = merged_raw_data
                lead.status = "refined"
                
                try:
                    self.notion_service.update_lead_status(
                        link=lead.url,
                        title=lead.title,
                        status="Refined",
                        page_id=merged_raw_data.get("notion_page_id"),
                    )
                except Exception as notion_exc:
                    print(f"⚠️ Notion status sync failed for lead {lead.id}: {notion_exc}")
            except Exception as e:
                print(f"⚠️ Error refining lead {lead.id}: {e}")
                lead.status = "refinement_failed"
        
        db.commit()
        db.close()
        print("✅ Refinement complete.")

    def refine(self, raw_data_path):
        """Legacy support for file-based refining."""
        # ... (keep for compatibility if needed, but we'll use refine_new_leads)
        self.refine_new_leads()

if __name__ == "__main__":
    processor = LeadProcessor()
    processor.refine("freelance-os/leads/active_leads.json")

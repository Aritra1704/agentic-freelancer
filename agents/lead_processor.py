# freelance-os/agents/lead_processor.py
import json
from core.ollama_bridge import OllamaBridge

class LeadProcessor:
    """
    Refines raw data from The Scout into clean, structured JSON using Ollama.
    """
    def __init__(self):
        self.bridge = OllamaBridge(model="llama3")

    def refine(self, raw_data_path):
        with open(raw_data_path, "r") as f:
            raw_content = f.read()

        prompt = (
            "You are a data cleaner. Below is raw text from a web scraper. "
            "Extract a valid JSON list of jobs. Each job must have: 'title', 'budget', 'url'. "
            "If budget is missing, use 'Unknown'. Return ONLY the JSON. "
            f"RAW TEXT: {raw_content}"
        )

        clean_json = self.bridge.generate_code(prompt)
        
        # Save the refined leads
        refined_path = raw_data_path.replace("active_leads", "refined_leads")
        with open(refined_path, "w") as f:
            f.write(clean_json)
        print(f"--- Refined leads saved to {refined_path} ---")

if __name__ == "__main__":
    processor = LeadProcessor()
    processor.refine("freelance-os/leads/active_leads.json")

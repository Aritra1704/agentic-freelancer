import os
import requests
from dotenv import load_dotenv

load_dotenv("freelance-os/.env")

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
LEADS_DB_ID = "36246136033f81338087f47d95afd853"
STRATEGY_DB_ID = "36246136033f81a08817ece9f2021bd6"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def add_lead(title, platform, budget, link):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": LEADS_DB_ID},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Platform": {"select": {"name": platform}},
            "Budget": {"number": budget},
            "Link": {"url": link},
            "Status": {"select": {"name": "Scraped"}}
        }
    }
    res = requests.post(url, headers=HEADERS, json=data)
    return res.json()

def add_strategy(name, lead_name, stack, quote):
    url = "https://api.notion.com/v1/pages"
    data = {
        "parent": {"database_id": STRATEGY_DB_ID},
        "properties": {
            "Strategy Name": {"title": [{"text": {"content": name}}]},
            "Lead": {"rich_text": [{"text": {"content": lead_name}}]},
            "Suggested Stack": {"multi_select": [{"name": s} for s in stack]},
            "Quotation": {"number": quote},
            "Status": {"select": {"name": "Draft"}}
        }
    }
    res = requests.post(url, headers=HEADERS, json=data)
    return res.json()

def add_sop_blocks(parent_page_id):
    url = f"https://api.notion.com/v1/blocks/{parent_page_id}/children"
    data = {
        "children": [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🌊 Freelance-OS Workflow Guide"}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": "Follow these steps to land and execute your next AI project."}}]}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Phase 1: Hunting (The Scout)"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Run `python main.py hunt` to scrape new leads."}}]}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Phase 2: Strategy (The Strategist)"}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Review leads in the 'Freelance Leads' database."}}]}
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Run `python main.py strategize` to generate technical plans."}}]}
            }
        ]
    }
    requests.patch(url, headers=HEADERS, json=data)

if __name__ == "__main__":
    print("🛠 Creating sample workflow data...")
    lead = add_lead("AI Agent for E-commerce", "Upwork", 1500, "https://upwork.com/jobs/123")
    print(f"✅ Added Lead: {lead.get('id')}")
    
    strategy = add_strategy("Agentic RAG Strategy", "AI Agent for E-commerce", ["Python", "Gemini", "Pinecone"], 2000)
    print(f"✅ Added Strategy: {strategy.get('id')}")
    
    print("📖 Adding Workflow Guide to Parent Page...")
    add_sop_blocks(os.getenv("NOTION_PARENT_PAGE_ID"))
    print("🎉 Workflow setup complete!")

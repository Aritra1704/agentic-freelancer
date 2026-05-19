import os
import requests
from dotenv import load_dotenv

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def create_database(parent_id, title, properties):
    url = "https://api.notion.com/v1/databases"
    data = {
        "parent": {"type": "page_id", "page_id": parent_id},
        "title": [{"type": "text", "text": {"content": title}}],
        "properties": properties
    }
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code == 200:
        print(f"✅ Created Database: {title}")
        return response.json()["id"]
    else:
        print(f"❌ Failed to create {title}: {response.text}")
        return None

def main():
    if not NOTION_TOKEN or not PARENT_PAGE_ID:
        print("❌ Error: NOTION_API_KEY and NOTION_PARENT_PAGE_ID must be set in .env")
        return

    print("🚀 Bootstrapping Freelance-OS Notion Workspace...")

    # 1. Leads Database
    leads_props = {
        "Name": {"title": {}},
        "Platform": {"select": {"options": [
            {"name": "Upwork", "color": "green"},
            {"name": "Contra", "color": "blue"},
            {"name": "LinkedIn", "color": "gray"}
        ]}},
        "Budget": {"number": {"format": "dollar"}},
        "Link": {"url": {}},
        "Status": {"select": {"options": [
            {"name": "Scraped", "color": "gray"},
            {"name": "Refined", "color": "yellow"},
            {"name": "Strategized", "color": "orange"},
            {"name": "Applied", "color": "blue"},
            {"name": "Won", "color": "green"},
            {"name": "Lost", "color": "red"}
        ]}},
        "Match Score": {"number": {}}
    }
    leads_db_id = create_database(PARENT_PAGE_ID, "Freelance Leads", leads_props)

    # 2. Strategy Database
    strategy_props = {
        "Strategy Name": {"title": {}},
        "Lead": {"rich_text": {}},  # Simplified to text for bootstrap stability
        "Suggested Stack": {"multi_select": {}},
        "Quotation": {"number": {"format": "dollar"}},
        "Pitch Content": {"rich_text": {}},
        "Status": {"select": {"options": [
            {"name": "Draft", "color": "gray"},
            {"name": "Ready", "color": "green"}
        ]}}
    }
    # Note: Creating relations via API can be tricky if both aren't created. 
    # For simplicity, we create them as standalone first or use text fields.
    strategy_db_id = create_database(PARENT_PAGE_ID, "Strategy Pipeline", strategy_props)

    # 3. Active Projects
    project_props = {
        "Project Name": {"title": {}},
        "Client": {"rich_text": {}},
        "Status": {"select": {"options": [
            {"name": "Scaffolding", "color": "gray"},
            {"name": "In Progress", "color": "blue"},
            {"name": "Testing", "color": "purple"},
            {"name": "Delivered", "color": "green"}
        ]}},
        "Deadline": {"date": {}}
    }
    projects_db_id = create_database(PARENT_PAGE_ID, "Active Projects", project_props)

    print("\n🎉 Bootstrap complete! Check your Notion.")
    print("\nAdd these to your .env:")
    print(f"NOTION_LEADS_DB_ID=\"{leads_db_id}\"")
    print(f"NOTION_STRATEGY_DB_ID=\"{strategy_db_id}\"")
    print(f"# Active Projects DB ID: {projects_db_id}")

if __name__ == "__main__":
    main()

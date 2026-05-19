import os
import requests
from dotenv import load_dotenv

load_dotenv("freelance-os/.env")

NOTION_TOKEN = os.getenv("NOTION_API_KEY")
PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def inject_architecture_hub(parent_page_id):
    url = f"https://api.notion.com/v1/blocks/{parent_page_id}/children"
    
    # Define the Rich Architecture Blocks
    children = [
        # Divider
        {"object": "block", "type": "divider", "divider": {}},
        
        # 1. System Architecture Section
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {"rich_text": [{"type": "text", "text": {"content": "🏗️ Freelance-OS: System Architecture"}}, {"type": "text", "text": {"content": " (AI-Native)"}, "annotations": {"italic": True, "color": "blue"}}]}
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [{"type": "text", "text": {"content": "Freelance-OS is a multi-agent orchestrator that automates the lifecycle of a software contract: from scraping job boards to TDD-based code execution."}}],
                "icon": {"emoji": "🚀"},
                "color": "blue_background"
            }
        },

        # 2. Modular Stages (Toggle)
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🧩 Modular Stages & Core Agents"}}]}
        },
        {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "1. The Scout (Lead Discovery)"}, "annotations": {"bold": True}}],
                "children": [
                    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Tools: Playwright, browser-use, Gemini 1.5 Flash"}}]}},
                    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Action: Navigates job boards, bypasses auth, extracts DOM structure to JSON."}}]}}
                ]
            }
        },
        {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "2. The Strategist (Proposal Logic)"}, "annotations": {"bold": True}}],
                "children": [
                    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Tools: Gemini 1.5 Pro, local context (portfolio.md)"}}]}},
                    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Action: 'Grill-Me' sessions to identify client risks and draft winning technical HLDs."}}]}}
                ]
            }
        },
        {
            "object": "block",
            "type": "toggle",
            "toggle": {
                "rich_text": [{"type": "text", "text": {"content": "3. The Builder (TDD Execution)"}, "annotations": {"bold": True}}],
                "children": [
                    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Tools: Ollama (Llama 3), Pytest, Gemini CLI"}}]}},
                    {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": "Action: Scaffolds project, generates failing tests, implements code until green."}}]}}
                ]
            }
        },

        # 3. Data Flow Diagram (Code Block)
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🔄 Data Flow Structure"}}]}
        },
        {
            "object": "block",
            "type": "code",
            "code": {
                "caption": [{"type": "text", "text": {"content": "Mermaid.js Flowchart (Copy to Mermaid Live Editor if needed)"}}],
                "language": "plain text",
                "rich_text": [{"type": "text", "text": {"content": "graph TD\n    A[Web/Job Boards] -->|Scrape| B(Scout Agent)\n    B -->|Save Raw| C[(PostgreSQL/Notion)]\n    C -->|Feed Context| D(Strategist Agent)\n    D -->|HLD/LLD| E(User Approval)\n    E -->|Scaffold| F(Builder Agent)\n    F -->|Test/Code Loop| G[Final Delivery]\n    G -->|Update| H[(Notion Client Portal)]"}}]
            }
        },

        # 4. Tech Stack Matrix
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "🛠️ Tech Stack & Skills"}}] }
        },
        {
            "object": "block",
            "type": "table",
            "table": {
                "table_width": 3,
                "has_column_header": True,
                "has_row_header": False,
                "children": [
                    {
                        "type": "table_row",
                        "table_row": {"cells": [[{"type": "text", "text": {"content": "Layer"}}], [{"type": "text", "text": {"content": "Technology"}}], [{"type": "text", "text": {"content": "Model/Library"}}]]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [
                            [{"type": "text", "text": {"content": "Intelligence"}}], 
                            [{"type": "text", "text": {"content": "Gemini API / Ollama"}}], 
                            [{"type": "text", "text": {"content": "1.5 Pro / Llama 3"}}]
                        ]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [
                            [{"type": "text", "text": {"content": "Orchestration"}}], 
                            [{"type": "text", "text": {"content": "Python / MCP"}}], 
                            [{"type": "text", "text": {"content": "LangChain / Stdio"}}]
                        ]}
                    },
                    {
                        "type": "table_row",
                        "table_row": {"cells": [
                            [{"type": "text", "text": {"content": "Persistence"}}], 
                            [{"type": "text", "text": {"content": "Notion API / SQL"}}], 
                            [{"type": "text", "text": {"content": "notion-client / SQLAlchemy"}}]
                        ]}
                    }
                ]
            }
        }
    ]
    
    print(f"📡 Sending {len(children)} architecture blocks to Notion...")
    response = requests.patch(url, headers=HEADERS, json={"children": children})
    if response.status_code == 200:
        print("✅ Architecture Hub injected successfully!")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    if not PARENT_PAGE_ID:
        print("❌ PARENT_PAGE_ID not found in .env")
    else:
        inject_architecture_hub(PARENT_PAGE_ID)

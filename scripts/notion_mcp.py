import os
import asyncio
from mcp.server import Server
from mcp.types import Tool, TextContent
from dotenv import load_dotenv
from core.notion_service import NotionService

load_dotenv()

# Initialize MCP Server
app = Server("notion-mcp")
notion = NotionService(leads_db_id=os.getenv("NOTION_LEADS_DB_ID"))

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="add_notion_lead",
            description="Add a new lead to the Freelance Leads database in Notion",
            input_schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Project title"},
                    "platform": {"type": "string", "description": "Platform (Upwork, Contra, etc.)"},
                    "budget": {"type": "number", "description": "Budget amount"},
                    "link": {"type": "string", "description": "URL to the job post"}
                },
                "required": ["title", "platform", "budget", "link"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name, arguments):
    if name == "add_notion_lead":
        result = notion.add_lead(
            title=arguments["title"],
            platform=arguments["platform"],
            budget=arguments["budget"],
            link=arguments["link"],
        )
        return [TextContent(type="text", text=str(result))]
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

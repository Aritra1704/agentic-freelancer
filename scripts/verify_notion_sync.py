from core.database import SessionLocal, Lead
from core.notion_service import NotionService


def main():
    notion = NotionService()
    notion_index = notion.fetch_lead_index()

    db = SessionLocal()
    try:
        leads = db.query(Lead).all()
    finally:
        db.close()

    missing_in_notion = []
    status_mismatches = []

    for lead in leads:
        notion_lead = notion_index.get(lead.url)
        if not notion_lead:
            missing_in_notion.append({"title": lead.title, "url": lead.url, "status": lead.status})
            continue

        stored_page_id = (lead.raw_data or {}).get("notion_page_id")
        if stored_page_id and stored_page_id != notion_lead["page_id"]:
            status_mismatches.append(
                {
                    "title": lead.title,
                    "url": lead.url,
                    "local_page_id": stored_page_id,
                    "notion_page_id": notion_lead["page_id"],
                }
            )

    print("=== Notion Sync Report ===")
    print(f"Local leads checked: {len(leads)}")
    print(f"Notion leads indexed: {len(notion_index)}")
    print(f"Missing in Notion: {len(missing_in_notion)}")
    print(f"Page ID mismatches: {len(status_mismatches)}")

    if missing_in_notion:
        print("\nLeads missing in Notion:")
        for entry in missing_in_notion:
            print(f"- {entry['title']} | {entry['status']} | {entry['url']}")

    if status_mismatches:
        print("\nLead page ID mismatches:")
        for entry in status_mismatches:
            print(
                f"- {entry['title']} | local={entry['local_page_id']} | notion={entry['notion_page_id']}"
            )


if __name__ == "__main__":
    main()

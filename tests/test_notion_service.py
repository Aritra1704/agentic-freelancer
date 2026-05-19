from core.notion_service import NotionService


class FakePagesAPI:
    def __init__(self):
        self.created = []
        self.updated = []

    def create(self, **kwargs):
        self.created.append(kwargs)
        return {"id": "page-created"}

    def update(self, **kwargs):
        self.updated.append(kwargs)
        return {"id": kwargs["page_id"]}


class FakeDatabasesAPI:
    def __init__(self, query_results=None, schemas=None):
        self.query_results = list(query_results or [])
        self.schemas = schemas or {}
        self.query_calls = []
        self.retrieve_calls = []

    def query(self, **kwargs):
        self.query_calls.append(kwargs)
        if self.query_results:
            return self.query_results.pop(0)
        return {"results": []}

    def retrieve(self, **kwargs):
        self.retrieve_calls.append(kwargs)
        database_id = kwargs["database_id"]
        return {"properties": self.schemas.get(database_id, {})}


class FakeNotionClient:
    def __init__(self, query_results=None, schemas=None):
        self.pages = FakePagesAPI()
        self.databases = FakeDatabasesAPI(query_results=query_results, schemas=schemas)


def test_add_lead_creates_page_when_no_match_exists():
    client = FakeNotionClient(query_results=[{"results": []}, {"results": []}])
    service = NotionService(
        client=client,
        leads_db_id="leads-db",
        strategy_db_id="strategy-db",
        notion_token="token",
    )

    result = service.add_lead(
        title="AI Agent Build",
        platform="Upwork",
        budget="$1,200 fixed",
        link="https://example.com/job/1",
    )

    assert result["ok"] is True
    assert result["action"] == "created"
    payload = client.pages.created[0]
    assert payload["parent"]["database_id"] == "leads-db"
    assert payload["properties"]["Budget"]["number"] == 1200.0
    assert payload["properties"]["Status"]["select"]["name"] == "Scraped"


def test_add_strategy_links_relation_when_database_uses_relation_property():
    client = FakeNotionClient(
        query_results=[
            {"results": [{"id": "lead-page-1"}]},
            {"results": []},
        ],
        schemas={
            "strategy-db": {
                "Lead": {"type": "relation"},
                "Pitch Content": {"type": "rich_text"},
            }
        },
    )
    service = NotionService(
        client=client,
        leads_db_id="leads-db",
        strategy_db_id="strategy-db",
        notion_token="token",
    )

    result = service.add_strategy(
        lead_title="RAG Pipeline",
        lead_url="https://example.com/job/2",
        proposal_content="Detailed proposal body",
        suggested_stack=["Python", "Postgres"],
        quotation=2500,
    )

    assert result["ok"] is True
    payload = client.pages.created[0]
    assert payload["properties"]["Lead"] == {"relation": [{"id": "lead-page-1"}]}
    assert payload["properties"]["Quotation"]["number"] == 2500
    assert "Pitch Content" in payload["properties"]


def test_update_lead_status_updates_existing_page():
    client = FakeNotionClient(query_results=[{"results": [{"id": "lead-page-9"}]}])
    service = NotionService(
        client=client,
        leads_db_id="leads-db",
        strategy_db_id="strategy-db",
        notion_token="token",
    )

    result = service.update_lead_status(
        link="https://example.com/job/9",
        title="Lead 9",
        status="Strategized",
    )

    assert result["ok"] is True
    assert client.pages.updated[0]["page_id"] == "lead-page-9"
    assert client.pages.updated[0]["properties"]["Status"]["select"]["name"] == "Strategized"

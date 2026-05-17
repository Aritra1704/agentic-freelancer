import os
import time
from functools import lru_cache

from dotenv import load_dotenv

try:
    from notion_client import Client
except ImportError:  # pragma: no cover - dependency may be absent in test env
    Client = None


load_dotenv()


class NotionService:
    """
    Centralized Notion integration service for lead and strategy sync.
    Degrades safely when Notion is not configured.
    """

    def __init__(
        self,
        client=None,
        notion_token=None,
        leads_db_id=None,
        strategy_db_id=None,
        retry_attempts=3,
        retry_delay=0.5,
    ):
        self.notion_token = notion_token or os.getenv("NOTION_API_KEY")
        self.leads_db_id = leads_db_id or os.getenv("NOTION_LEADS_DB_ID")
        self.strategy_db_id = strategy_db_id or os.getenv("NOTION_STRATEGY_DB_ID")
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.client = client
        self.enabled = bool(self.notion_token and Client and (self.leads_db_id or self.strategy_db_id))

        if self.client is None and self.enabled:
            self.client = Client(auth=self.notion_token)

    def add_lead(self, title, platform, budget, link, status="Scraped", match_score=None):
        """
        Creates or updates a lead row in Notion and returns the page id when available.
        """
        if not self._can_use_database(self.leads_db_id):
            return self._disabled_result("lead_sync_disabled")

        existing_page = self.find_lead_page(link=link, title=title)
        properties = {
            "Name": {"title": [{"text": {"content": title}}]},
            "Platform": {"select": {"name": platform}},
            "Budget": self._number_property(budget),
            "Link": {"url": link},
            "Status": {"select": {"name": status}},
        }
        if match_score is not None:
            properties["Match Score"] = {"number": match_score}

        if existing_page:
            self._with_retries(
                self.client.pages.update,
                page_id=existing_page["id"],
                properties=properties,
            )
            return {"ok": True, "page_id": existing_page["id"], "action": "updated"}

        response = self._with_retries(
            self.client.pages.create,
            parent={"database_id": self.leads_db_id},
            properties=properties,
        )
        return {"ok": True, "page_id": response["id"], "action": "created"}

    def add_strategy(
        self,
        lead_title,
        lead_url,
        proposal_content,
        suggested_stack=None,
        quotation=None,
        status="Draft",
    ):
        """
        Creates or updates a strategy row in Notion and links it back to the lead.
        """
        if not self._can_use_database(self.strategy_db_id):
            return self._disabled_result("strategy_sync_disabled")

        lead_page = self.find_lead_page(link=lead_url, title=lead_title)
        lead_reference = self._lead_reference_property(lead_title, lead_url, lead_page)
        strategy_name = f"Strategy - {lead_title}"

        properties = {
            "Strategy Name": {"title": [{"text": {"content": strategy_name}}]},
            "Lead": lead_reference,
            "Status": {"select": {"name": status}},
        }
        if suggested_stack:
            properties["Suggested Stack"] = {
                "multi_select": [{"name": item} for item in suggested_stack[:10]]
            }
        if quotation is not None:
            properties["Quotation"] = {"number": quotation}
        if self._database_has_property(self.strategy_db_id, "Pitch Content"):
            properties["Pitch Content"] = {
                "rich_text": [{"text": {"content": proposal_content[:1900]}}]
            }

        existing_page = self.find_strategy_page(lead_url=lead_url, lead_title=lead_title)
        if existing_page:
            self._with_retries(
                self.client.pages.update,
                page_id=existing_page["id"],
                properties=properties,
            )
            return {
                "ok": True,
                "page_id": existing_page["id"],
                "lead_page_id": lead_page["id"] if lead_page else None,
                "action": "updated",
            }

        response = self._with_retries(
            self.client.pages.create,
            parent={"database_id": self.strategy_db_id},
            properties=properties,
        )
        return {
            "ok": True,
            "page_id": response["id"],
            "lead_page_id": lead_page["id"] if lead_page else None,
            "action": "created",
        }

    def update_lead_status(self, link=None, title=None, status="Strategized", page_id=None):
        """
        Updates the lead pipeline status in Notion.
        """
        if not self._can_use_database(self.leads_db_id):
            return self._disabled_result("lead_sync_disabled")

        target_page = {"id": page_id} if page_id else self.find_lead_page(link=link, title=title)
        if not target_page:
            return {"ok": False, "reason": "lead_not_found"}

        self._with_retries(
            self.client.pages.update,
            page_id=target_page["id"],
            properties={"Status": {"select": {"name": status}}},
        )
        return {"ok": True, "page_id": target_page["id"], "status": status}

    def find_lead_page(self, link=None, title=None):
        if not self._can_use_database(self.leads_db_id):
            return None

        for filter_payload in self._build_lead_search_filters(link=link, title=title):
            result = self._safe_query(
                database_id=self.leads_db_id,
                filter=filter_payload,
                page_size=1,
            )
            if result.get("results"):
                return result["results"][0]
        return None

    def find_strategy_page(self, lead_url=None, lead_title=None):
        if not self._can_use_database(self.strategy_db_id):
            return None

        filters = []
        lead_property_type = self._database_property_type(self.strategy_db_id, "Lead")
        if lead_url and lead_property_type == "rich_text":
            filters.append(
                {
                    "property": "Lead",
                    "rich_text": {"contains": lead_url},
                }
            )
        if lead_title:
            filters.append(
                {
                    "property": "Strategy Name",
                    "title": {"contains": lead_title},
                }
            )

        for filter_payload in filters:
            result = self._safe_query(
                database_id=self.strategy_db_id,
                filter=filter_payload,
                page_size=1,
            )
            if result.get("results"):
                return result["results"][0]
        return None

    def fetch_lead_index(self):
        """
        Returns a URL-indexed snapshot of Notion leads for sync verification.
        """
        if not self._can_use_database(self.leads_db_id):
            return {}

        result = self._safe_query(
            database_id=self.leads_db_id,
            page_size=100,
        )
        index = {}
        for page in result.get("results", []):
            properties = page.get("properties", {})
            link = properties.get("Link", {}).get("url")
            title_chunks = properties.get("Name", {}).get("title", [])
            title = "".join(chunk.get("plain_text", "") for chunk in title_chunks)
            if link:
                index[link] = {"page_id": page["id"], "title": title}
        return index

    def _safe_query(self, database_id, **kwargs):
        """
        Executes a database query using the library's .query method if available,
        otherwise falls back to direct requests or the search API.
        """
        # 1. Try DataSources (New SDK version)
        if hasattr(self.client, "data_sources") and hasattr(self.client.data_sources, "query"):
            try:
                return self._with_retries(
                    self.client.data_sources.query,
                    data_source_id=database_id,
                    **kwargs
                )
            except Exception:
                pass
        
        # 2. Try Databases (Old SDK version)
        if hasattr(self.client, "databases") and hasattr(self.client.databases, "query"):
            try:
                return self._with_retries(
                    self.client.databases.query,
                    database_id=database_id,
                    **kwargs
                )
            except Exception:
                pass
        
        # 3. Try Search API as a high-signal fallback for finding pages
        # If we are looking for a specific lead by URL/Title, search is actually very good
        if "filter" in kwargs:
            try:
                filter_obj = kwargs["filter"]
                search_query = ""
                # Extract plain text search term from common filter structures
                if "url" in filter_obj.get(next(iter(filter_obj.keys()), ""), {}):
                    search_query = filter_obj[next(iter(filter_obj.keys()))]["url"].get("equals", "")
                elif "title" in filter_obj.get(next(iter(filter_obj.keys()), ""), {}):
                    search_query = filter_obj[next(iter(filter_obj.keys()))]["title"].get("equals", "") or \
                                   filter_obj[next(iter(filter_obj.keys()))]["title"].get("contains", "")
                
                if search_query:
                    search_results = self._with_retries(
                        self.client.search,
                        query=search_query,
                        page_size=1
                    )
                    # Filter results to ensure they belong to our target database
                    filtered_results = [
                        r for r in search_results.get("results", [])
                        if r.get("parent", {}).get("database_id") == database_id.replace("-", "") or \
                           r.get("parent", {}).get("database_id") == database_id
                    ]
                    if filtered_results:
                        return {"results": filtered_results}
            except Exception:
                pass

        # 4. Try direct request with data_sources path
        try:
            return self._with_retries(
                self.client.request,
                path=f"data_sources/{database_id}/query",
                method="POST",
                body=kwargs
            )
        except Exception:
            # 5. Final fallback to databases path
            return self._with_retries(
                self.client.request,
                path=f"databases/{database_id}/query",
                method="POST",
                body=kwargs
            )

    def _lead_reference_property(self, lead_title, lead_url, lead_page):
        property_type = self._database_property_type(self.strategy_db_id, "Lead")
        if property_type == "relation" and lead_page:
            return {"relation": [{"id": lead_page["id"]}]}

        rich_text_value = lead_title
        if lead_url:
            rich_text_value = f"{lead_title} | {lead_url}"
        return {"rich_text": [{"text": {"content": rich_text_value[:1900]}}]}

    def _build_lead_search_filters(self, link=None, title=None):
        filters = []
        if link:
            filters.append({"property": "Link", "url": {"equals": link}})
        if title:
            filters.append({"property": "Name", "title": {"equals": title}})
            filters.append({"property": "Name", "title": {"contains": title}})
        return filters

    def _number_property(self, value):
        number = self._parse_budget(value)
        return {"number": number}

    def _parse_budget(self, value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)

        digits = []
        decimal_seen = False
        for char in str(value):
            if char.isdigit():
                digits.append(char)
            elif char == "." and not decimal_seen:
                digits.append(char)
                decimal_seen = True

        if not digits:
            return None
        try:
            return float("".join(digits))
        except ValueError:
            return None

    @lru_cache(maxsize=8)
    def _database_schema(self, database_id):
        if not self._can_use_database(database_id):
            return {}
        
        # Try retrieving as data_source first, then database
        try:
            if hasattr(self.client, "data_sources"):
                response = self._with_retries(self.client.data_sources.retrieve, data_source_id=database_id)
                if response and "properties" in response:
                    return response.get("properties", {})
        except Exception:
            pass

        try:
            # Try with hyphens just in case the library version requires them for this specific endpoint
            hid = database_id if "-" in database_id else f"{database_id[:8]}-{database_id[8:12]}-{database_id[12:16]}-{database_id[16:20]}-{database_id[20:]}"
            for test_id in [database_id, hid]:
                try:
                    response = self._with_retries(self.client.databases.retrieve, database_id=test_id)
                    if response and "properties" in response:
                        return response.get("properties", {})
                except Exception:
                    continue
        except Exception:
            pass

        # If schema retrieval fails, return a minimal working schema for the known databases
        # to allow page creation to proceed even if we can't query/verify properties
        if database_id.replace("-", "") == self.leads_db_id.replace("-", ""):
            return {"Name": {"type": "title"}, "Status": {"type": "select"}, "Link": {"type": "url"}}
        if database_id.replace("-", "") == self.strategy_db_id.replace("-", ""):
            return {"Strategy Name": {"type": "title"}, "Status": {"type": "select"}}
            
        return {}

    def _database_property_type(self, database_id, property_name):
        return self._database_schema(database_id).get(property_name, {}).get("type")

    def _database_has_property(self, database_id, property_name):
        return property_name in self._database_schema(database_id)

    def _with_retries(self, operation, **kwargs):
        last_error = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                return operation(**kwargs)
            except Exception as exc:  # pragma: no cover - network/client behavior
                last_error = exc
                if attempt == self.retry_attempts:
                    raise
                time.sleep(self.retry_delay * attempt)
        raise last_error

    def _can_use_database(self, database_id):
        return bool(self.client and database_id)

    def _disabled_result(self, reason):
        return {"ok": False, "reason": reason}

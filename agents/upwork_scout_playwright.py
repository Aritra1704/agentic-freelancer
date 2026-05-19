import asyncio
import json
import os
import random
from playwright.async_api import async_playwright
from core.database import Lead, SessionLocal
from core.notion_service import NotionService
from core.orchestrator import Stitcher

class UpworkScoutPlaywright:
    def __init__(self, user_data_dir="./browser-use-user-data-dir-local", platform="Upwork"):
        self.user_data_dir = user_data_dir
        self.output_path = "leads/active_leads.json"
        self.platform = platform
        self.notion_service = NotionService()
        self.stitcher = Stitcher()

    async def hunt(self, keywords=["Python AI Agent", "LLM Integration", "RAG"], negative_constraints=""):
        print(f"--- Upwork Playwright Scout is starting a hunt ---")
        if negative_constraints and "No historical scouting guardrails found." not in negative_constraints:
            print(f"🧠 Scout guardrails loaded:\n{negative_constraints}")
        
        async with async_playwright() as p:
            # Launch persistent context
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.user_data_dir,
                headless=False,
                channel="chrome",
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--disable-gpu"
                ]
            )
            
            page = await context.new_page()
            page.set_default_timeout(60000)
            if negative_constraints and any(
                keyword in negative_constraints.lower()
                for keyword in ("cloudflare", "anti-bot", "stealth", "automation")
            ):
                await page.set_extra_http_headers(
                    {
                        "Accept-Language": "en-US,en;q=0.9",
                        "Upgrade-Insecure-Requests": "1",
                        "Cache-Control": "max-age=0",
                    }
                )
            await self._random_delay()
            
            # Go to Upwork search
            query = " ".join(keywords)
            search_url = f"https://www.upwork.com/nx/search/jobs/?q={query}&sort=recency"
            
            print(f"🌐 Navigating to: {search_url}")
            await page.goto(search_url)
            await self._human_scroll(page)
            
            # Wait for job listings to load
            try:
                await self._wait_for_job_tiles(page)
            except Exception as e:
                print(f"⚠️ Warning: Job tiles not found or timed out. Checking if logged in...")
                if "login" in page.url:
                    print("❌ Error: Not logged in. Please run login_to_upwork.py first.")
                    await context.close()
                    return []
                
            # Extract jobs
            jobs = []
            job_tiles = await page.query_selector_all('article.job-tile')
            
            db = SessionLocal()
            new_leads_count = 0
            created_leads = []

            for tile in job_tiles[:10]: # Increased to 10
                try:
                    title_elem = await self._query_first(tile, [
                        'h2.job-tile-title a',
                        '[data-test="job-title-link"]',
                        'a[data-test="job-tile-title-link"]',
                    ])
                    title = await title_elem.inner_text() if title_elem else "N/A"
                    url = await title_elem.get_attribute('href') if title_elem else ""
                    if url:
                        if url.startswith('/'):
                            url = "https://www.upwork.com" + url
                        elif not url.startswith('http'):
                            url = "https://www.upwork.com/" + url
                        
                    # Remove query params from URL for unique identification
                    clean_url = url.split('?')[0] if url else ""
                    
                    if not clean_url:
                        continue

                    # Check for duplicates in DB
                    existing_lead = db.query(Lead).filter(Lead.url == clean_url).first()
                    if existing_lead:
                        print(f"⏭️ Skipping existing lead: {title[:30]}...")
                        continue

                    description_elem = await self._query_first(tile, [
                        '.job-tile-description',
                        '[data-test="job-description-text"]',
                        '[data-test="UpCLineClamp JobDescription"]',
                    ])
                    description = await description_elem.inner_text() if description_elem else "N/A"
                    
                    budget_elem = await self._query_first(tile, [
                        '.job-tile-info-list',
                        '[data-test="job-type-label"]',
                        '[data-test="is-fixed-price"]',
                    ])
                    budget = await budget_elem.inner_text() if budget_elem else "N/A"
                    
                    job_data = {
                        "title": title.strip(),
                        "url": clean_url,
                        "description": description.strip(),
                        "budget": budget.strip()
                    }
                    if len(jobs) < 3:
                        job_data.update(await self._enrich_job_details(context, clean_url))
                    
                    # Save to DB
                    new_lead = self.stitcher.create_lead(
                        platform=self.platform,
                        title=job_data["title"],
                        url=clean_url,
                        budget=job_data["budget"],
                        description=job_data["description"],
                        raw_data=job_data,
                        db=db,
                    )
                    created_leads.append(new_lead)
                    jobs.append(job_data)
                    new_leads_count += 1
                    await self._random_delay(0.2, 0.8)
                except Exception as e:
                    print(f"⚠️ Error parsing a job tile: {e}")
            
            db.commit()
            self._sync_new_leads_to_notion(db, created_leads)
            db.close()
            
            print(f"✅ Found {len(job_tiles)} tiles, added {new_leads_count} new leads.")
            
            # Still save to JSON for backward compatibility if needed
            if jobs:
                os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
                with open(self.output_path, "w") as f:
                    json.dump(jobs, f, indent=2)
                
            await context.close()
            return jobs

    async def _wait_for_job_tiles(self, page):
        selectors = [
            'article.job-tile',
            '[data-test="job-tile-list"] article',
            '[data-ev-label="job_tile"]',
        ]
        for selector in selectors:
            try:
                await page.wait_for_selector(selector, timeout=5000)
                return
            except Exception:
                continue
        raise TimeoutError("No known Upwork job tile selectors became available.")

    async def _query_first(self, scope, selectors):
        for selector in selectors:
            handle = await scope.query_selector(selector)
            if handle:
                return handle
        return None

    async def _enrich_job_details(self, context, job_url):
        details = {
            "tags": [],
            "client_history": "",
        }
        page = await context.new_page()
        page.set_default_timeout(20000)
        try:
            await page.goto(job_url)
            await self._random_delay(0.4, 1.0)
            await self._human_scroll(page, distance=600)

            tag_nodes = await page.query_selector_all(
                '[data-test="TokenClamp JobAttrs"] span, [data-test="TokenClamp"] span, .air3-token span'
            )
            tags = []
            for node in tag_nodes[:8]:
                text = (await node.inner_text()).strip()
                if text:
                    tags.append(text)

            client_history_node = await self._query_first(page, [
                '[data-test="client-spendings"]',
                '[data-test="client-job-posting-stats"]',
                '[data-test="AboutClient"]',
            ])
            client_history = await client_history_node.inner_text() if client_history_node else ""
            details["tags"] = tags
            details["client_history"] = client_history.strip()
        except Exception as exc:
            print(f"⚠️ Deep search failed for {job_url}: {exc}")
        finally:
            await page.close()
        return details

    async def _human_scroll(self, page, distance=1200):
        await page.mouse.wheel(0, random.randint(250, 450))
        await self._random_delay(0.2, 0.7)
        await page.mouse.wheel(0, random.randint(350, distance))
        await self._random_delay(0.3, 0.8)

    async def _random_delay(self, minimum=0.3, maximum=1.2):
        await asyncio.sleep(random.uniform(minimum, maximum))

    def _sync_new_leads_to_notion(self, db, created_leads):
        for lead in created_leads:
            try:
                result = self.notion_service.add_lead(
                    title=lead.title,
                    platform=lead.platform,
                    budget=lead.budget,
                    link=lead.url,
                    status="Scraped",
                    match_score=(lead.raw_data or {}).get("opportunity_score"),
                )
                if result.get("ok") and result.get("page_id"):
                    lead.raw_data = dict(lead.raw_data or {})
                    lead.raw_data["notion_page_id"] = result["page_id"]
            except Exception as exc:
                print(f"⚠️ Notion sync failed for lead '{lead.title}': {exc}")

        if created_leads:
            db.commit()

if __name__ == "__main__":
    scout = UpworkScoutPlaywright()
    asyncio.run(scout.hunt())

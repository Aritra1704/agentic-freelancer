import asyncio
import json
import os
from playwright.async_api import async_playwright

class UpworkScoutPlaywright:
    def __init__(self, user_data_dir="./browser-use-user-data-dir-local"):
        self.user_data_dir = user_data_dir
        self.output_path = "leads/active_leads.json"

    async def hunt(self, keywords=["Python AI Agent", "LLM Integration", "RAG"]):
        print(f"--- Upwork Playwright Scout is starting a hunt ---")
        
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
            
            # Go to Upwork search
            query = " ".join(keywords)
            search_url = f"https://www.upwork.com/nx/search/jobs/?q={query}&sort=recency"
            
            print(f"🌐 Navigating to: {search_url}")
            await page.goto(search_url)
            
            # Wait for job listings to load
            try:
                await page.wait_for_selector('article.job-tile', timeout=15000)
            except Exception as e:
                print(f"⚠️ Warning: Job tiles not found or timed out. Checking if logged in...")
                if "login" in page.url:
                    print("❌ Error: Not logged in. Please run login_to_upwork.py first.")
                    await context.close()
                    return []
                
            # Extract jobs
            jobs = []
            job_tiles = await page.query_selector_all('article.job-tile')
            
            for tile in job_tiles[:5]:
                try:
                    title_elem = await tile.query_selector('h2.job-tile-title a')
                    title = await title_elem.inner_text() if title_elem else "N/A"
                    url = await title_elem.get_attribute('href') if title_elem else ""
                    if url and not url.startswith('http'):
                        url = "https://www.upwork.com" + url
                        
                    description_elem = await tile.query_selector('.job-tile-description')
                    description = await description_elem.inner_text() if description_elem else "N/A"
                    
                    budget_elem = await tile.query_selector('.job-tile-info-list')
                    budget = await budget_elem.inner_text() if budget_elem else "N/A"
                    
                    jobs.append({
                        "title": title.strip(),
                        "url": url,
                        "description": description.strip(),
                        "budget": budget.strip()
                    })
                except Exception as e:
                    print(f"⚠️ Error parsing a job tile: {e}")
            
            print(f"✅ Found {len(jobs)} jobs.")
            
            # Save leads
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, "w") as f:
                json.dump(jobs, f, indent=2)
                
            await context.close()
            return jobs

if __name__ == "__main__":
    scout = UpworkScoutPlaywright()
    asyncio.run(scout.hunt())

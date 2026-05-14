import asyncio
from playwright.async_api import async_playwright

async def login():
    print("🌍 Opening Upwork for manual login...")
    print("👉 Please log in with your Google Account or Credentials.")
    print("⏳ The session will be saved into the './browser_data' directory for the Scout Agent.")
    print("❌ Just close the browser window when you are done logging in.")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./browser_data",
            headless=False,
            no_viewport=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await browser.new_page()
        await page.goto("https://www.upwork.com/ab/account-security/login")
        
        try:
            # Wait for the browser to be closed by the user
            await page.wait_for_event("close", timeout=0)
        except Exception as e:
            # Handle potential timeout or early exit gracefully
            pass
            
    print("\n✅ Session successfully saved! You can now run ./START_HERE.sh")

if __name__ == "__main__":
    asyncio.run(login())

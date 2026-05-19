import asyncio
from playwright.async_api import async_playwright


async def login():
    print("🌍 Opening Contra for manual login...")
    print("👉 Please log in with your credentials.")
    print("⏳ The session will be saved into the './browser-use-user-data-dir-local' directory.")

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir="./browser-use-user-data-dir-local",
            headless=False,
            channel="chrome",
        )
        page = await browser.new_page()
        await page.goto("https://contra.com/login")
        await page.wait_for_event("close", timeout=0)
    print("\n✅ Session successfully saved!")


if __name__ == "__main__":
    asyncio.run(login())

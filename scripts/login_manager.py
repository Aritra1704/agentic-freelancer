# freelance-os/scripts/login_manager.py
import asyncio
import os
import sys
from browser_use import Agent, Browser
from browser_use.browser.profile import BrowserProfile

# Ensure the core/LLM factory can be found if run directly
sys.path.append(os.getcwd())
from core.llm_factory import LLMFactory

async def login_to_platform(platform_url, platform_name):
    print(f"\n--- 🔐 Login Mode: {platform_name} ---")
    print(f"Please log in to {platform_name} in the browser window.")
    
    # Persistent profile for cookies
    profile = BrowserProfile(
        user_data_dir="./browser_data" 
    )
    
    # Headed mode for login
    browser = Browser(
        headless=False,
        profile=profile
    )
    
    llm = LLMFactory.get_model_instance("flash")
    
    agent = Agent(
        task=f"Go to {platform_url}. I will perform the login manually. Wait until I have successfully logged in and the dashboard is visible. Once I am in, tell me 'LOGIN_SUCCESS' and stop.",
        llm=llm,
        browser=browser,
        # Pass context config through the browser session if needed, 
        # but browser-use handles it via the browser instance usually.
    )

    await agent.run()
    await browser.close()
    print(f"✅ Session for {platform_name} saved.")

async def main():
    platforms = [
        ("https://www.upwork.com", "Upwork"),
        ("https://www.linkedin.com", "LinkedIn"),
        ("https://github.com/login", "GitHub")
    ]
    
    for url, name in platforms:
        await login_to_platform(url, name)
        input(f"Press Enter to proceed to the next platform ({name} done)...")

if __name__ == "__main__":
    asyncio.run(main())

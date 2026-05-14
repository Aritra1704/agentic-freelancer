# freelance-os/agents/profile_scout.py
import asyncio
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from core.llm_factory import LLMFactory

async def main():
    # Use Flash for cost-effective research
    llm = ChatGoogleGenerativeAI(model=LLMFactory.get_model("flash"))
    
    task = (
        "Search for 'aritrarpal GitHub' and 'aritrarpal LinkedIn'. "
        "Summarize the key technologies, top repositories, and professional experience. "
        "Extract specific Java, Python, and JavaScript project details. "
        "Save the summary to freelance-os/context/scraped_profile.txt"
    )
    
    agent = Agent(
        task=task,
        llm=llm
    )
    
    print("--- Profile Scout is researching your online presence ---")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())

# Freelance-OS: AI-Native Execution Plan

This document outlines the end-to-end system for finding, winning, and executing software freelancing jobs using an AI-augmented workflow.

## 1. Project Architecture
The system follows a **Scout -> Strategist -> Builder** lifecycle.

- **Scout:** Uses `browser-use` (Playwright) + Gemini 1.5 Flash to find leads.
- **Strategist:** Uses Gemini 1.5 Pro to analyze leads against local portfolio context.
- **Builder:** Uses Gemini CLI + Local Ollama to generate code, tests, and docs.

---

## 2. Infrastructure Setup

### Directory Structure
```text
freelance-os/
├── context/
│   ├── portfolio.md       # Your skills, projects, and bio
│   └── resume.md          # Technical experience
├── leads/
│   └── active_leads.json  # Scraped jobs from platforms
├── scripts/
│   ├── hunt_leads.py      # Browser-use script (Playwright)
│   └── filter_leads.py    # Logic to rank jobs
└── workspace/             # Working directory for client projects
```

### Required Tools
1. **Gemini 1.5 Pro/Flash:** (Paid API) for high-level reasoning.
2. **Ollama:** (Local) for cost-effective boilerplate and unit testing.
3. **MCP Servers:**
   - `browser-use`: For web interaction.
   - `filesystem`: For reading/writing project files.

---

## 3. The "Scout" Script (Lead Hunting)
This script uses the `browser-use` library to automate job searching on platforms like Upwork or Contra.

```python
# scripts/hunt_leads.py
import asyncio
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI

async def main():
    # Use Flash for cost-effective web navigation
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    
    agent = Agent(
        task="""
        1. Go to Upwork.com (or Contra.com).
        2. Search for 'Python AI Agent' or 'LLM Integration' jobs.
        3. Extract the last 10 jobs: Title, Budget, Description, and Client Rating.
        4. Save the output to leads/active_leads.json.
        """,
        llm=llm
    )
    
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. The "Strategist" Logic (Proposal Generation)
Use Gemini 1.5 Pro via CLI to analyze the leads and write a "winning" pitch.

**Prompt for Gemini CLI:**
```text
"Read ./leads/active_leads.json and ./context/portfolio.md.
Identify the top 2 jobs where my portfolio provides the strongest 'Speed & Value' advantage.
For each:
1. Create a 3-step technical execution plan.
2. Write a proposal that says: 'I use an AI-Native workflow (MCP/Gemini) to deliver 2x faster with 100% test coverage.'
3. Save the proposal to ./leads/proposal_drafts.md."
```

---

## 5. Cost Optimization Strategy (Hybrid Mode)

| Task | Model | Reason |
| :--- | :--- | :--- |
| **Scraping/Browsing** | Gemini 1.5 Flash | Fast and significantly cheaper for token-heavy web pages. |
| **Strategy/Architecture** | Gemini 1.5 Pro | Highest reasoning for winning contracts. |
| **Boilerplate/Unit Tests** | Ollama (Llama 3) | Zero cost for high-volume, low-complexity code generation. |
| **Documentation** | Ollama (Mistral) | Local models excel at summarizing and formatting text. |

---

## 6. Full-Proof Execution (The "Builder" Phase)

Once you win a job:
1. **Scaffold:** Use Gemini CLI to create the project structure.
2. **Surgical Coding:** Use `replace` to implement core logic.
3. **Local Testing:**
   ```bash
   # Use Ollama to generate tests locally
   ollama run llama3 "Write 5 pytest cases for this function: $(cat src/logic.py)" > tests/test_logic.py
   ```
4. **Validation:** Run tests and use Gemini to fix any failures.

---

## 7. Immediate Next Steps
1. **Populate `./context/portfolio.md`:** List your specific tech stack and past results.
2. **Install Playwright:** Run `playwright install` to enable `browser-use`.
3. **Configure API Keys:** Set `GOOGLE_API_KEY` and ensure Ollama is running on port 11434.

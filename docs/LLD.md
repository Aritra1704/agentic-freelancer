# Low-Level Design (LLD): Freelance-OS

## 1. Directory Structure
```text
freelance-os/
├── agents/            # Core Agent implementations
├── core/              # Shared logic (LLM, DB, NotionService)
├── leads/             # Scraped/Raw job data
├── skills/            # Playbooks (for Agents) and specialized skills
├── workspace/         # Client project scaffolding
└── docs/              # Retained documentation
```

## 2. Core Module Specifications

### A. The Scout (`agents/scout_agent.py`)
- **Library:** `browser-use` (Playwright).
- **Functionality:** Scrapes platforms, performs deep extraction (navigating to individual job URLs), and syncs leads to Notion via `NotionService`.

### B. The Strategist (`agents/strategist_agent.py`)
- **Functionality:** Implements the `grill-me` skill to identify risks and drafts technical pitches.
- **Skill Integration:** Loads Markdown playbooks (e.g., `marketing-psychology`, `market-sizing`) from `skills/playbooks/` to guide LLM reasoning.

### C. The Builder (`agents/builder_agent.py`)
- **Functionality:** Scaffolds TDD projects, performs architecture passes for entropy control, and wraps Gemini CLI.

### D. Notion Service (`core/notion_service.py`)
- **Purpose:** Centralized, resilient Notion API handler.
- **Features:**
    - Supports both Databases and Data Sources (SDK 3.1.0 compatibility).
    - `_safe_query`: Bypasses broken query endpoints using direct HTTP requests and Search API fallbacks.
    - `add_lead`, `add_strategy`, `update_lead_status`: Unified sync methods.

---

## 3. Skill & Playbook Integration
Playbooks are stored in `skills/playbooks/` and loaded dynamically into agent prompts.
- **`security-auditor`**: Used by Builder Agent for code security.
- **`market-sizing-analysis`**: Used by Scout for lead scoring.
- **`marketing-psychology`**: Used by Strategist for pitch conversion.

---

## 4. Operational & Execution Flow
1. **Bootstrap/Setup:** Configure `.env` with `NOTION_API_KEY` and verified IDs.
2. **Lead Discovery:** Execute `python main.py hunt`.
3. **Lead Refinement:** `LeadProcessor` runs, utilizing local Ollama, robust JSON extraction, and Notion sync.
4. **Strategy Formulation:** Execute `python main.py strategize`.
5. **Project Scaffolding:** Execute `python main.py build`.

---

## 5. Security & Error Handling
- **API Keys:** Kept in `.env` (not committed).
- **Robustness:** 
    - Exponential backoff for API calls.
    - JSON extraction regex for Ollama responses.
    - Fallback mechanisms in `NotionService` for API compatibility.
- **Local Processing:** Ollama is utilized to keep sensitive code analysis off the cloud.

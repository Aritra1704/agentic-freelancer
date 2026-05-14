# Low-Level Design (LLD): Freelance-OS

## 1. Directory Structure Details
```text
freelance-os/
├── agents/
│   ├── scout_agent.py      # Browser-use implementation
│   ├── strategist_agent.py  # Ranking & Proposal logic
│   └── builder_agent.py     # Code scaffolding & testing
├── core/
│   ├── llm_factory.py      # Configuration for Gemini & Ollama
│   └── mcp_client.py       # Shared MCP connection logic
├── leads/
│   ├── active_leads.json   # Raw data
│   └── ranked_leads.json   # Analyzed data
└── workspace/              # Dynamic client folders
```

## 2. Module Specifications

### A. Scout Agent (`agents/scout_agent.py`)
- **Library:** `browser-use`
- **Class:** `LeadScout`
- **Methods:**
    - `search_platforms(query: str)`: Navigates to Upwork/Contra.
    - `extract_job_data()`: Parses DOM for title, budget, description, and link.
    - `save_leads()`: Writes to `active_leads.json`.
- **Logic:** Uses a headless browser with user-agent rotation to avoid detection.

### B. Strategist Agent (`agents/strategist_agent.py`)
- **Class:** `ProposalStrategist`
- **Methods:**
    - `calculate_fit(job_desc, portfolio)`: Returns a score (0-100).
    - `internal_grill(job_desc)`: **Skill Hook: `grill-me`**. Generates 5 "Hard Questions" about the job to refine the pitch.
    - `generate_pitch(job_desc)`: Uses Gemini 1.5 Pro to draft a tailored technical solution.
- **Logic:** Implements a "Reasoning Loop" (Chain-of-Thought) and updates the project's `CONTEXT.md` (Skill: `ubiquitous-language`).

### C. Builder Agent (`agents/builder_agent.py`)
- **Class:** `ProjectBuilder`
- **Methods:**
    - `scaffold_with_tdd()`: **Skill Hook: `tdd`**. Writes tests before code.
    - `apply_architecture_pass()`: **Skill Hook: `improve-codebase-architecture`**. Refactors logic into deep modules.
    - `run_cli_command(command)`: Wrapper for `gemini` CLI tools.

### D. LLM Factory (`core/llm_factory.py`)
- **Purpose:** Centralize model switching based on task complexity.
```python
def get_llm(tier="pro"):
    if tier == "pro":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro")
    elif tier == "flash":
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    elif tier == "local":
        return Ollama(model="llama3")
```

## 3. Automation Scripts

### Execution Flow for Antigravity:
1. **Bootstrap:** Run `mkdir` for all folders in the structure.
2. **Context Setup:** Write a template `context/portfolio.md`.
3. **Lead Hunting:**
   - Execute `scout_agent.py`.
   - Output goes to `leads/active_leads.json`.
4. **Proposal Generation:**
   - Execute `strategist_agent.py`.
   - Reads `active_leads.json` and `portfolio.md`.
   - Output goes to `leads/ranked_leads.json`.

## 4. Error Handling
- **Browser Failures:** Retry logic (up to 3 times) for Playwright timeouts.
- **API Rate Limits:** Exponential backoff for Gemini API calls.
- **Ollama Availability:** Fallback to Gemini Flash if local Ollama is not running.

## 5. Integration with Gemini CLI
The `builder_agent.py` will primarily act as a wrapper for Gemini CLI commands:
- `gemini replace ...`
- `gemini write_file ...`
- `gemini run_shell_command ...`

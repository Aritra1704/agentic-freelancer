# High-Level Design (HLD): Freelance-OS

## 1. Executive Summary
Freelance-OS is an agentic system designed to automate the lead generation, proposal drafting, and project execution phases of software freelancing. It leverages a hybrid model of cloud-based LLMs (Gemini) and local models (Ollama).

## 2. System Architecture
The system is divided into three core autonomous layers:

### A. The Scout (Lead Discovery)
- **Role:** Monitor job boards for high-value opportunities.
- **Fundamental:** `ubiquitous-language`. Uses a pre-defined glossary to filter jobs.

### B. The Strategist (Proposal & Strategy)
- **Role:** Filter leads and generate custom technical pitches.
- **Fundamental:** `grill-me`. Performs an internal "Grill Session" to identify client risks and hidden requirements.

### C. The Builder (Project Execution)
- **Role:** Scaffold projects, write code, and generate tests.
- **Fundamental:** `tdd` & `improve-codebase-architecture`.

---

## 3. The "Control Tower" (Future Dashboard)
To transform from a CLI tool into a comprehensive Strategy Engine, we are planning a visual UI:
- **Backend:** FastAPI (Python) - Acts as a bridge between agents and the UI.
- **Frontend:** Next.js (React) + TailwindCSS + ShadcnUI.
- **Persistence:** Expanded PostgreSQL schema (`ProjectStrategy` table).
- **Core Features:** 
    - Inbox view, HLD/LLD visualizers (Mermaid), Pitch editor, and Economics/Quotation breakdown.

---

## 4. The Persistence & Memory Layer
- **PostgreSQL:** Centralized storage for leads, proposals, and project status.
- **MemPalace:** Implements **Verbatim Storage** and **Spatial Organization** to prevent duplicate job processing and enable historical analysis.
- **Notion Dashboard:** Automated sync for real-time project tracking and portfolio hosting.

---

## 5. Technology Stack
| Tier | Model | Purpose |
| :--- | :--- | :--- |
| **Primary (Paid)** | **Gemini 1.5 Pro** | Deep reasoning, proposal logic, and complex coding. |
| **Secondary (Paid)** | **Gemini 1.5 Flash** | Fast web scraping, lead summarization. |
| **Local (Free)** | **Ollama (Llama 3/Mistral)** | Unit tests, documentation, and sensitive code. |

---

## 6. Execution Roadmap & Status
### Status
- **Core Infrastructure:** Complete.
- **Scout Agent:** Complete (Upwork/Browser-use).
- **Strategist Agent:** Complete (Proposal/Internal Grill).
- **Builder Agent:** Complete (TDD/Ollama).
- **Notion Sync:** Complete.

### Pending Tasks
- [x] **Multi-Platform Support:** Fiverr/Contra/Freelancer paths are now supported through platform-aware scouting and login helpers.
- [x] **The Control Tower (Dashboard):** FastAPI backend and a minimal Next.js dashboard scaffold have been added.
- [x] **Docker Skill:** `skills/docker_skill.py` now generates deployment assets and performs real build verification when Docker is present.
- [x] **Refactor Leads:** `Lead` now stores structured strategy fields (HLD/LLD/quotation/milestones/feedback).
- [x] **Stitch Orchestration Engine:** State machine and `run-orchestrator` CLI flow implemented (`docs/STITCH_ORCHESTRATOR_PLAN.md`).
- [x] **Refinement Guardrails:** The refinement stage now enforces `technical_doubts` as a required output and routes invalid payloads into `refinement_failed` for recovery.
- [x] **Dashboard Completion:** The UI now renders `technical_doubts` plus the broader structured strategy payload exposed by the API.
- [ ] **Canva Integration:** Code path is implemented and now validates placeholder config more explicitly, but live Canva verification is still blocked by an invalid configured access token and missing real template IDs.
- [x] **Proposal Identity Source of Truth:** The strategist now reads both `context/portfolio.md` and `context/resume.md`, and the resume content has been personalized.

### Backlog
For detailed system gaps and future tasks, see [BACKLOG.md](./BACKLOG.md).

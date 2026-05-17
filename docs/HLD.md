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
- [ ] **Multi-Platform Support:** Fiverr/Contra integration.
- [ ] **The Control Tower (Dashboard):** Build the Next.js/FastAPI UI.
- [ ] **Docker Skill:** Mature the skeletal implementation in `skills/docker_skill.py`.
- [ ] **Refactor Leads:** Refactor `Leads` table to include structured strategy fields (HLD/LLD/Cost).

# High-Level Design (HLD): Freelance-OS

## 1. Executive Summary
Freelance-OS is an agentic system designed to automate the lead generation, proposal drafting, and project execution phases of software freelancing. It leverages a hybrid model of cloud-based LLMs (Gemini) and local models (Ollama).

## 2. System Architecture & Operational Philosophy
The system is divided into three core autonomous layers, underpinned by Matt Pocock's **Software Fundamentals**:

### A. The Scout (Lead Discovery)
- **Role:** Monitor job boards for high-value opportunities.
- **Fundamental:** `ubiquitous-language`. Uses a pre-defined glossary to filter jobs that match the user's specific "Expertise Nouns."

### B. The Strategist (Proposal & Strategy)
- **Role:** Filter leads and generate custom technical pitches.
- **Fundamental:** `grill-me`. Before drafting, the agent performs an internal "Grill Session" to identify client risks and hidden requirements.

### C. The Builder (Project Execution)
- **Role:** Scaffold projects, write code, and generate tests.
- **Fundamental:** `tdd` & `improve-codebase-architecture`. Code is delivered in small, testable increments.

### D. The Memory Layer (Cross-Project Intelligence)
- **Role:** Capture learnings and update the `UKB.md`.

### E. The Client Trust Layer (Transparency & Delivery)
- **Notion:** Automated "Client Portal" for real-time project tracking and portfolio hosting.
- **Canva:** Generation of visual wireflows and professional contract documents.
- **Docker:** Standardized delivery format ensuring "It works on their machine" from Day 1.

## 3. Technology Stack & Model Selection
| Tier | Model | Purpose |
| :--- | :--- | :--- |
| **Primary (Paid)** | **Gemini 1.5 Pro** | Deep reasoning, proposal logic, and complex coding. |
| **Secondary (Paid)** | **Gemini 1.5 Flash** | Fast web scraping, lead summarization, and initial filtering. |
| **Local (Free)** | **Ollama (Llama 3/Mistral)** | Unit tests, documentation, and sensitive data processing. |

**Paid Version Recommendation:** Use **Google AI Studio (Pay-as-you-go)**. It provides API keys for both Pro and Flash with high rate limits suitable for agentic workflows.

## 4. Data Flow
1. **Scout** scrapes job platforms -> Stores in `leads/`.
2. **Strategist** reads `leads/` + `context/portfolio.md` -> Drafts in `proposals/`.
3. **User** reviews and approves -> Submits via Browser.
4. **Builder** receives contract details -> Scaffolds in `workspace/`.

## 5. Security & Privacy
- **Client Data:** Stored locally in `workspace/`.
- **API Keys:** Managed via `.env` files; never committed.
- **Local Processing:** Ollama is used for sensitive logic to avoid sending proprietary client code to the cloud.

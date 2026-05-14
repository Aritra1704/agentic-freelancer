# Context: Freelance-OS

## Ubiquitous Language (Terminology)
- **The Scout:** Autonomous agent responsible for navigating job boards and extracting raw lead data using `browser-use`.
- **The Strategist:** Logic layer that performs "Internal Grilling" and drafts personalized technical proposals.
- **The Builder:** TDD-driven execution layer that implements client projects in the `workspace/`.
- **The Bridge:** The communication layer that delegates "Low-Logic" coding tasks to local **Ollama** models via CLI.
- **Lead:** A structured JSON object containing job details (title, budget, link).
- **Architecture Pass:** A periodic refactoring step aimed at reducing code entropy.

## Technical Constants
- **Primary LLM:** Gemini 1.5 Pro (via Google AI Studio).
- **Secondary LLM:** Gemini 1.5 Flash (Scraping).
- **Local LLM:** Ollama (Llama3/Deepseek-coder).
- **Workspace:** `/freelance-os/workspace/`.

## Operational Rules
1. **TDD First:** No implementation code is written before a failing test exists.
2. **Alignment First:** Use `grill-me` logic for every new major requirement.
3. **Deep Modules:** Prefer simple interfaces that hide complex AI-generated logic.

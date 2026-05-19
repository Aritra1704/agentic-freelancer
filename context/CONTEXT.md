# Context: Freelance-OS

## Core Engineering Principles (Software Fundamentals)
Freelance-OS is built on the following principles, inspired by Matt Pocock:

### 1. `grill-me` (Alignment)
The agent must interrogate the user/client *before* writing code to pin down the design space and uncover hidden assumptions. The **Strategist Agent** uses the `technical_doubts` field (captured as a requirement during the refinement stage) to generate these high-signal alignment questions.

### 2. `ubiquitous-language` (Terminology)
A shared glossary ensures consistency. (See "Vocabulary" below). Every client project in `workspace/` MUST start with a `CONTEXT.md`.

### 3. `tdd` (Feedback Loops)
Red-Green-Refactor in tiny vertical slices to prevent massive, unverified code dumps. The **Builder Agent** writes tests *before* features.

### 4. `improve-codebase-architecture` (Entropy Control)
Periodic "Architecture Passes" to clean up technical debt generated during rapid AI coding sessions, maintaining deep modules and simple interfaces.

---

## Ubiquitous Language (Vocabulary)
- **The Scout:** Autonomous agent responsible for navigating job boards and extracting raw lead data using `browser-use`.
- **The Strategist:** Logic layer that performs "Internal Grilling" and drafts personalized technical proposals.
- **The Builder:** TDD-driven execution layer that implements client projects in the `workspace/`.
- **The Bridge:** The communication layer that delegates "Low-Logic" coding tasks to local **Ollama** models via CLI.
- **Lead:** A structured JSON object containing job details (title, budget, link).
- **Architecture Pass:** A periodic refactoring step aimed at reducing code entropy.
- **Project:** A defined piece of work undertaken for a Client.
- **Contract:** A legally binding agreement outlining terms between Freelance-OS and a Client.

---

## Technical Constants
- **Primary LLM:** Gemini 1.5 Pro (via Google AI Studio).
- **Secondary LLM:** Gemini 1.5 Flash (Scraping).
- **Local LLM:** Ollama (Llama3/Deepseek-coder).
- **Workspace:** `freelance-os/workspace/`.

---

## Operational Rules
1. **TDD First:** No implementation code is written before a failing test exists.
2. **Alignment First:** Use `grill-me` logic for every new major requirement.
3. **Deep Modules:** Prefer simple interfaces that hide complex AI-generated logic.

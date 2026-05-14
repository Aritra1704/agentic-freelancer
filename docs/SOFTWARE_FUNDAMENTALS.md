# Software Fundamentals & AI Skills (Matt Pocock Philosophy)

This document outlines the core engineering principles integrated into the Freelance-OS project, inspired by Matt Pocock's "Software Fundamentals Matter More Than Ever."

## Core Skills

### 1. `grill-me` (Alignment)
- **Concept:** The agent must interrogate the user/client before writing code.
- **Goal:** Pin down the design space and uncover hidden assumptions.
- **Freelance-OS Use:** The **Strategist Agent** will "grill" the user or analyze the job description to ensure the technical architecture is perfectly aligned with client needs.

### 2. `ubiquitous-language` (Terminology)
- **Concept:** A shared glossary (captured in `CONTEXT.md`) between the human and the agent.
- **Goal:** Reduce reasoning tokens and naming inconsistencies.
- **Freelance-OS Use:** Every client project in the `workspace/` folder MUST start with a `CONTEXT.md`.

### 3. `tdd` (Feedback Loops)
- **Concept:** Red-Green-Refactor in tiny vertical slices.
- **Goal:** Prevent massive, unverified code dumps.
- **Freelance-OS Use:** The **Builder Agent** will prioritize writing a failing test before implementing features.

### 4. `improve-codebase-architecture` (Entropy Control)
- **Concept:** Continuous refactoring toward "deep modules" and simple interfaces.
- **Goal:** Keep the codebase manageable as it grows.
- **Freelance-OS Use:** Periodic "Architecture Passes" to clean up technical debt generated during rapid AI coding sessions.

## Workflow Integration
1. **Align** before coding (`grill-me`).
2. **Define** shared language (`CONTEXT.md`).
3. **Execute** in tiny steps (`tdd`).
4. **Refactor** for simplicity (`improve-codebase-architecture`).

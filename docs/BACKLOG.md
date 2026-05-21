# Backlog: Freelance-OS

This document tracks the remaining implementation work after a repo audit on May 19, 2026.
It is intended to reflect actual code state, not earlier planning assumptions.

## Current Summary
- `technical_doubts` and `suggested_stack` are already stored in the database and exposed by the FastAPI layer.
- Refinement now enforces `technical_doubts`, and invalid payloads are routed into `refinement_failed` for recovery.
- The dashboard now exposes the structured strategy fields already returned by the API, including `technical_doubts`, milestones, quotation, and HLD/LLD content.
- `context/resume.md` has been personalized, and the strategist now reads both resume and portfolio context.
- Canva integration code exists and is wired into the strategist flow, but live template/app configuration is still incomplete because the current token is invalid and no real template IDs are configured.

## Priority 1: Skill Integration (Autonomous Brain)
- [ ] **Plug-in `grill-me`:** Update `StrategistAgent.py` to instantiate `GrillWithDocsSkill` and perform a mandatory alignment check against `docs/*.md` before drafting any proposal.
- [ ] **Plug-in `ubiquitous-language`:** Update `LeadProcessor.py` to use `UbiquitousLanguageSkill` to validate that lead `tags` match the terms defined in `VOCABULARY.md`.
- [ ] **Plug-in `adr-manager`:** Update `BuilderAgent.py` to use `ADRSkill` to automatically document architectural changes during the 'Architecture Pass' phase.

## Priority 2: System Integrity & Fundamentals
- [x] **Enforce `grill-me` during refinement:** `agents/lead_processor.py` now requires `technical_doubts`, validates at least 3 distinct questions, and refuses to mark a lead as `refined` when that condition fails.
- [x] **Resolve legacy refinement failure state:** `PipelineStatus` now includes `REFINEMENT_FAILED`, and the orchestrator can re-claim those leads for another refinement pass.
- [x] **Remove the strategist fallback that hides missing refinement output:** `StrategistAgent` no longer fabricates default questions. Leads missing refinement-grade `technical_doubts` are pushed back into `refinement_failed`.

## Priority 2: Identity & Proposal Quality
- [x] **Personalize `context/resume.md`:** The resume now contains real positioning, experience, and project context derived from the existing portfolio and system context.
- [x] **Decide strategist source of truth for personal context:** `StrategistAgent` now loads both `context/portfolio.md` and `context/resume.md` so proposal generation uses a fuller identity context instead of an unresolved either/or.
- [ ] **Complete live Canva configuration:** The code now detects placeholder configuration more accurately, but live verification is still blocked because the currently configured Canva access token returns `invalid_access_token` and no real template IDs are present.

## Priority 3: Dashboard & UX
- [x] **Finish dashboard support for strategy fields:** `dashboard/app/page.tsx` now renders `technical_doubts` alongside `suggested_stack`.
- [x] **Improve lead detail visibility in the dashboard:** The dashboard now surfaces milestones, quotation, HLD/LLD, and pitch content through a dedicated lead-detail panel.

## Notes
- The `.env.example` file already includes the required Canva variables. The remaining work is real configuration and validation, not variable naming or template scaffolding.
- `docs/HLD.md` and `docs/CANVA_INTEGRATION_PLAN.md` should be kept aligned with this backlog as implementation proceeds.

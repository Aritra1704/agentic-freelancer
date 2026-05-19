# Backlog: Freelance-OS

This document tracks identified gaps and required improvements found during the system verification on May 18, 2026.

## Priority 1: System Integrity & Fundamentals
- [ ] **Enforce `grill-me` (Alignment):** Update `agents/lead_processor.py` to move `technical_doubts` from an optional field to a **required** field in the LLM prompt. Ensure the system refuses to refine a lead without at least 3 high-signal technical questions.
- [ ] **Sync Pipeline Status:** Add `REFINEMENT_FAILED = "refinement_failed"` to the `PipelineStatus` Enum in `core/database.py` to reconcile existing database records with the source code.

## Priority 2: Identity & Branding
- [ ] **Resume Personalization:** Populate `context/resume.md` with actual professional experience. This is critical for the Strategist Agent to generate accurate and high-conversion proposals.
- [ ] **Canva Integration:** Add `CANVA_API_KEY` and relevant `TEMPLATE_ID`s to the `.env` file to enable the automated generation of branded PDF proposals and contracts.

## Priority 3: Dashboard & UX
- [ ] **Frontend Completion:** Finalize the Next.js dashboard components in `dashboard/app/page.tsx` to visualize the `technical_doubts` and `suggested_stack` for each lead.

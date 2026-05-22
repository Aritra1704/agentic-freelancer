# Freelance OS: Architectural Blueprint (Full Lifecycle)

## The Team
1. **Sales Lead (`freelance-os`):** Owns the **Sales Pipeline**. Finds jobs, performs strategy, crafts pitches, manages client communication, closes deals.
2. **Legal/Compliance Agent:** Owns the **Compliance Gates**. Reviews agreements (Pre-Won) and audits deliverables (Post-Dev).
3. **Developer (`localclaw`):** Owns the **Development Pipeline**. Executes technical tasks ONLY after a project is `WON`.

## Lifecycle Flow
1. **Sales Pipeline (freelance-os):** Vetted Lead -> STRATEGIZING (Strategy/Pitch) -> PITCHING -> NEGOTIATING -> **WON**.
2. **Development Pipeline (localclaw):** WON -> IN_DEVELOPMENT -> COMPLIANCE_CHECK -> READY_FOR_DELIVERY -> COMPLETED.

## Task Board Schema
- **Sales Pipeline:** Managed in `leads` table.
- **Development Pipeline:** Managed in `task_board` table.
- **The Bridge:** Status `WON` triggers `LeadService.promote_to_dev_board()`.

## Capability Assessment
- **`freelance-os`:** Business strategy, communication, and commercial negotiation.
- **`localclaw`:** Technical execution, testing, and system-level verification.

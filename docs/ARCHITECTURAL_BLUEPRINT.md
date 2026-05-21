# Freelance OS: Architectural Blueprint (Full Lifecycle)

## The Team
1. **Sales Lead (`freelance-os`):** External-facing. Searches for jobs, handles client comms, writes proposals, handles billing/invoicing.
2. **Legal/Compliance Agent (NEW):** Internal-facing. Reviews contracts, ensures SOW compliance, validates final deliverables for security/privacy before client delivery.
3. **Developer (`localclaw`):** Internal-facing (Agentic Kernel). Autonomous developer with file system and CLI access. Runs in a Plan-Act-Verify loop.

## Lifecycle & Interaction Flow
1. **Sales Lead:** Finds job -> Negotiates -> Agrees on Price/Scope.
2. **Legal Agent:** Receives agreement -> Reviews Contract -> Validates Compliance -> **Approves for Dev**.
3. **Developer (`localclaw`):** Picks up task from queue -> Develops -> Tests -> Validates -> Marks **Ready for Delivery**.
4. **Legal Agent:** Performs final check (e.g., secrets scanning, PII check) -> **Approves for Sales**.
5. **Sales Lead:** Receives approval -> Sends final delivery -> Requests payment.

## Interaction Model
- **Persistence:** All work is defined in a shared PostgreSQL `task_board` table (Agile/Jira-style).
- **Communication:** Agents read/write tasks and update status based on their role.
- **Independence:** All three are separate processes on the Mac.

## Task Board Schema (Agile Structure)
| Field | Purpose |
| :--- | :--- |
| `task_id` | Unique ID |
| `ticket_name` | Short summary |
| `description` | Requirements & Specs |
| `priority` | 1 (High) to 5 (Low) |
| `status` | BACKLOG, LEGAL_REVIEW, PENDING, IN_PROGRESS, COMPLIANCE_CHECK, READY_FOR_DELIVERY, COMPLETED |
| `assignee` | "freelance-os" \| "legal_agent" \| "localclaw" |
| `notes` | Log of blockers or progress |

## Capability Assessment
- **`freelance-os`:** Event-driven sales orchestrator.
- **`Legal Agent`:** Validation and compliance gatekeeper.
- **`localclaw`:** Persistent autonomous development kernel.

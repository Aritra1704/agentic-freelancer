# Implementation Plan: Human-in-the-Loop Lead Inbox

## Overview
Create a "Lead Inbox" UI to allow manual vetting of leads scraped by the Scout agent. Only leads approved by the user will be converted into Tasks and promoted to the main `task_board`.

## Functional Requirements
1. **Lead Inbox View:**
   - A dedicated UI table/board to display raw `leads` from the PostgreSQL `leads` table.
   - Fields: Title, Budget, Description, Platform.
2. **Approval/Rejection Actions:**
   - **Approve:** Move lead to `task_board` (Table -> Task Board).
   - **Reject:** Delete lead or mark as `ARCHIVED` in the database.
3. **Task Promotion:**
   - Create a `LeadService` in `core/` to handle the conversion from `Lead` object to `Task` object.

## Implementation Steps for Codex
1. **API:** Implement `dashboard/app/api/leads/route.ts` (GET) to fetch raw leads.
2. **API:** Implement `dashboard/app/api/leads/[id]/route.ts` (POST - "approve", DELETE - "reject").
3. **Frontend:** Create `dashboard/app/components/LeadInbox.tsx` or update `dashboard/app/page.tsx` to include an "Inbox" tab.
4. **Backend:** Implement the promotion logic in `core/lead_service.py` to map lead fields (title, desc) to task fields and insert into `task_board`.

## Task Board Integration
The main Kanban board remains the view for "Active" work. The Lead Inbox is a pre-stage entry gate.

---
**Storage Location:** `/Users/aritrarpal/Documents/workspace_biz/freelance-os/docs/IMPLEMENTATION_PLAN_LEAD_INBOX.md`

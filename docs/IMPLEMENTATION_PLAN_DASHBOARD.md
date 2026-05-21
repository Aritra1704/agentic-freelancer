# Implementation Plan: Dashboard & Agent Trigger UI

## Overview
This plan outlines the implementation of the UI control panel and trigger system within the existing Next.js `dashboard/` project. The goal is to allow manual triggering of the Sales and Legal agents and provide a visual status of the shared PostgreSQL Task Board.

## Component 1: Trigger API Routes (Backend)
These Next.js API routes will act as the bridge between the UI and the Python agent scripts.

*   **Task:** Create `dashboard/app/api/trigger/sales/route.ts`
    *   **Logic:** Execute `python3 scripts/run_sales.py` using Node.js `child_process.exec`.
*   **Task:** Create `dashboard/app/api/trigger/legal/route.ts`
    *   **Logic:** Execute `python3 scripts/run_legal.py` using Node.js `child_process.exec`.

## Component 2: Task Board Visualization (Frontend)
A simple dashboard to view the state of the shared PostgreSQL table.

*   **Task:** Create `dashboard/app/api/tasks/route.ts`
    *   **Logic:** Query the `task_board` table and return JSON data.
*   **Task:** Update `dashboard/app/page.tsx`
    *   **UI:** Use `fetch` to get task data.
    *   **Layout:** Build a Kanban board using Tailwind CSS, grouping tasks by `status` (BACKLOG, PENDING, etc.).

## Component 3: Integration (UI Triggers)
*   **Task:** Update `dashboard/app/page.tsx`
    *   **Buttons:** Add "Run Sales Scan" and "Perform Legal Review" buttons.
    *   **Interaction:** Clicking a button triggers a `fetch('POST', '/api/trigger/[agent]')` and refreshes the Kanban view.

## Execution Steps for Codex
1.  **Environment:** Ensure `dashboard/` has necessary dependencies (e.g., `pg` client for Postgres access).
2.  **API:** Implement trigger routes using `child_process`.
3.  **Frontend:** Create a Kanban component that maps over the tasks fetched from the API.
4.  **Verification:** Trigger an agent from the UI, observe the Task Board status change in the UI, and verify the Python log output.

---
**Storage Location:** `/Users/aritrarpal/Documents/workspace_biz/freelance-os/docs/IMPLEMENTATION_PLAN_DASHBOARD.md`

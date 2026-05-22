# Lead Vetting Enhancements: Requirements

This document outlines requested UI and metadata enhancements for the lead vetting process to improve traceability and decision-making during human review.

## 1. UI Display Enhancements
*   **Job ID:** Display a concise, platform-prefixed identifier for each lead (e.g., `UPWRK-0001`, `FIVRR-0002`) for easy reference.
*   **Job Classification:** Tag leads by engagement type:
    *   Contractual
    *   Fixed-Price Project
    *   Hourly
*   **Project Valuation:** Automatically or manually label clients based on potential value:
    *   High-Value / Big Client
    *   Low-Value / Budget Client
*   **Job Priority:** User-definable priority level to influence the `localclaw` execution sequence.

## 2. Technical Requirements
*   **Database:** Update `Lead` model to include `job_id`, `engagement_type`, `valuation_label`, and `priority`.
*   **Frontend:** Update `LeadInbox` view to render these new metadata fields as badges or labels.
*   **Pipeline:** Ensure the promotion logic (Lead -> Task) carries these metadata fields into the `Task` object.

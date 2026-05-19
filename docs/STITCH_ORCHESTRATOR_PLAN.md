# Plan: Stitch Orchestration Engine

## 1. Goal
Implement a robust state machine to manage lead processing, ensuring atomic transitions and resumable workflows.

## 2. Implementation Phases

### Phase 1: State Formalization
- Define `LeadStatus` enum in `core/database.py` (New: `SCAPED`, `REFINING`, `REFINED`, `STRATEGIZING`, `STRATEGIZED`).
- Add a `last_updated_at` field to the `Lead` model to detect stale leads.

### Phase 2: The Stitcher Engine (`core/orchestrator.py`)
- Create `Stitcher` class with `transition(lead_id, new_status)` and `get_pending_tasks()`.
- Logic for error handling: If a transition fails, set status to `ERROR` and log to `MemPalace`.

### Phase 3: Agent Migration
- Update `ScoutAgent` to transition to `SCAPED`.
- Update `LeadProcessor` to pull `SCAPED` leads, transition to `REFINING`, then `REFINED`.
- Update `StrategistAgent` to pull `REFINED` leads, transition to `STRATEGIZING`, then `STRATEGIZED`.

### Phase 4: CLI Integration
- Update `main.py` to support `python main.py run-orchestrator` which runs the entire pipeline based on current DB states.

## 3. Backlog & Priority
- [x] Implement `PipelineStatus` Enum.
- [x] Build `Stitcher` core engine.
- [x] Refactor Agent DB interactions.
- [x] Finalize `run-orchestrator` CLI command.

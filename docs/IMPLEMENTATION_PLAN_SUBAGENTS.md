# Implementation Plan: Sub-Agent Architecture (`ProposalEngine` & `PricingPredictor`)

## 1. Interaction Contract (The "Handshake")

`freelance-os` will interact with sub-agents using a standardized `AgentInterface`.

```json
// Example: Request from Orchestrator
{
  "task": "generate_proposal",
  "input": {
    "job_description": "...",
    "freelancer_context": "..."
  }
}

// Example: Response from Sub-Agent
{
  "status": "success",
  "artifact": {
    "type": "text",
    "content": "..."
  }
}
```

## 2. Implementation Roadmap

### Phase 1: Base Architecture (freelance-os)
*   [x] Define `BaseAgent` class in `core/agent_manager.py` to enforce input/output contracts.
*   [x] Implement the `AgentRegistry` for sub-agent lookup in `core/agent_manager.py`.

### Phase 2: `ProposalEngine` Implementation
*   [x] Create `agents/proposal_engine.py` (stubbed).
*   [x] Implement logic to process `job_description` and portfolio/resume context.
*   [x] Add unit tests (`tests/test_proposal_engine.py`).

### Phase 3: `PricingPredictor` Implementation
*   [x] Create `agents/pricing_predictor.py` (stubbed).
*   [x] Implement logic for complexity-based pricing estimation.
*   [x] Add unit tests (`tests/test_pricing_predictor.py`).

### Phase 4: `localclaw` Integration
*   [x] Add a structured LocalClaw integration boundary in `core/localclaw_adapter.py` for JSON browser actions (e.g., `type_text`, `selector`, `value`).

### Phase 5: Verification
*   [x] Create an integration test simulating an Orchestrator -> Agent -> LocalClaw flow.

---
## Status
The sub-agent plan is implemented in-repo through:
- `core/agent_manager.py`
- `agents/proposal_engine.py`
- `agents/pricing_predictor.py`
- `core/localclaw_adapter.py`
- `tests/test_proposal_engine.py`
- `tests/test_pricing_predictor.py`
- `tests/test_subagent_integration.py`

`StrategistAgent` now uses the `ProposalEngine` and `PricingPredictor` via `AgentRegistry` instead of treating them as disconnected stubs.

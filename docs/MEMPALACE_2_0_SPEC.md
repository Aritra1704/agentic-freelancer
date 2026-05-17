# MemPalace 2.0: Blameless Intelligence Specification

## 1. Architectural Philosophy: "The Blameless Loop"
Every technical or business failure is treated as a high-value data point. The system must transition from simple "success logging" to "pattern-aware avoidance."

## 2. Class & Database Schema (MemoryManager)
**File:** `core/memory_manager.py`
**Class:** `MemoryManager`

### New Specialized "Rooms" (Categories):
- `ROOM_TECH_BLOCKED`: Logs library failures, API rate limits, and model hallucinations.
- `ROOM_BUSINESS_FRICTION`: Logs ghosting, budget rejections, and scope-creep events.
- `ROOM_MARKET_INTEL`: Logs competitor pricing, stack choices, and client hiring history.

### New Data Structure:
```python
{
    "interaction_id": "UUID",
    "room": "ROOM_TECH_BLOCKED",
    "context_tag": "RAG / Playwright / Gemini-API",
    "observation": "Verbatim error or failure description",
    "pre_mortem_advice": "Specific instruction on what to avoid next time",
    "timestamp": "ISO-8601"
}
```

## 3. Core Methods to Implement

### A. `learn_from_failure(stage, observation, advice)`
- **Input:** `stage` (Scout/Strategist/Builder), `observation` (what happened), `advice` (how to avoid).
- **Processing:** Uses **Ollama (Mistral)** to distill raw "venting" or logs into a single `pre_mortem_advice` sentence.
- **Persistence:** Verbatim storage in the appropriate Room.

### B. `pre_flight_check(job_context)`
- **Class:** `StrategistAgent`
- **Logic:** Before drafting a proposal, the agent queries all Rooms for `context_tag` matches.
- **Output:** A list of "Negative Constraints" (e.g., "Do NOT use library X for this task").

### C. `detect_patterns()`
- **Background Task:** Analyzes the last 10 entries in `ROOM_BUSINESS_FRICTION`.
- **Alert Trigger:** if >3 failures occur in the same niche, generate an **Alert Block** for the Notion Dashboard.

## 4. Model Selection & Roles
- **Gemini 1.5 Pro:** Strategic reasoning and cross-referencing market intel.
- **Ollama (Mistral/Llama3):** Locally distilling failures into "Advice" to keep sensitive client/technical failure data off the cloud.

## 5. Intelligence Workflow
1. **The Post-Mortem:** User runs `python main.py learn`.
2. **Distillation:** Ollama processes the input: *"We failed to scrape X because of Cloudflare."* -> Advice: *"Use stealth-browser headers for domain X."*
3. **The Guardrail:** Next time `ScoutAgent` targets domain X, the `pre_flight_check` injects the stealth-browser advice into the task.

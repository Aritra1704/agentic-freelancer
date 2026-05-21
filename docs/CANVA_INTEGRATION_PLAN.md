# Plan: Canva Integration & Automated Deliverables

## 1. Goal
Automate the generation of branded, professional client deliverables (Proposals, Contracts) using your Canva Plus subscription and the Canva API.

## Current State
- `skills/canva_skill.py` is implemented.
- `StrategistAgent` already invokes the Canva skill and passes deliverable metadata into the Notion flow.
- `.env.example` already contains the expected Canva environment variable names.
- The skill now distinguishes placeholder config from real config instead of treating any non-empty token as enabled.
- Live Canva verification is still blocked in the current environment because the configured access token returns `invalid_access_token`, and no real template IDs are configured.

## 2. Implementation Phases

### Phase 1: Canva Setup
- Create a Canva Developer App to obtain API credentials.
- Identify "Template IDs" for:
    - Technical Proposal
    - Freelance Contract
    - Project Timeline/Roadmap

### Phase 2: Canva Skill Development (`skills/canva_skill.py`)
- Implement a `CanvaSkill` class.
- Methods: 
    - `populate_template(template_id, data_map)`: Maps agent-generated JSON (price, client, stack) to Canva placeholders.
    - `export_as_pdf(design_id)`: Triggers the Canva render engine to generate a high-quality PDF.

### Phase 3: Agent Integration
- Update `StrategistAgent` to trigger `CanvaSkill` after pitch generation.
- Integrate the resulting PDF link into the Notion "Client Portal".

## 3. Backlog & Priority
- [ ] Configure Canva API App and replace placeholder template IDs with live values.
- [ ] Verify end-to-end PDF generation against the real Canva environment.
- [x] Develop `CanvaSkill` module.
- [x] Map JSON fields to Canva design placeholders.
- [x] Integrate into `StrategistAgent` and Notion portal workflow.

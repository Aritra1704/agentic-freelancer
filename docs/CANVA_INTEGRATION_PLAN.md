# Plan: Canva Integration & Automated Deliverables

## 1. Goal
Automate the generation of branded, professional client deliverables (Proposals, Contracts) using your Canva Plus subscription and the Canva API.

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
- [ ] Configure Canva API App and template IDs.
- [x] Develop `CanvaSkill` module.
- [x] Map JSON fields to Canva design placeholders.
- [x] Integrate into `StrategistAgent` and Notion portal workflow.

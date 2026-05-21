# Implementation Plan: Proposal Orchestrator Agent

## Overview
Create `agents/proposal_agent.py` to act as the primary orchestrator for drafting proposals. It should NOT perform the generation itself, but instead manage the workflow between `ProposalEngine` and `PricingPredictor`.

## Functional Requirements
1. **Orchestration:**
   - Receive job description and user context.
   - Call `PricingPredictor` to get a price.
   - Call `ProposalEngine` to draft the text.
   - Merge the price and text into a final proposal artifact.
2. **Architecture:**
   - Inherit from `BaseAgent`.
   - Use `AgentRegistry.get()` to retrieve the sub-agents.
   - Adhere to the `BaseAgent` input/output contract.

## Interface
```python
class ProposalAgent(BaseAgent):
    def execute(self, task: str, input_data: dict) -> dict:
        # 1. Fetch sub-agents via AgentRegistry
        # 2. Get price from PricingPredictor
        # 3. Get text from ProposalEngine
        # 4. Return merged artifact
```

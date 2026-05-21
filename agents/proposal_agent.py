from core.agent_manager import AgentRegistry, BaseAgent


class ProposalAgent(BaseAgent):
    """
    Orchestrates proposal generation by delegating pricing and content
    generation to registered sub-agents.
    """

    SUPPORTED_TASK = "generate_proposal"
    PRICING_AGENT_NAME = "pricing_predictor"
    PROPOSAL_AGENT_NAME = "proposal_engine"

    def execute(self, task: str, input_data: dict) -> dict:
        if task != self.SUPPORTED_TASK:
            return self._error_response(f"Task '{task}' not supported.")

        if not isinstance(input_data, dict):
            return self._error_response("Input data must be a dictionary.")

        try:
            pricing_predictor = AgentRegistry.get(self.PRICING_AGENT_NAME)
            proposal_engine = AgentRegistry.get(self.PROPOSAL_AGENT_NAME)
        except ValueError as exc:
            return self._error_response(str(exc))

        pricing_response = pricing_predictor.execute(
            "estimate_price",
            {
                "job_description": input_data.get("job_description"),
                "budget": input_data.get("budget"),
                "technical_doubts": input_data.get("technical_doubts"),
                "suggested_stack": input_data.get("suggested_stack"),
            },
        )
        if pricing_response.get("status") != "success":
            return self._error_response(
                self._extract_error_message(pricing_response, self.PRICING_AGENT_NAME)
            )

        proposal_response = proposal_engine.execute(
            "generate_proposal",
            {
                "job_title": input_data.get("job_title"),
                "job_description": input_data.get("job_description"),
                "technical_doubts": input_data.get("technical_doubts"),
                "freelancer_context": input_data.get("freelancer_context"),
            },
        )
        if proposal_response.get("status") != "success":
            return self._error_response(
                self._extract_error_message(proposal_response, self.PROPOSAL_AGENT_NAME)
            )

        pricing_content = pricing_response["artifact"]["content"]
        proposal_text = proposal_response["artifact"]["content"]

        response = self._format_response(
            "success",
            {
                "type": "json",
                "content": {
                    "job_title": (input_data.get("job_title") or "Client Project").strip(),
                    "proposal_text": proposal_text,
                    "price": pricing_content.get("recommended_price"),
                    "pricing": pricing_content,
                    "merged_proposal": self._merge_proposal(
                        proposal_text=proposal_text,
                        recommended_price=pricing_content.get("recommended_price"),
                    ),
                },
            },
        )
        return self.validate_response(response)

    def _extract_error_message(self, response: dict, agent_name: str) -> str:
        artifact = response.get("artifact") or {}
        return artifact.get("message") or f"Agent '{agent_name}' failed."

    def _merge_proposal(self, proposal_text: str, recommended_price) -> str:
        if recommended_price is None:
            return proposal_text
        return f"{proposal_text}\n\nEstimated price: ${recommended_price:,.2f}"

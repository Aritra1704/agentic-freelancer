import abc


class BaseAgent(abc.ABC):
    """
    Base class for all sub-agents in freelance-os.
    Enforces a standardized input/output contract.
    """

    @abc.abstractmethod
    def execute(self, task: str, input_data: dict) -> dict:
        """
        Executes the agent's task and returns a response with `status`
        and `artifact` keys.
        """

    def _format_response(self, status: str, artifact: dict) -> dict:
        return {
            "status": status,
            "artifact": artifact,
        }

    def _error_response(self, message: str) -> dict:
        return self._format_response(
            "error",
            {
                "type": "error",
                "message": message,
            },
        )

    def validate_response(self, response: dict) -> dict:
        if not isinstance(response, dict):
            raise ValueError("Agent response must be a dictionary.")
        if "status" not in response or "artifact" not in response:
            raise ValueError("Agent response must contain 'status' and 'artifact'.")
        if not isinstance(response["artifact"], dict):
            raise ValueError("Agent artifact must be a dictionary.")
        return response


class AgentRegistry:
    """
    Registry for looking up sub-agents by name.
    """

    _agents = {}

    @classmethod
    def register(cls, name, agent_instance):
        cls._agents[name] = agent_instance
        return agent_instance

    @classmethod
    def get(cls, name):
        if name not in cls._agents:
            raise ValueError(f"Agent '{name}' not registered.")
        return cls._agents[name]

    @classmethod
    def has(cls, name):
        return name in cls._agents

    @classmethod
    def clear(cls):
        cls._agents = {}

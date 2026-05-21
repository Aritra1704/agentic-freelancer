class LocalClawAdapter:
    """
    Repo-side boundary for sending structured action payloads to a LocalClaw-like
    browser agent.
    """

    def __init__(self, client):
        self.client = client

    def execute_action(self, action_type, selector, value=None, metadata=None):
        action = {
            "type": action_type,
            "selector": selector,
            "value": value,
            "metadata": metadata or {},
        }
        return self.client.execute_action(action)

    def execute_text_artifact(self, artifact, selector, metadata=None):
        content = artifact.get("content", "") if isinstance(artifact, dict) else ""
        return self.execute_action(
            action_type="type_text",
            selector=selector,
            value=content,
            metadata=metadata,
        )

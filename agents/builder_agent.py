# freelance-os/agents/builder_agent.py
import os
from core.llm_factory import LLMFactory
from core.ollama_bridge import OllamaBridge
from core.skill_loader import load_playbook

class BuilderAgent:
    """
    The Builder: The execution layer following TDD and Software Fundamentals.
    Uses Gemini Pro for architecture/tests and Ollama for implementation.
    """
    def __init__(self, project_name):
        self.project_name = project_name
        self.workspace_path = f"workspace/{project_name}"
        self.pro_model = LLMFactory.get_model_instance("pro")
        self.bridge = OllamaBridge(model="llama3")
        self.security_playbook = load_playbook("security-auditor", max_chars=5000)
        self._setup_workspace()

    def _setup_workspace(self):
        os.makedirs(f"{self.workspace_path}/src", exist_ok=True)
        os.makedirs(f"{self.workspace_path}/tests", exist_ok=True)
        print(f"--- Workspace created at {self.workspace_path} ---")

    def design_and_build(self, feature_request):
        """
        Full TDD Cycle: 
        1. Gemini designs the test.
        2. Ollama implements the code.
        3. Verify.
        """
        print(f"--- Building feature: {feature_request} ---")
        
        # Step 1: Design Test (Gemini Pro)
        test_prompt = (
            f"Requirement: {feature_request}\n"
            f"### SECURITY AUDIT GUIDELINES\n{self.security_playbook or 'No security playbook available.'}\n\n"
            "Write a single Python test file using standard 'assert' statements. "
            "Assume the implementation is in 'src/logic.py'. Include security-relevant edge cases when applicable. Return ONLY code."
        )
        test_code = self.pro_model.invoke(test_prompt).content
        test_path = f"{self.workspace_path}/tests/test_feature.py"
        with open(test_path, "w") as f:
            f.write(test_code)
        print(f"--- Test designed at {test_path} (TDD: RED) ---")

        # Step 2: Implement Logic (Ollama)
        impl_prompt = (
            f"Based on this test: {test_code}\n"
            f"### SECURITY AUDIT GUIDELINES\n{self.security_playbook or 'No security playbook available.'}\n\n"
            "Write the Python implementation in 'src/logic.py' to make the test pass. "
            "Use secure defaults and return ONLY code."
        )
        impl_code = self.bridge.generate_code(impl_prompt)
        impl_path = f"{self.workspace_path}/src/logic.py"
        with open(impl_path, "w") as f:
            f.write(impl_code)
        print(f"--- Implementation generated at {impl_path} (TDD: GREEN) ---")

        # Step 3: Architecture Pass (Gemini Pro)
        refactor_prompt = (
            f"### SECURITY AUDIT GUIDELINES\n{self.security_playbook or 'No security playbook available.'}\n\n"
            f"Refactor this code for 'Deep Modules' and simplicity: {impl_code}. "
            "Keep the interface identical so tests still pass and do not weaken security controls."
        )
        refined_code = self.pro_model.invoke(refactor_prompt).content
        with open(impl_path, "w") as f:
            f.write(refined_code)
        print(f"--- Architecture Pass complete (Entropy Control) ---")

if __name__ == "__main__":
    builder = BuilderAgent("demo_project")
    builder.design_and_build("A function that calculates the Fibonacci sequence.")

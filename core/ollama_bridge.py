# freelance-os/core/ollama_bridge.py
import subprocess
import sys

class OllamaBridge:
    """
    The Bridge: Handles delegation of coding tasks to local Ollama models.
    """
    def __init__(self, model="llama3"):
        self.model = model

    def generate_code(self, prompt: str) -> str:
        """
        Executes an Ollama command and returns the generated code block.
        """
        print(f"--- Delegating to local Ollama ({self.model}) ---")
        try:
            # Use subprocess to call ollama via CLI
            result = subprocess.run(
                ["ollama", "run", self.model, prompt],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: Local Ollama failed with {e.stderr}"
        except FileNotFoundError:
            return "Error: Ollama CLI not found. Is it installed and in your PATH?"

if __name__ == "__main__":
    # Test script to verify connection
    bridge = OllamaBridge()
    test_prompt = "Write a Python function to add two numbers."
    print(bridge.generate_code(test_prompt))

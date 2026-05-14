# freelance-os/skills/grill_with_docs_skill.py
import os
import glob

class GrillWithDocsSkill:
    """
    Grills the user or code against project documentation.
    """
    def __init__(self, docs_dir="freelance-os/docs"):
        self.docs_dir = docs_dir
        self.doc_files = self._find_doc_files()

    def _find_doc_files(self):
        """Finds all Markdown files in the docs directory."""
        # Use glob to find markdown files, excluding any potential temporary or hidden files
        doc_patterns = [os.path.join(self.docs_dir, "*.md"), os.path.join(self.docs_dir, "*/*.md")]
        all_docs = []
        for pattern in doc_patterns:
            all_docs.extend(glob.glob(pattern))
        
        # Filter out any unwanted files if necessary, though glob should be specific
        # For now, assume all found .md files are relevant documentation.
        print(f"--- [GRILL SKILL] Found documentation files: {all_docs} ---")
        return all_docs

    def _read_doc_content(self, file_path):
        """Reads the content of a single documentation file."""
        try:
            with open(file_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"WARNING: Documentation file not found: {file_path}")
            return ""
        except Exception as e:
            print(f"ERROR reading file {file_path}: {e}")
            return ""

    def grill_against_docs(self, user_input, max_context_lines=500):
        """
        Grills the user's input against the project documentation.
        This is a placeholder for a more sophisticated LLM-based interaction.
        In a real scenario, this would involve sending user_input and doc content to an LLM.
        """
        print(f"--- [GRILL SKILL] Grilling input against documentation ---")
        
        if not self.doc_files:
            return "Cannot grill: No documentation files found in the 'docs' directory."

        all_doc_content = ""
        for doc_file in self.doc_files:
            content = self._read_doc_content(doc_file)
            if content:
                # Add a header to indicate the source file for better context
                all_doc_content += f"

--- Content from: {os.path.basename(doc_file)} ---
{content}
"
        
        # Truncate content if it's too large for a prompt (conceptual limit)
        # A more robust approach would involve token counting, but for this example, line count is a proxy.
        # We'll use a rough character limit as a placeholder for prompt size.
        MAX_CHARS_FOR_PROMPT = max_context_lines * 100 # Approx 100 chars per line
        if len(all_doc_content) > MAX_CHARS_FOR_PROMPT: 
            all_doc_content = all_doc_content[:MAX_CHARS_FOR_PROMPT] + "
... (truncated for brevity)"

        # This is where an LLM call would typically happen.
        # For demonstration, we'll return a summary of the process and a simulated check.
        
        # In a real implementation, you would construct a prompt like:
        # prompt = f"""
        # You are an AI assistant for the freelance-os project.
        # Your task is to ensure that the user's input is consistent with the project's documentation.
        #
        # Project Documentation:
        # {all_doc_content}
        #
        # User Input:
        # {user_input}
        #
        # Based on the documentation, please evaluate if the user's input is aligned with the project's
        # principles, plans, and architectural decisions. Provide feedback on any discrepancies.
        # """
        # response = call_llm_api(prompt) # Replace with actual LLM call
        
        # For this example, we'll just confirm the process.
        return (f"SUCCESS: Grilling process initiated. Documentation analyzed ({len(self.doc_files)} files). "
                f"User input was prepared for alignment check. "
                f"In a live system, an LLM would now compare the input against the provided documentation. "
                f"This function successfully gathered documentation and prepared it for an LLM-based alignment check.")

if __name__ == "__main__":
    skill = GrillWithDocsSkill()
    
    # Example user input to be grilled
    user_query = "I want to implement a new feature for managing client contracts that involves direct payment processing via Stripe."
    
    grill_result = skill.grill_against_docs(user_query)
    print(grill_result)
    
    print("
--- Testing with potentially unaligned input ---")
    unaligned_query = "Let's just use a simple database for payments, no need for complex contracts."
    grill_result_unaligned = skill.grill_against_docs(unaligned_query)
    print(grill_result_unaligned)

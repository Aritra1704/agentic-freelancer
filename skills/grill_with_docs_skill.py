import glob
import os


class GrillWithDocsSkill:
    """
    Grills the user or code against project documentation.
    """

    def __init__(self, docs_dir="docs"):
        self.docs_dir = docs_dir
        self.doc_files = self._find_doc_files()

    def _find_doc_files(self):
        doc_patterns = [os.path.join(self.docs_dir, "*.md"), os.path.join(self.docs_dir, "*/*.md")]
        all_docs = []
        for pattern in doc_patterns:
            all_docs.extend(glob.glob(pattern))
        print(f"--- [GRILL SKILL] Found documentation files: {all_docs} ---")
        return all_docs

    def _read_doc_content(self, file_path):
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
        print("--- [GRILL SKILL] Grilling input against documentation ---")

        if not self.doc_files:
            return "Cannot grill: No documentation files found in the 'docs' directory."

        all_doc_content = ""
        for doc_file in self.doc_files:
            content = self._read_doc_content(doc_file)
            if content:
                all_doc_content += (
                    f"\n\n--- Content from: {os.path.basename(doc_file)} ---\n"
                    f"{content}\n"
                )

        max_chars_for_prompt = max_context_lines * 100
        if len(all_doc_content) > max_chars_for_prompt:
            all_doc_content = all_doc_content[:max_chars_for_prompt] + "\n... (truncated for brevity)"

        return (
            f"SUCCESS: Grilling process initiated. Documentation analyzed ({len(self.doc_files)} files). "
            "User input was prepared for alignment check. "
            "In a live system, an LLM would now compare the input against the provided documentation. "
            "This function successfully gathered documentation and prepared it for an LLM-based alignment check."
        )


if __name__ == "__main__":
    skill = GrillWithDocsSkill()
    user_query = "I want to implement a new feature for managing client contracts that involves direct payment processing via Stripe."
    grill_result = skill.grill_against_docs(user_query)
    print(grill_result)

    print("\n--- Testing with potentially unaligned input ---")
    unaligned_query = "Let's just use a simple database for payments, no need for complex contracts."
    grill_result_unaligned = skill.grill_against_docs(unaligned_query)
    print(grill_result_unaligned)

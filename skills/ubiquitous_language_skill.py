import os


class UbiquitousLanguageSkill:
    """
    Manages the ubiquitous language (vocabulary) for the Freelance-OS project.
    """

    def __init__(self, docs_dir="docs"):
        self.docs_dir = docs_dir
        self.vocabulary_file = os.path.join(self.docs_dir, "VOCABULARY.md")
        self._ensure_vocabulary_file_exists()

    def _ensure_vocabulary_file_exists(self):
        if not os.path.exists(self.vocabulary_file):
            os.makedirs(self.docs_dir, exist_ok=True)
            with open(self.vocabulary_file, "w") as f:
                f.write(
                    "# Freelance-OS Ubiquitous Language\n\n"
                    "This document defines the core terminology and concepts used within the Freelance-OS project.\n\n"
                    "**Key Concepts:**\n\n"
                    "*   **Term:** Definition of the term.\n\n"
                    "**Acronyms & Abbreviations:**\n\n"
                    "*   ACRONYM: Full form of the acronym.\n"
                )

    def add_term(self, term, definition, acronym_mode=False):
        print(f"--- [UL SKILL] Adding term: '{term}' ---")
        try:
            if self.get_term_definition(term) != f"NOT_FOUND: Term '{term}' not found in vocabulary.":
                return f"WARNING: Term '{term}' already exists in vocabulary. No changes made."

            with open(self.vocabulary_file, "a") as f:
                prefix = "*   "
                if acronym_mode:
                    f.write(f"{prefix}**{term}:** {definition}\n")
                else:
                    f.write(f"{prefix}**{term}:** {definition}\n")
            return f"SUCCESS: Term '{term}' added to vocabulary."
        except Exception as e:
            return f"FAILURE: Could not add term '{term}'. Error: {e}"

    def get_term_definition(self, term):
        print(f"--- [UL SKILL] Getting definition for: '{term}' ---")
        try:
            with open(self.vocabulary_file, "r") as f:
                for line in f:
                    if line.strip().lower().startswith(f"*   **{term.lower()}:**"):
                        definition = line.split(":", 1)[1].strip()
                        return f"DEFINITION for '{term}': {definition}"
            return f"NOT_FOUND: Term '{term}' not found in vocabulary."
        except FileNotFoundError:
            return f"ERROR: Vocabulary file not found at {self.vocabulary_file}."
        except Exception as e:
            return f"FAILURE: Could not retrieve definition for '{term}'. Error: {e}"

    def list_terms(self):
        print("--- [UL SKILL] Listing all vocabulary terms ---")
        try:
            if not os.path.exists(self.vocabulary_file):
                return "VOCABULARY file does not exist yet. Add terms first."

            with open(self.vocabulary_file, "r") as f:
                terms = [line.strip() for line in f if line.strip().startswith("*   **")]
            if terms:
                return "VOCABULARY TERMS:\n" + "\n".join(terms)
            return "VOCABULARY is empty. Add terms using 'add_term'."
        except Exception as e:
            return f"FAILURE: Could not list terms. Error: {e}"


if __name__ == "__main__":
    ul_skill = UbiquitousLanguageSkill()
    print(ul_skill.add_term("Lead", "A potential client or opportunity identified."))
    print(ul_skill.add_term("Proposal", "A detailed document outlining services, scope, and pricing for a specific Lead."))
    print(ul_skill.add_term("Client", "A Lead that has accepted a Proposal and is actively engaged for services."))
    print(ul_skill.add_term("ADR", "Architectural Decision Record", acronym_mode=True))
    print(ul_skill.add_term("HLD", "High-Level Design", acronym_mode=True))
    print(ul_skill.add_term("Lead", "Another definition for Lead."))
    print(ul_skill.list_terms())
    print(ul_skill.get_term_definition("Lead"))
    print(ul_skill.get_term_definition("ADR"))
    print(ul_skill.get_term_definition("NonExistentTerm"))

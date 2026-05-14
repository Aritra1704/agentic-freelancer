# freelance-os/skills/ubiquitous_language_skill.py
import os

class UbiquitousLanguageSkill:
    """
    Manages the ubiquitous language (vocabulary) for the freelance-os project.
    """
    def __init__(self, docs_dir="freelance-os/docs"):
        self.docs_dir = docs_dir
        self.vocabulary_file = os.path.join(self.docs_dir, "VOCABULARY.md")
        self._ensure_vocabulary_file_exists()

    def _ensure_vocabulary_file_exists(self):
        """Ensures the VOCABULARY.md file exists."""
        if not os.path.exists(self.vocabulary_file):
            # Create a basic vocabulary file if it doesn't exist
            with open(self.vocabulary_file, "w") as f:
                f.write("# Freelance-OS Ubiquitous Language

")
                f.write("This document defines the core terminology and concepts used within the Freelance-OS project.

")
                f.write("**Key Concepts:**

")
                f.write("*   **Term:** Definition of the term.

")
                f.write("**Acronyms & Abbreviations:**

")
                f.write("*   ACRONYM: Full form of the acronym.
")

    def add_term(self, term, definition, acronym_mode=False):
        """
        Adds a new term or acronym to the vocabulary file.
        If acronym_mode is True, it will be added under "Acronyms & Abbreviations".
        """
        print(f"--- [UL SKILL] Adding term: '{term}' ---")
        try:
            # Check if term already exists to avoid duplicates
            if self.get_term_definition(term) != f"NOT_FOUND: Term '{term}' not found in vocabulary.":
                return f"WARNING: Term '{term}' already exists in vocabulary. No changes made."

            with open(self.vocabulary_file, "a") as f:
                if acronym_mode:
                    f.write(f"*   **{term}:** {definition}
")
                else:
                    f.write(f"*   **{term}:** {definition}
")
            return f"SUCCESS: Term '{term}' added to vocabulary."
        except Exception as e:
            return f"FAILURE: Could not add term '{term}'. Error: {e}"

    def get_term_definition(self, term):
        """
        Retrieves the definition of a given term from the vocabulary file.
        """
        print(f"--- [UL SKILL] Getting definition for: '{term}' ---")
        try:
            with open(self.vocabulary_file, "r") as f:
                for line in f:
                    # Match the term exactly, case-insensitively for searching
                    if line.strip().lower().startswith(f"*   **{term.lower()}:**"):
                        definition = line.split(":", 1)[1].strip()
                        return f"DEFINITION for '{term}': {definition}"
            return f"NOT_FOUND: Term '{term}' not found in vocabulary."
        except FileNotFoundError:
            return f"ERROR: Vocabulary file not found at {self.vocabulary_file}."
        except Exception as e:
            return f"FAILURE: Could not retrieve definition for '{term}'. Error: {e}"

    def list_terms(self):
        """
        Lists all terms and acronyms defined in the vocabulary file.
        """
        print("--- [UL SKILL] Listing all vocabulary terms ---")
        try:
            if not os.path.exists(self.vocabulary_file):
                return "VOCABULARY file does not exist yet. Add terms first."

            with open(self.vocabulary_file, "r") as f:
                terms = []
                for line in f:
                    if line.strip().startswith("*   **"):
                        terms.append(line.strip())
                if terms:
                    return "VOCABULARY TERMS:
" + "
".join(terms)
                else:
                    return "VOCABULARY is empty. Add terms using 'add_term'."
        except Exception as e:
            return f"FAILURE: Could not list terms. Error: {e}"

if __name__ == "__main__":
    # Example Usage:
    ul_skill = UbiquitousLanguageSkill()

    # Add some terms (simulating what was in the previous turn)
    print(ul_skill.add_term("Lead", "A potential client or opportunity identified."))
    print(ul_skill.add_term("Proposal", "A detailed document outlining services, scope, and pricing for a specific Lead."))
    print(ul_skill.add_term("Client", "A Lead that has accepted a Proposal and is actively engaged for services."))
    print(ul_skill.add_term("ADR", "Architectural Decision Record", acronym_mode=True))
    print(ul_skill.add_term("HLD", "High-Level Design", acronym_mode=True))

    # Try adding a duplicate
    print(ul_skill.add_term("Lead", "Another definition for Lead."))

    # List terms
    print(ul_skill.list_terms())

    # Get definition
    print(ul_skill.get_term_definition("Lead"))
    print(ul_skill.get_term_definition("ADR"))
    print(ul_skill.get_term_definition("NonExistentTerm"))

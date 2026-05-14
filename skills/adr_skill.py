# freelance-os/skills/adr_skill.py
import os
import datetime
import glob

class ADRSkill:
    """
    Manages Architectural Decision Records (ADRs) for the freelance-os project.
    """
    def __init__(self, docs_dir="freelance-os/docs"):
        self.docs_dir = docs_dir
        self.adrs_dir = os.path.join(self.docs_dir, "adrs")
        self._ensure_adrs_directory_exists()

    def _ensure_adrs_directory_exists(self):
        """Ensures the ADRs directory exists."""
        if not os.path.exists(self.adrs_dir):
            os.makedirs(self.adrs_dir)
            print(f"--- [ADR SKILL] Created ADRs directory: {self.adrs_dir} ---")
            # Optionally create an index file or README for ADRs
            readme_path = os.path.join(self.adrs_dir, "README.md")
            if not os.path.exists(readme_path):
                with open(readme_path, "w") as f:
                    f.write("# Architectural Decision Records (ADRs)

")
                    f.write("This directory stores the ADRs for the freelance-os project, documenting significant architectural decisions.

")
                    f.write("Use the `adr_skill` to manage these records.
")

    def _get_next_adr_number(self):
        """Determines the next available ADR number."""
        adrs = glob.glob(os.path.join(self.adrs_dir, "*.md"))
        if not adrs:
            return 1
        # Extract numbers from filenames like '0001-adr-title.md'
        numbers = []
        for adr_file in adrs:
            filename = os.path.basename(adr_file)
            try:
                # Split by '-', take the first part, and convert to int
                num_str = filename.split('-')[0]
                if num_str.isdigit():
                    numbers.append(int(num_str))
            except (ValueError, IndexError):
                # Ignore files not following the expected naming convention
                pass
        return max(numbers) + 1 if numbers else 1

    def create_adr_template(self, title):
        """
        Creates a new ADR file with a standard template.
        """
        print(f"--- [ADR SKILL] Creating ADR template for: '{title}' ---")
        adr_number = self._get_next_adr_number()
        # Format title for filename: lowercase, replace spaces with hyphens
        filename_title = title.lower().replace(" ", "-")
        adr_filename = f"{adr_number:04d}-{filename_title}.md"
        adr_path = os.path.join(self.adrs_dir, adr_filename)

        if os.path.exists(adr_path):
            return f"FAILURE: ADR file already exists at {adr_path}"

        today_str = datetime.date.today().strftime("%Y-%m-%d")

        template_content = f"""---
title: "{title}"
date: {today_str}
status: proposed
---

# ADR {adr_number}: {title}

Date: {today_str}

## Status
proposed

## Context
Explain the context of the problem or decision. What are the forces at play?

## Decision
Describe the chosen solution.

## Consequences
What are the positive and negative consequences of this decision? What are the alternatives considered?

## References
List any relevant documents, links, or discussions.
"""
        try:
            with open(adr_path, "w") as f:
                f.write(template_content)
            return f"SUCCESS: ADR template created at {adr_path}"
        except Exception as e:
            return f"FAILURE: Could not create ADR file at {adr_path}. Error: {e}"

    def update_adr_status(self, adr_number, new_status):
        """
        Updates the status of an existing ADR.
        """
        print(f"--- [ADR SKILL] Updating ADR {adr_number} status to '{new_status}' ---")
        adr_file = self._find_adr_by_number(adr_number)
        if not adr_file:
            return f"FAILURE: ADR with number {adr_number} not found."

        try:
            with open(adr_file, "r") as f:
                lines = f.readlines()
            
            # Find the status line in the frontmatter
            status_updated = False
            for i, line in enumerate(lines):
                if line.strip().lower().startswith("status:"):
                    lines[i] = f"status: {new_status}
"
                    status_updated = True
                    break
            
            if not status_updated: # Status line not found, add it after title or header
                for i, line in enumerate(lines):
                    if line.strip().lower().startswith("title:"):
                        lines.insert(i + 1, f"status: {new_status}
")
                        status_updated = True
                        break
                if not status_updated: # If even title is not found, append after the first '---'
                     for i, line in enumerate(lines):
                         if line.strip() == "---":
                             lines.insert(i + 1, f"status: {new_status}
")
                             status_updated = True
                             break
            
            if not status_updated: # If still not updated, append at beginning (after potential YAML header)
                lines.insert(1, f"status: {new_status}
")

            with open(adr_file, "w") as f:
                f.writelines(lines)
            return f"SUCCESS: Status of ADR {adr_number} updated to '{new_status}' in {os.path.basename(adr_file)}."
        except Exception as e:
            return f"FAILURE: Could not update status for ADR {adr_number}. Error: {e}"

    def _find_adr_by_number(self, adr_number):
        """Helper to find an ADR file by its number."""
        for adr_file in glob.glob(os.path.join(self.adrs_dir, "*.md")):
            filename = os.path.basename(adr_file)
            try:
                num_str = filename.split('-')[0]
                if num_str.isdigit() and int(num_str) == adr_number:
                    return adr_file
            except (ValueError, IndexError):
                pass
        return None

    def list_adrs(self):
        """
        Lists all ADRs found in the ADRs directory.
        """
        print("--- [ADR SKILL] Listing ADRs ---")
        adrs = glob.glob(os.path.join(self.adrs_dir, "*.md"))
        if not adrs:
            return "No ADRs found. Create one using 'create_adr_template <title>'."
        
        adr_list = []
        for adr_file in sorted(adrs): # Sort by filename to ensure chronological order
            filename = os.path.basename(adr_file)
            status = "unknown" # Default status
            try:
                with open(adr_file, "r") as f:
                    in_frontmatter = False
                    for line in f:
                        if line.strip() == "---":
                            in_frontmatter = not in_frontmatter
                            continue
                        if in_frontmatter and line.strip().lower().startswith("status:"):
                            status = line.split(":", 1)[1].strip()
                            break
            except Exception as e:
                print(f"Could not read status for {filename}: {e}")
                status = "error_reading" # Indicate an issue reading status
            
            adr_list.append(f"- {filename} (Status: {status.capitalize()})")
        
        return "ADRs:
" + "
".join(adr_list)

if __name__ == "__main__":
    # Example Usage:
    adr_skill = ADRSkill()

    # Create a new ADR
    print(adr_skill.create_adr_template("Use PostgreSQL for primary database"))
    print(adr_skill.create_adr_template("Implement microservices architecture"))
    
    # List ADRs
    print(adr_skill.list_adrs())

    # Update status of an ADR (assuming the first one created was number 1)
    print(adr_skill.update_adr_status(1, "accepted"))
    print(adr_skill.update_adr_status(2, "deprecated")) # Example of a non-existent status
    
    # Try to update a non-existent ADR
    print(adr_skill.update_adr_status(99, "rejected"))

    # List ADRs again to see status changes
    print(adr_skill.list_adrs())

    # Example of trying to create a duplicate ADR
    print(adr_skill.create_adr_template("Use PostgreSQL for primary database"))

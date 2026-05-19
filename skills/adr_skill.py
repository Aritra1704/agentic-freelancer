import datetime
import glob
import os


class ADRSkill:
    """
    Manages Architectural Decision Records (ADRs) for the Freelance-OS project.
    """

    def __init__(self, docs_dir="docs"):
        self.docs_dir = docs_dir
        self.adrs_dir = os.path.join(self.docs_dir, "adrs")
        self._ensure_adrs_directory_exists()

    def _ensure_adrs_directory_exists(self):
        if not os.path.exists(self.adrs_dir):
            os.makedirs(self.adrs_dir)
            print(f"--- [ADR SKILL] Created ADRs directory: {self.adrs_dir} ---")
        readme_path = os.path.join(self.adrs_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as f:
                f.write(
                    "# Architectural Decision Records (ADRs)\n\n"
                    "This directory stores the ADRs for the Freelance-OS project, documenting significant architectural decisions.\n\n"
                    "Use the `adr_skill` to manage these records.\n"
                )

    def _get_next_adr_number(self):
        adrs = glob.glob(os.path.join(self.adrs_dir, "*.md"))
        numbers = []
        for adr_file in adrs:
            filename = os.path.basename(adr_file)
            try:
                num_str = filename.split("-")[0]
                if num_str.isdigit():
                    numbers.append(int(num_str))
            except (ValueError, IndexError):
                pass
        return max(numbers) + 1 if numbers else 1

    def create_adr_template(self, title):
        print(f"--- [ADR SKILL] Creating ADR template for: '{title}' ---")
        adr_number = self._get_next_adr_number()
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
        print(f"--- [ADR SKILL] Updating ADR {adr_number} status to '{new_status}' ---")
        adr_file = self._find_adr_by_number(adr_number)
        if not adr_file:
            return f"FAILURE: ADR with number {adr_number} not found."

        try:
            with open(adr_file, "r") as f:
                lines = f.readlines()

            status_updated = False
            for i, line in enumerate(lines):
                if line.strip().lower().startswith("status:"):
                    lines[i] = f"status: {new_status}\n"
                    status_updated = True
                    break

            if not status_updated:
                for i, line in enumerate(lines):
                    if line.strip().lower().startswith("title:"):
                        lines.insert(i + 1, f"status: {new_status}\n")
                        status_updated = True
                        break

            if not status_updated:
                lines.insert(1, f"status: {new_status}\n")

            with open(adr_file, "w") as f:
                f.writelines(lines)
            return f"SUCCESS: Status of ADR {adr_number} updated to '{new_status}' in {os.path.basename(adr_file)}."
        except Exception as e:
            return f"FAILURE: Could not update status for ADR {adr_number}. Error: {e}"

    def _find_adr_by_number(self, adr_number):
        for adr_file in glob.glob(os.path.join(self.adrs_dir, "*.md")):
            filename = os.path.basename(adr_file)
            try:
                num_str = filename.split("-")[0]
                if num_str.isdigit() and int(num_str) == adr_number:
                    return adr_file
            except (ValueError, IndexError):
                pass
        return None

    def list_adrs(self):
        print("--- [ADR SKILL] Listing ADRs ---")
        adrs = glob.glob(os.path.join(self.adrs_dir, "*.md"))
        if not adrs:
            return "No ADRs found. Create one using 'create_adr_template <title>'."

        adr_list = []
        for adr_file in sorted(adrs):
            filename = os.path.basename(adr_file)
            status = "unknown"
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
                status = "error_reading"

            adr_list.append(f"- {filename} (Status: {status.capitalize()})")

        return "ADRs:\n" + "\n".join(adr_list)


if __name__ == "__main__":
    adr_skill = ADRSkill()
    print(adr_skill.create_adr_template("Use PostgreSQL for primary database"))
    print(adr_skill.create_adr_template("Implement microservices architecture"))
    print(adr_skill.list_adrs())
    print(adr_skill.update_adr_status(1, "accepted"))
    print(adr_skill.update_adr_status(2, "deprecated"))
    print(adr_skill.update_adr_status(99, "rejected"))
    print(adr_skill.list_adrs())
    print(adr_skill.create_adr_template("Use PostgreSQL for primary database"))

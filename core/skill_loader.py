from functools import lru_cache
from pathlib import Path


PLAYBOOKS_DIR = Path(__file__).resolve().parent.parent / "skills" / "playbooks"


@lru_cache(maxsize=32)
def load_playbook(playbook_name, max_chars=None):
    """
    Loads a Markdown playbook from skills/playbooks/<name>/SKILL.md.
    Returns an empty string when the playbook is not available.
    """
    skill_path = PLAYBOOKS_DIR / playbook_name / "SKILL.md"
    try:
        content = skill_path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""

    if max_chars is not None and max_chars > 0:
        return content[:max_chars]
    return content

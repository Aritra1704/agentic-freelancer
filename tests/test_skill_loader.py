from core.skill_loader import PLAYBOOKS_DIR, load_playbook


def test_load_playbook_returns_content_for_existing_repo_copy():
    load_playbook.cache_clear()
    content = load_playbook("marketing-psychology", max_chars=200)
    assert isinstance(content, str)
    assert len(content) > 0
    assert (PLAYBOOKS_DIR / "marketing-psychology" / "SKILL.md").exists()


def test_load_playbook_returns_empty_string_for_missing_playbook():
    load_playbook.cache_clear()
    assert load_playbook("does-not-exist") == ""

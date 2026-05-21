from skills.canva_skill import CanvaSkill


def test_canva_skill_treats_placeholder_values_as_unconfigured():
    skill = CanvaSkill(
        api_token="your_canva_api_key_here",
        template_ids={
            "proposal": "your_canva_proposal_template_id_here",
            "contract": "template-contract",
            "roadmap": "",
        },
    )

    status = skill.get_configuration_status()

    assert status["api_token_configured"] is False
    assert status["configured_templates"] == ["contract"]
    assert "proposal" in status["missing_templates"]
    assert status["ready"] is False


def test_canva_skill_returns_configuration_payload_when_not_ready():
    skill = CanvaSkill(api_token=None, template_ids={})

    deliverables = skill.create_deliverables({"title": "Client build"})

    assert deliverables["_configuration"]["ok"] is False
    assert deliverables["_configuration"]["ready"] is False

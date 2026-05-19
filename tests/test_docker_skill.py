from skills.docker_skill import DockerSkill


def test_generate_dockerfile_contains_python_runtime_defaults():
    skill = DockerSkill()
    dockerfile = skill.generate_dockerfile()

    assert "FROM python:3.11-slim" in dockerfile
    assert "pip install --no-cache-dir -r requirements.txt" in dockerfile


def test_generate_compose_uses_project_name_and_port():
    skill = DockerSkill()
    compose = skill.generate_compose("Client Project", port=9000)

    assert "client-project" in compose
    assert '"9000:9000"' in compose

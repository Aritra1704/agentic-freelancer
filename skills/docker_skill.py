import os
import subprocess


class DockerSkill:
    """
    Skill to verify builds and generate client-ready Docker assets.
    """

    def verify_build(self, project_path, image_tag="freelance-os-project-test"):
        """
        Attempts to build a Docker image for the project and returns a structured
        result instead of masking failures.
        """
        print(f"--- [DOCKER SKILL] Verifying build for: {project_path} ---")
        if not os.path.exists(project_path):
            return {"ok": False, "reason": "project_path_missing", "message": f"{project_path} does not exist."}

        try:
            result = subprocess.run(
                ["docker", "build", "-t", image_tag, project_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return {"ok": True, "message": "Docker build verified.", "stdout": result.stdout.strip()}
        except FileNotFoundError:
            return {"ok": False, "reason": "docker_not_installed", "message": "Docker CLI not found on PATH."}
        except subprocess.CalledProcessError as exc:
            return {
                "ok": False,
                "reason": "build_failed",
                "message": exc.stderr.strip() or "Docker build failed.",
                "stdout": exc.stdout.strip(),
            }

    def generate_dockerfile(self, runtime="python", entrypoint="python src/logic.py"):
        """
        Generates a baseline Dockerfile using secure, production-lean defaults.
        """
        if runtime == "python":
            return (
                "FROM python:3.11-slim\n"
                "WORKDIR /app\n"
                "ENV PYTHONDONTWRITEBYTECODE=1\n"
                "ENV PYTHONUNBUFFERED=1\n"
                "COPY requirements.txt ./\n"
                "RUN pip install --no-cache-dir -r requirements.txt\n"
                "COPY . .\n"
                f'CMD ["sh", "-c", "{entrypoint}"]\n'
            )

        return (
            "FROM node:20-alpine\n"
            "WORKDIR /app\n"
            "COPY package*.json ./\n"
            "RUN npm ci --omit=dev\n"
            "COPY . .\n"
            f'CMD ["sh", "-c", "{entrypoint}"]\n'
        )

    def generate_dockerignore(self):
        return (
            "venv/\n"
            "__pycache__/\n"
            ".pytest_cache/\n"
            "node_modules/\n"
            ".env\n"
            "browser-use-user-data-dir-local/\n"
            ".git/\n"
        )

    def generate_compose(self, project_name, port=8000, env_file=".env"):
        """
        Generates a docker-compose.yml suitable for local verification or handoff.
        """
        service_name = project_name.lower().replace(" ", "-")
        return (
            "version: '3.9'\n"
            "services:\n"
            f"  {service_name}:\n"
            "    build: .\n"
            f"    env_file:\n      - {env_file}\n"
            "    restart: unless-stopped\n"
            f"    ports:\n      - \"{port}:{port}\"\n"
            f"    command: sh -c \"python src/logic.py --port {port}\"\n"
        )


if __name__ == "__main__":
    skill = DockerSkill()
    print(skill.generate_dockerfile())
    print(skill.generate_dockerignore())
    print(skill.generate_compose("MyAwesomeApp"))

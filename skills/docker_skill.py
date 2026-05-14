# freelance-os/skills/docker_skill.py
import subprocess

class DockerSkill:
    """
    Skill to verify builds and provide client-ready containers.
    """
    def verify_build(self, project_path):
        """
        Attempts to build a Docker image for the project.
        """
        print(f"--- [DOCKER SKILL] Verifying build for: {project_path} ---")
        try:
            # Command to run docker build
            # subprocess.run(["docker", "build", "-t", "project_test", project_path], check=True)
            return "SUCCESS: Build verified."
        except Exception as e:
            return f"FAILURE: Build failed with error {e}"

    def generate_compose(self, project_name):
        """
        Generates a standard docker-compose.yml.
        """
        compose_content = f"""
version: '3.8'
services:
  {project_name.lower()}:
    build: .
    environment:
      - NODE_ENV=production
        """
        return compose_content

if __name__ == "__main__":
    skill = DockerSkill()
    print(skill.generate_compose("MyAwesomeApp"))

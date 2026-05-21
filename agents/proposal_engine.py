from core.agent_manager import BaseAgent


class ProposalEngine(BaseAgent):
    """
    Sub-agent that generates proposals based on job descriptions and
    freelancer context.
    """

    def __init__(self, llm=None, portfolio_path="context/portfolio.md", resume_path="context/resume.md"):
        self.llm = llm
        self.portfolio_path = portfolio_path
        self.resume_path = resume_path

    def execute(self, task: str, input_data: dict) -> dict:
        if task != "generate_proposal":
            return self._error_response(f"Task '{task}' not supported.")

        job_description = (input_data.get("job_description") or "").strip()
        job_title = (input_data.get("job_title") or "Client Project").strip()
        technical_doubts = input_data.get("technical_doubts") or []
        freelancer_context = self._build_freelancer_context(input_data)

        if not job_description:
            return self._error_response("Missing required input: job_description.")

        proposal_content = self._generate_proposal(
            job_title=job_title,
            job_description=job_description,
            freelancer_context=freelancer_context,
            technical_doubts=technical_doubts,
        )

        response = self._format_response(
            "success",
            {
                "type": "text",
                "content": proposal_content,
            },
        )
        return self.validate_response(response)

    def _build_freelancer_context(self, input_data):
        explicit_context = (input_data.get("freelancer_context") or "").strip()
        context_parts = []
        for path in (self.portfolio_path, self.resume_path):
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    context_parts.append(handle.read().strip())
            except FileNotFoundError:
                continue
        if explicit_context:
            context_parts.append(explicit_context)
        return "\n\n".join(part for part in context_parts if part)

    def _generate_proposal(self, job_title, job_description, freelancer_context, technical_doubts):
        if self.llm:
            prompt = self._build_prompt(
                job_title=job_title,
                job_description=job_description,
                freelancer_context=freelancer_context,
                technical_doubts=technical_doubts,
            )
            response = self.llm.invoke(prompt)
            return getattr(response, "content", str(response)).strip()

        context_snapshot = self._summarize_context(freelancer_context)
        alignment_block = self._format_alignment_block(technical_doubts)
        scoped_summary = self._summarize_job(job_description)

        return (
            f"Proposal for {job_title}\n\n"
            f"Why I fit\n{context_snapshot}\n\n"
            f"Understanding of the work\n{scoped_summary}\n\n"
            f"Alignment questions\n{alignment_block}\n\n"
            "Execution plan\n"
            "Day 1: confirm scope, architecture boundaries, and delivery sequence.\n"
            "Day 2: implement the critical path, integrate dependencies, and surface risks early.\n"
            "Day 3: validate the result, harden quality, and deliver a clean handoff.\n\n"
            "Close\n"
            "I optimize for a reliable first milestone, fast feedback loops, and architecture that can grow without rework."
        )

    def _build_prompt(self, job_title, job_description, freelancer_context, technical_doubts):
        alignment_block = self._format_alignment_block(technical_doubts)
        return (
            f"You are ProposalEngine for freelance-os.\n"
            f"Job title: {job_title}\n"
            f"Job description:\n{job_description}\n\n"
            f"Freelancer context:\n{freelancer_context}\n\n"
            f"Client alignment questions:\n{alignment_block}\n\n"
            "Write a concise, high-conviction freelance proposal with these sections:\n"
            "1. Why I fit\n"
            "2. Understanding of the work\n"
            "3. Execution plan\n"
            "4. Close\n"
            "Do not invent credentials beyond the provided context."
        )

    def _format_alignment_block(self, technical_doubts):
        if not technical_doubts:
            return "- Confirm business success criteria.\n- Confirm technical constraints.\n- Confirm delivery milestones."
        return "\n".join(f"- {question}" for question in technical_doubts)

    def _summarize_context(self, freelancer_context):
        lines = [line.strip("- ").strip() for line in freelancer_context.splitlines() if line.strip()]
        if not lines:
            return "AI-native engineer with delivery rigor across mobile, backend, and applied automation."
        chosen_lines = []
        for line in lines:
            if line.startswith("#"):
                continue
            chosen_lines.append(line)
            if len(chosen_lines) == 3:
                break
        return " ".join(chosen_lines) if chosen_lines else lines[0]

    def _summarize_job(self, job_description):
        sentences = [segment.strip() for segment in job_description.replace("\n", " ").split(".") if segment.strip()]
        if not sentences:
            return "The scope needs to be clarified before implementation starts."
        return ". ".join(sentences[:2]) + "."

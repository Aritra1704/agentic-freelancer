from agents.proposal_engine import ProposalEngine


def test_proposal_engine_uses_explicit_freelancer_context():
    engine = ProposalEngine(llm=None)

    response = engine.execute(
        "generate_proposal",
        {
            "job_title": "AI Workflow Build",
            "job_description": "Build an agent pipeline with a dashboard and API integration.",
            "freelancer_context": "Senior engineer with AI-native delivery discipline.",
            "technical_doubts": [
                "Which systems are the source of truth?",
                "What are the non-functional performance expectations?",
                "Who owns the downstream API contracts?",
            ],
        },
    )

    assert response["status"] == "success"
    assert response["artifact"]["type"] == "text"
    assert "Proposal for AI Workflow Build" in response["artifact"]["content"]
    assert "Senior engineer with AI-native delivery discipline." in response["artifact"]["content"]


def test_proposal_engine_rejects_missing_job_description():
    engine = ProposalEngine(llm=None)

    response = engine.execute("generate_proposal", {"job_title": "Missing scope"})

    assert response["status"] == "error"
    assert "job_description" in response["artifact"]["message"]

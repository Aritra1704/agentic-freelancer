from agents.pricing_predictor import PricingPredictor


def test_pricing_predictor_estimates_complexity_and_price():
    predictor = PricingPredictor()

    response = predictor.execute(
        "estimate_price",
        {
            "job_description": (
                "Build a RAG agent with real-time dashboard updates, API integrations, "
                "security requirements, and scalable architecture."
            ),
            "budget": "$4,500",
            "technical_doubts": [
                "What are the document retention constraints?",
                "Which vector store is preferred?",
                "What latency target must the assistant meet?",
            ],
            "suggested_stack": ["Python", "Postgres", "LangChain"],
        },
    )

    estimate = response["artifact"]["content"]

    assert response["status"] == "success"
    assert estimate["complexity_band"] in {"high", "very_high"}
    assert estimate["recommended_price"] > 0
    assert estimate["budget_reference"] == 4500.0
    assert "signals" in estimate["rationale"]


def test_pricing_predictor_rejects_missing_job_description():
    predictor = PricingPredictor()

    response = predictor.execute("estimate_price", {"budget": 1000})

    assert response["status"] == "error"
    assert "job_description" in response["artifact"]["message"]

from agents.lead_processor import LeadProcessor, RefinementValidationError


def test_validate_technical_doubts_requires_three_distinct_questions():
    processor = LeadProcessor.__new__(LeadProcessor)

    questions = processor._validate_technical_doubts(
        {
            "technical_doubts": [
                "What is the deployment target and hosting boundary?",
                "Which external APIs are already available to integrate against?",
                "How will success be measured for the first milestone?",
                "What is the deployment target and hosting boundary?",
            ]
        }
    )

    assert len(questions) == 3
    assert questions[0] == "What is the deployment target and hosting boundary?"


def test_validate_technical_doubts_rejects_missing_or_thin_payload():
    processor = LeadProcessor.__new__(LeadProcessor)

    try:
        processor._validate_technical_doubts({"technical_doubts": ["Too short?", "Small?", "Tiny?"]})
    except RefinementValidationError as exc:
        assert "at least 3 distinct" in str(exc)
    else:
        raise AssertionError("Expected invalid technical_doubts payload to be rejected.")

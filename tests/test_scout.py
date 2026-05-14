# freelance-os/tests/test_scout.py
import json
import os

def mock_job_data():
    """Returns a list of mock job entries for testing."""
    return [
        {"title": "Python Developer for AI Agent", "budget": "$1000", "description": "Need an expert in Gemini and MCP."},
        {"title": "WordPress Site Setup", "budget": "$50", "description": "Just install a theme."},
        {"title": "LLM Integration Specialist", "budget": "$2500", "description": "Build a RAG pipeline using LangChain."}
    ]

def filter_ai_jobs(jobs):
    ai_keywords = ['ai', 'llm', 'agent', 'gpt']
    return [job for job in jobs if any(keyword.lower() in job['title'].lower() for keyword in ai_keywords)]

def test_filter_ai_jobs():
    """
    Test: Verify that jobs containing AI-related keywords are identified.
    Success Condition: Returns 2 out of the 3 mock jobs.
    """
    jobs = mock_job_data()
    filtered = filter_ai_jobs(jobs)
    
    # We expect 'AI Agent' and 'LLM Integration' to be caught
    assert len(filtered) == 2
    assert any("AI Agent" in job["title"] for job in filtered)
    assert any("LLM" in job["title"] for job in filtered)

if __name__ == "__main__":
    # Allow running directly for quick verification
    try:
        test_filter_ai_jobs()
        print("Test Passed!")
    except AssertionError:
        print("Test Failed (as expected for Red-Green-Refactor)!")

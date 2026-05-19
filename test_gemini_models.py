import os

import pytest
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


pytestmark = pytest.mark.skipif(
    os.getenv("RUN_LIVE_GEMINI_TESTS") != "1" or not os.getenv("GOOGLE_API_KEY"),
    reason="Live Gemini checks are disabled unless RUN_LIVE_GEMINI_TESTS=1 and GOOGLE_API_KEY is set.",
)


@pytest.mark.parametrize(
    "name",
    [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
    ],
)
def test_model(name):
    llm = ChatGoogleGenerativeAI(model=name)
    response = llm.invoke("Hi")
    assert response.content

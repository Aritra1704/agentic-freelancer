import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def test_model(name):
    print(f"Testing model: {name}...")
    try:
        llm = ChatGoogleGenerativeAI(model=name)
        response = llm.invoke("Hi")
        print(f"✅ {name} works!")
        return True
    except Exception as e:
        print(f"❌ {name} failed: {e}")
        return False

models_to_test = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite"
]

for model in models_to_test:
    test_model(model)

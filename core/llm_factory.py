# freelance-os/core/llm_factory.py
import os
from langchain_google_genai import ChatGoogleGenerativeAI

class BrowserUseLLM:
    """
    A wrapper to make LangChain models compatible with browser-use.
    """
    def __init__(self, llm):
        self.llm = llm
        self.provider = "google" # browser-use specific requirement
        self.model_name = getattr(llm, "model", "gemini-1.5-flash") # browser-use requirement

    def __getattr__(self, name):
        # Delegate everything else to the original llm
        return getattr(self.llm, name)
    
    async def ainvoke(self, *args, **kwargs):
        return await self.llm.ainvoke(*args, **kwargs)

    def invoke(self, *args, **kwargs):
        return self.llm.invoke(*args, **kwargs)

class LLMFactory:
    """
    Factory to switch between Gemini Pro, Flash, and Ollama.
    """
    @staticmethod
    def get_model_instance(tier="flash"):
        models = {
            "pro": "gemini-1.5-pro",
            "flash": "gemini-1.5-flash",
        }
        model_name = models.get(tier, "gemini-1.5-flash")
        llm = ChatGoogleGenerativeAI(model=model_name)
        
        # Wrap the llm for browser-use compatibility
        return BrowserUseLLM(llm)

    @staticmethod
    def get_model(tier="flash"):
        models = {
            "pro": "gemini-1.5-pro",
            "flash": "gemini-1.5-flash",
            "local": "llama3"
        }
        return models.get(tier, "gemini-1.5-flash")

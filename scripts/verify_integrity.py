# freelance-os/scripts/verify_integrity.py
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

def test_imports():
    print("🧪 Testing Imports...")
    try:
        from browser_use import Agent, Browser
        from browser_use.browser.session import BrowserSession
        from browser_use.browser.profile import BrowserProfile
        print("✅ browser_use imports verified.")
    except ImportError as e:
        print(f"❌ browser_use import failed: {e}")
        return False

    try:
        from core.llm_factory import LLMFactory
        from core.ollama_bridge import OllamaBridge
        print("✅ core module imports verified.")
    except ImportError as e:
        print(f"❌ core module import failed: {e}")
        return False
    
    return True

def test_file_structure():
    print("🧪 Testing File Structure...")
    required_files = [
        "main.py",
        "agents/scout_agent.py",
        "agents/strategist_agent.py",
        "core/llm_factory.py",
        "context/portfolio.md"
    ]
    for f in required_files:
        if os.path.exists(f):
            print(f"✅ Found: {f}")
        else:
            print(f"❌ Missing: {f}")
            return False
    return True

if __name__ == "__main__":
    if test_imports() and test_file_structure():
        print("\n🚀 INTEGRITY VERIFIED: Project is safe to run.")
        sys.exit(0)
    else:
        print("\n❌ INTEGRITY FAILED: Do not run.")
        sys.exit(1)

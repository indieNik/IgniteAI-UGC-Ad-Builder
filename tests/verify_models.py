import os
import sys
from dotenv import load_dotenv

# Ensure project root is in path
sys.path.append(os.getcwd())
load_dotenv()

from execution.llm_factory import generate_content_json
from execution.media_factory import MediaFactory

def test_llm():
    print("Testing LLM Factory (LiteLLM)...")
    try:
        response = generate_content_json(
            system_prompt="You are a helpful assistant.",
            user_prompt="Output a JSON with key 'status' and value 'ok'"
        )
        print(f"LLM Response: {response}")
        if response.get("status") == "ok":
            print("✅ LLM Test Passed")
        else:
            print("❌ LLM Test Failed: Unexpected content")
    except Exception as e:
        print(f"❌ LLM Test Failed with Exception: {e}")

def test_media_factory_mock():
    print("\nTesting Media Factory (Mock/Config check)...")
    # We won't actually burn credits for video gen here, but we can try to inspect the provider.
    try:
        provider = MediaFactory.get_provider("gemini")
        print(f"✅ Provider loaded: {type(provider)}")
    except Exception as e:
        print(f"❌ Media Factory Provider Load Failed: {e}")

if __name__ == "__main__":
    test_llm()
    test_media_factory_mock()

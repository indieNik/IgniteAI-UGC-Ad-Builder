import os
import json
from dotenv import load_dotenv
from execution.llm_factory import generate_content_json

# Load env vars
load_dotenv()

# Force provider to gemini for this test
os.environ["LLM_PROVIDER"] = "gemini"

def test_gemini():
    print("--- Testing Gemini Integration (Standalone) ---")
    
    system_prompt = "You are a helpful AI assistant. Output JSON."
    user_prompt = "Explain how AI works in a simple sentence. Return JSON with key 'explanation'."
    
    try:
        print(f"Sending request to Gemini (Model: gemini-3-pro-preview)...")
        result = generate_content_json(system_prompt, user_prompt)
        print("\n--- Result Received ---")
        print(json.dumps(result, indent=2))
        print("\nGemini Test PASSED.")
    except Exception as e:
        print(f"\nGemini Test FAILED: {e}")
        # Print instructions if it's an API key issue
        if "API_KEY" in str(e) or "403" in str(e):
             print("Check your GEMINI_API_KEY in .env")

if __name__ == "__main__":
    test_gemini()

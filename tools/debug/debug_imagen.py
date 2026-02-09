import os
from dotenv import load_dotenv

# Conditional import
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai not installed")
    exit(1)

load_dotenv()

def debug_imagen():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    client = genai.Client(api_key=api_key)
    print(f"Client initialized.")
    
    try:
        print("Listing available models...")
        for m in client.models.list():
            # Just print the model object or name
            print(f"Model: {m.name}")
            if "imagen" in m.name.lower():
                print(f"*** FOUND IMAGEN: {m.name} ***")
                
    except Exception as e:
        print(f"ListModels failed: {e}")


if __name__ == "__main__":
    debug_imagen()

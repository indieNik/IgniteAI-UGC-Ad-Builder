import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

def list_genai_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("--- Listing Models ---")
    try:
        pager = client.models.list()
        for model in pager:
            # Print available attributes
            print(f"Model Name: {model.name}")
            print(f"Display Name: {model.display_name}")
            # Try to print everything to find capability info
            # print(model) 
            print("-" * 20)
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_genai_models()

import os
from google import genai
from dotenv import load_dotenv
load_dotenv()

try:
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    print("Function signature for generate_videos:")
    print(help(client.models.generate_videos))
except Exception as e:
    print(e)

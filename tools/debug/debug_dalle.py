import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt = "SCENE ACTION: Character holding the product bottle and smiling at the camera. CHARACTER: Athletic young adult fitness enthusiast, Long, wavy brown hair tied in a ponytail, wearing Bright athletic wear. PRODUCT: High Energy Fitness Drink. STYLE: Bright natural daylight. Photorealistic."

try:
    print(f"Testing Prompt: {prompt}")
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1792", 
        quality="standard",
        n=1,
    )
    print("Success URL:", response.data[0].url)
except Exception as e:
    print("FAILED:", e)

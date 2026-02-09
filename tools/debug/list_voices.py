import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
client = ElevenLabs(api_key=api_key)

try:
    response = client.voices.get_all()
    # Handle the response based on its type
    if hasattr(response, 'voices'):
        voices = response.voices
    else:
        # If it's a list or other iterable
        voices = response

    print("--- Available Voices ---")
    for voice in voices:
        print(f"Name: {voice.name}, ID: {voice.voice_id}, Category: {voice.category}")
except Exception as e:
    print(f"Error fetching voices: {e}")

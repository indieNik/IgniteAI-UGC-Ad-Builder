import os
import uuid
from typing import Dict, Any, Optional
from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv

# Integration
from execution import llm_factory

load_dotenv()

MUSIC_DIR = "tmp" # Use temp for generated assets
os.makedirs(MUSIC_DIR, exist_ok=True)

def generate_bgm_track(visual_dna: Dict[str, Any], output_dir: str = "tmp", config: Dict[str, Any] = {}) -> Optional[str]:
    """
    Generates a unique BGM track using ElevenLabs Sound Effects API based on 'vibe'.
    Returns absolute path to mp3 or None.
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("ElevenLabs API Key missing. Skipping BGM.")
        return None
        
    client = ElevenLabs(api_key=api_key)
    
    print("--- AI Composer: Generating Original Score ---")
    
    # Priority: Config Custom Prompt > Brand Music Style > Config Mood > Visual DNA
    brand = config.get("brand", {})
    brand_music_style = brand.get("music_style")
    config_mood = config.get("music_mood") or config.get("mood")
    custom_prompt = config.get("custom_music_prompt") or brand_music_style

    
    char_vibe = config_mood if config_mood else visual_dna.get("character", {}).get("vibe", "Neutral")
    style_desc = visual_dna.get("visual_style", {}).get("lighting", "")
    
    music_prompt = ""
    
    if custom_prompt:
        # Direct Override
        print(f"Using Custom Music Prompt: '{custom_prompt}'")
        music_prompt = custom_prompt
    else:
        # predefined mappings for stability
        vibe_map = {
            "energetic": "Upbeat electronic pop background music, high energy, positive vibe, suitable for ads",
            "relaxed": "Chill lo-fi hip hop beat, relaxing, background music, soft piano",
            "professional": "Corporate ambient background music, inspiring, minimal, tech vibe",
            "dark": "Cinematic dark ambient, suspenseful, deep bass, movie trailer style"
        }
        
        # Check for key match
        for key, val in vibe_map.items():
            if key in char_vibe.lower():
                music_prompt = val
                print(f"Mapped Vibe '{char_vibe}' to Pre-defined Prompt.")
                break
        
        # Fallback to LLM if no mapping or custom prompt
        if not music_prompt:
            # 1. LLM Music Prompting
            system_prompt = f"""
            You are a Music Supervisor. Write a text-to-audio prompt for a background track.
            Ad Vibe: "{char_vibe}"
            Visual Style: "{style_desc}"
            
            CRITICAL: The prompt must be descriptive of instruments and mood. 
            Examples: 
            - "A relaxing acoustic guitar melody with soft piano"
            - "Upbeat lofi hip hop beat with jazzy chords"
            - "Cinematic ambient drone with swelling strings"
            
            Output JSON: {{ "music_prompt": "Your prompt here" }}
            """
            
            try:
                response = llm_factory.generate_content_json(system_prompt, "Write music prompt.")
                music_prompt = response.get("music_prompt", "Upbeat background music")
            except Exception as e:
                print(f"LLM Prompting failed: {e}. Using default.")
                music_prompt = "Upbeat pop background music"

    print(f"Composing: '{music_prompt}'")
    
    try:
        # 2. Call ElevenLabs
        # We use text_sound_effects as a proxy for music generation if music model not explicitly available
        # Max duration usually constrained, but 15-20s is enough for a loop.
        audio_gen = client.text_to_sound_effects.convert(
            text=f"{music_prompt} [Loopable] [Instrumental]", # Enforce instrumental loop structure
            duration_seconds=22, # Generate a slightly longer loopable chunk
            prompt_influence=0.5
        )
        
        os.makedirs(output_dir, exist_ok=True)
        filename = f"bgm_{uuid.uuid4()}.mp3"
        path = os.path.join(output_dir, filename)
        
        with open(path, "wb") as f:
            for chunk in audio_gen:
                f.write(chunk)
                
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            print(f"BGM Generated: {path}")
            return path
        else:
            print("Generated BGM file was empty/small.")
            return None
            
    except Exception as e:
        print(f"Music Generation failed: {e}")
        return None

# Alias for compatibility if imported as select_bgm_track
select_bgm_track = generate_bgm_track

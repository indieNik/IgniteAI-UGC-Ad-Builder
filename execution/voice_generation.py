import os
import time
import uuid
import json
import random
from typing import Tuple, List, Dict, Any, Optional
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

# Integration imports
from execution import llm_factory

# MoviePy for audio detection
try:
    from moviepy import VideoFileClip
except ImportError:
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        VideoFileClip = None

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    print("WARNING: ELEVENLABS_API_KEY not found in environment.")

try:
    client = ElevenLabs(api_key=api_key)
except Exception as e:
    print(f"Failed to initialize ElevenLabs client: {e}")
    client = None

# Voice Registry
VOICE_REGISTRY = {
    "Adam": {"id": "pNInz6obpgDQGcFmaJgB", "gender": "Male", "desc": "Deep, Narration, authoritative, American"},
    "Sarah": {"id": "EXAVITQu4vr4xnSDxMaL", "gender": "Female", "desc": "Calm, Storytelling, soothing, American"},
    "Charlie": {"id": "IKne3meq5aSn9XLyUdCD", "gender": "Male", "desc": "Deep, Confident, Energetic, American"},
    "Domi": {"id": "AZnzlk1XvdvUeBnXmlld", "gender": "Female", "desc": "Strong, Fashion, confident, North American"},
    "Liam": {"id": "TX3LPaxmHKxFdv7VOQHJ", "gender": "Male", "desc": "High energy, gamer, fast-paced, American"},
    "Bella": {"id": "EXAVITQu4vr4xnSDxMaL", "gender": "Female", "desc": "Soft, emotional, whisper, American (Mapped to Sarah)"},
    "Arnold": {"id": "VR6AewGX3RexUbFz31zN", "gender": "Male", "desc": "Detailed, explanatory, calm, American"},
    "Clyde": {"id": "2EiwWnXFnvU5JabPnv8n", "gender": "Male", "desc": "Deep, smooth, radio, American"},
    "Mimi": {"id": "zrHiDhphv9ZnVXBqCLjz", "gender": "Female", "desc": "Child-like, playful, younger, Australian/Neutral"},
    "Fin": {"id": "TX3LPaxmHKxFdv7VOQHJ", "gender": "Male", "desc": "High energy, gamer, fast-paced, Irish/Neutral (Mapped to Liam)"},
    "Aarav": {"id": "pNInz6obpgDQGcFmaJgB", "gender": "Male", "desc": "Deep, Indian Accent, Hindi/Kannada fluent, Professional (Mapped to Adam)"},
    "Ananya": {"id": "EXAVITQu4vr4xnSDxMaL", "gender": "Female", "desc": "Soft, Indian Accent, Hindi/Kannada fluent, Storytelling (Mapped to Sarah)"},
    "Default": {"id": "JBFqnCBsd6RMkjVDRZzb", "gender": "Male", "desc": "Standard"}
}

def _check_video_has_audio(scene_paths):
    """Check if video clips have native audio embedded."""
    if not scene_paths or not VideoFileClip:
        return False
    for p in scene_paths:
        if not os.path.exists(p):
            continue
        try:
            clip = VideoFileClip(p)
            if clip.audio is not None:
                clip.close()
                return True
            clip.close()
        except:
            pass
    return False

def _select_voice_agent(script_text, visual_dna):
    """
    Dynamic voice selection based on persona and script tone.
    Improvement: Use LLM to map character persona → voice ID.
    """
    try:
        character = visual_dna.get("character", {})
        char_desc = character.get("description", "")
        char_vibe = character.get("vibe", "")
        
        # Simple keyword→voice mapping
        tone_keywords = {
            "confident": "Domi",
            "energetic": "Liam",
            "calm": "Sarah",
            "fun": "Liam",
            "serious": "Adam",
            "professional": "Arnold",
            "warm": "Sarah",
            "exciting": "Charlie"
        }
        
        # Match
        for kw, voice_name in tone_keywords.items():
            if kw in char_desc.lower() or kw in char_vibe.lower():
                return VOICE_REGISTRY[voice_name]["id"]
        
        # Fallback: Gender-based
        if character.get("gender", "").lower() == "male":
            return VOICE_REGISTRY["Adam"]["id"]
        else:
            return VOICE_REGISTRY["Sarah"]["id"]
    
    except Exception as e:
        print(f"Casting Agent Failed: {e}. Using Default.")
        return VOICE_REGISTRY["Default"]["id"]

def _sanitize_script_text(script_text: str) -> str:
    """
    Clean script text using Voice Generator skill.
    Preserves expressive audio tags for eleven_v3 model.
    """
    from skills.voice_generator.agent import VoiceGenerator
    
    voice_gen = VoiceGenerator(api_key=api_key) if api_key else None
    
    if voice_gen:
        # Use skill's clean_script with preserve_expressive_tags=True
        # This keeps [happy], [sad], [whispers], [pause] etc. for v3 expressive control
        clean_text = voice_gen.clean_script(script_text, preserve_expressive_tags=True)
    else:
        # Fallback to basic cleaning if skill unavailable
        import re
        clean_text = re.sub(r'\(\s*\d+\s*(s|seconds?)\s*\)', '', script_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\([^)]*[a-zA-Z]{4,}[^)]*\)', '', clean_text)
        clean_text = clean_text.replace('*', '')
    
    print(f"--- Cleaned Script for Voiceover: '{clean_text[:50]}...' ---")
    
    # Safety Check: If script is empty after cleaning, return empty to skip VO
    if not clean_text or not clean_text.strip():
        print("Warning: Cleaned script is empty. Skipping voiceover.")
        return ""
    
    return clean_text


def generate_voiceover_elevenlabs(script_text: str, scene_paths: List[str] = [], visual_dna: Dict[str, Any] = {}, output_dir: str = "tmp") -> Tuple[str, float]:
    """
    Generates voiceover from text using ElevenLabs.
    Dynamic: checks for video audio first, and selects voice based on context.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Check for existing audio (e.g. Veo)
    if _check_video_has_audio(scene_paths):
        print("Native audio detected. SKIPPING Voiceover generation to avoid clashing.")
        print("Note: In a full production, we would insert Background Music here.")
        # Return a mock audio path or generic BGM if we had it.
        # For now, return None/Empty to signal Assembly not to overwrite.
        # But Assembly expects a path. Let's return a silent track or empty string?
        # Workflow expects a tuple.
        # Let's create a silent fallback or just return a distinct flag.
        # For this prototype, we'll return an empty string path, and update Assembly to handle it.
        return "", 0.0

    # 2. Sanitize Script Text
    clean_text = _sanitize_script_text(script_text)
    if not clean_text: # If _sanitize_script_text returned an empty string, skip VO
        return "", 0.0
    
    # 3. Dynamic Casting
    voice_id = _select_voice_agent(clean_text, visual_dna)
    
    print(f"--- Generating Voice using ElevenLabs (ID: {voice_id})... ---")
    
    output_filename = f"voiceover_{uuid.uuid4()}.mp3"
    output_path = os.path.join(output_dir, output_filename)
    
    if not client:
        print("⚠️ ElevenLabs client not initialized. Skipping voiceover.")
        return "", 0.0
    
    try:
        # returns a generator of bytes
        audio_generator = client.text_to_speech.convert(
            text=clean_text,
            voice_id=voice_id,
            model_id="eleven_v3"  # Updated for expressive audio tags support
        )
        
        with open(output_path, "wb") as f:
            for chunk in audio_generator:
                f.write(chunk)
                
        # Calculate duration
        file_size = os.path.getsize(output_path)
        if file_size < 100:
             print(f"Warning: Generated audio file is remarkably small ({file_size} bytes).")

        # Estimate duration if we can't inspect easily
        word_count = len(clean_text.split())
        duration = max(2.0, word_count / 2.6)
        
        print(f"Voice Generation Succeeded. Saved to: {output_path}")
        return output_path, duration

    except Exception as e:
        print(f"⚠️ ElevenLabs Generation Failed: {e}")
        error_str = str(e).lower()
        if "quota" in error_str or "401" in error_str:
            print("   -> Quota Exceeded. Proceeding with SILENT/NO AUDIO mode.")
        else:
            print("   -> Unknown error. Proceeding without voiceover.")
            
        # Return empty path to signal downstream to skip audio
        return "", 0.0


# Backward compatibility wrapper
def generate_voice(script_text: str, scene_paths: List[str] = [], visual_dna: Dict[str, Any] = {}, output_dir: str = "tmp") -> Tuple[str, float]:
    """
    Wrapper for backward compatibility.
    Calls generate_voiceover_elevenlabs with new skills integration.
    """
    return generate_voiceover_elevenlabs(script_text, scene_paths, visual_dna, output_dir)


if __name__ == "__main__":
    # Test
    # Mocking scenes for logic check
    print("Test: Dynamic Voice")
    path, dur = generate_voice("Test script", [], {"character": {"description": "cool surfer dude", "vibe": "chill"}})
    print(f"{path}, {dur}s")

#!/usr/bin/env python3
"""
Skills Playground: Caption + Voice Integration Test

Demonstrates both Caption Generator and Voice Generator skills working together
to add perfectly synced voiceover and captions to a video.

Usage:
    python3 skills/skills-playground/test_caption_voice_sync.py
"""

import os
import sys
import subprocess

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Load environment variables from .env if available
env_path = os.path.join(project_root, ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from skills.voice_generator.agent import VoiceGenerator
from skills.caption_generator.agent import CaptionGenerator


def get_audio_duration(audio_path: str) -> float:
    """Get duration of audio file using ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True,
        text=True
    )
    return float(result.stdout.strip())


def overlay_audio_on_video(video_path: str, audio_path: str, output_path: str):
    """Overlay audio on video using FFmpeg."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",  # Copy video stream
        "-map", "0:v:0",  # Use video from first input
        "-map", "1:a:0",  # Use audio from second input
        "-shortest",  # End when shortest stream ends
        output_path
    ]
    
    print(f"🎵 Overlaying audio onto video...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed: {result.stderr}")
    
    print(f"✅ Audio overlaid: {output_path}")
    return output_path


def main():
    print("🎬 Caption + Voice Integration Test\n")
    print("=" * 60)
    
    # Configuration
    script_text = "[excited] Cafe? The Jaggery Point in Bangalore. Anytime! [laugh]"
    input_video = "skills/skills-playground/input_video.mp4"
    
    # Output paths
    playground_dir = "skills/skills-playground"
    voiceover_path = os.path.join(playground_dir, "voiceover.mp3")
    video_with_audio = os.path.join(playground_dir, "video_with_audio.mp4")
    final_output = os.path.join(playground_dir, "final_output.mp4")
    
    # Check input video exists
    if not os.path.exists(input_video):
        print(f"❌ Error: Input video not found: {input_video}")
        print(f"   Please place a video at: {input_video}")
        return 1
    
    print(f"📹 Input Video: {input_video}")
    print(f"📝 Script: '{script_text}'")
    print()
    
    # Step 1: Generate Voiceover
    print("🎙️  STEP 1: Generating Voiceover")
    print("-" * 60)
    
    voice_gen = VoiceGenerator()
    
    try:
        voiceover_path = voice_gen.generate_voice(
            script=script_text,
            output_path=voiceover_path,
            voice_name="monika",  # Calm, clear female
            stability=0.5,  # v3 requires: 0.0, 0.5, or 1.0
            similarity_boost=0.8
        )
        
        # Get voiceover duration
        vo_duration = get_audio_duration(voiceover_path)
        print(f"⏱️  Voiceover duration: {vo_duration:.2f}s")
        print()
        
    except Exception as e:
        print(f"❌ Voice generation failed: {e}")
        return 1
    
    # Step 2: Overlay Audio on Video
    print("🎵 STEP 2: Overlaying Audio on Video")
    print("-" * 60)
    
    try:
        overlay_audio_on_video(input_video, voiceover_path, video_with_audio)
        print()
    except Exception as e:
        print(f"❌ Audio overlay failed: {e}")
        return 1
    
    # Step 3: Add Captions
    print("📝 STEP 3: Adding Captions")
    print("-" * 60)
    
    caption_gen = CaptionGenerator()
    
    # Get cleaned text for captions (REMOVE expressive tags - they're voice-only!)
    # Voice script: "[excited] Cafe? The Jaggery Point..." (for TTS emotion)
    # Caption text: "Cafe? The Jaggery Point..." (clean display text)
    cleaned_text = voice_gen.clean_script(script_text, preserve_expressive_tags=False)
    print(f"Caption text: '{cleaned_text}'")
    
    try:
        final_output = caption_gen.burn_captions(
            video_path=video_with_audio,
            caption_text=cleaned_text,
            output_path=final_output,
            font_size=100,
            font_color="yellow",
            position="bottom",
            duration=vo_duration,  # Match voiceover duration
            chunk_words=2  # TikTok-style 2-word chunks
        )
        print()
        
    except Exception as e:
        print(f"❌ Caption burning failed: {e}")
        return 1
    
    # Success!
    print("=" * 60)
    print("✨ SUCCESS! All steps completed!")
    print()
    print(f"📹 Final Output: {final_output}")
    print()
    print("🎯 What was created:")
    print(f"   1. Voiceover: {voiceover_path}")
    print(f"   2. Video + Audio: {video_with_audio}")
    print(f"   3. Final (Audio + Captions): {final_output}")
    print()
    print("💡 Both skills worked together seamlessly!")
    
    return 0


if __name__ == "__main__":
    exit(main())

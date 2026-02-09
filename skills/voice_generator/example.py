#!/usr/bin/env python3
"""
Example usage of Voice Generator Skill
"""

import os
import sys

# Load ELEVENLABS_API_KEY from .env file
# DO NOT hardcode API keys in source code
# Set the environment variable: export ELEVENLABS_API_KEY='your_key_here'

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from skills.voice_generator.agent import VoiceGenerator


def example_basic_generation():
    """Example: Basic voice generation"""
    generator = VoiceGenerator()
    
    script = "Welcome to the best cafe in Bengaluru - The Jaggery Point!"
    
    audio_path = generator.generate_voice(
        script=script,
        voice_name="riley",
        output_path="example_basic.mp3"
    )
    
    print(f"✅ Basic voice: {audio_path}")


def example_with_cleaning():
    """Example: Script with stage directions (auto-cleaned)"""
    generator = VoiceGenerator()
    
    # This script has stage directions that will be auto-removed
    messy_script = """
    VOICEOVER (Excited): Bengaluru, are you ready? (3s)
    [Action: Pause for effect] *giggles*
    The best cafe in the world is here!
    """
    
    audio_path = generator.generate_voice(
        script=messy_script,
        voice_name="domi",
        output_path="example_cleaned.mp3"
    )
    
    print(f"✅ Cleaned voice: {audio_path}")


def example_male_voice():
    """Example: Male voice"""
    generator = VoiceGenerator()
    
    script = "Introducing the revolutionary coffee experience"
    
    audio_path = generator.generate_voice(
        script=script,
        voice_name="josh",  # Deep narrative male
        output_path="example_male.mp3"
    )
    
    print(f"✅ Male voice: {audio_path}")


def example_custom_settings():
    """Example: Custom voice settings"""
    generator = VoiceGenerator()
    
    script = "Limited time offer - visit today!"
    
    audio_path = generator.generate_voice(
        script=script,
        voice_name="bella",
        stability=1.0,  # v3 requires: 0.0, 0.5, or 1.0 (Robust)
        similarity_boost=0.9,  # Higher clarity
        style=0.3,  # Some style exaggeration
        output_path="example_custom.mp3"
    )
    
    print(f"✅ Custom settings voice: {audio_path}")


if __name__ == "__main__":
    print("🎙️  Voice Generator Examples\n")
    
    # Check for API key
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ Error: ELEVENLABS_API_KEY not set in environment")
        print("   Set it with: export ELEVENLABS_API_KEY='your_key'")
        sys.exit(1)
    
    # Run examples
    print("1. Basic generation...")
    example_basic_generation()
    
    print("\n2. With auto-cleaning...")
    example_with_cleaning()
    
    print("\n3. Male voice...")
    example_male_voice()
    
    print("\n4. Custom settings...")
    example_custom_settings()
    
    print("\n✨ All examples completed!")

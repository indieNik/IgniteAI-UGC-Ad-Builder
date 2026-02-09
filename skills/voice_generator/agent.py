#!/usr/bin/env python3
"""
Voice Generator Skill
======================

Standalone agent for generating voiceovers from text using ElevenLabs TTS.

Features:
- Clean script preprocessing (removes stage directions, timing markers)
- Multiple voice selection
- Optimized audio settings for video
- Chunk-based generation for long scripts

Usage:
    from skills.voice_generator.agent import VoiceGenerator
    
    generator = VoiceGenerator(api_key="your_api_key")
    audio_path = generator.generate_voice(
        script="Welcome to our cafe!",
        voice_id="21m00Tcm4TlvDq8ikWAM"  # Rachel
    )
"""

import os
import re
import requests
from typing import Optional, Dict, Any


class VoiceGenerator:
    """
    Standalone voice generator using ElevenLabs TTS API.
    """
    
    # Popular ElevenLabs voices
    VOICES = {
        "riley": "hA4zGnmTwX2NQiTRMt7o",  # Calm, clear female
        "monika": "EaBs7G1VibMrNAuz2Na7",  # Calm, clear female
        "rachel": "21m00Tcm4TlvDq8ikWAM",  # Calm, clear female
        "domi": "AZnzlk1XvdvUeBnXmlld",    # Strong, confident female
        "bella": "EXAVITQu4vr4xnSDxMaL",   # Soft, gentle female
        "antoni": "ErXwobaYiN019PkySvjV",  # Well-rounded male
        "josh": "TxGEqnHWrfWFTfGW9XjX",   # Deep, narrative male
        "arnold": "VR6AewLTigWG4xSOukaG",  # Crisp, authoritative male
    }
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize voice generator.
        
        Args:
            api_key: ElevenLabs API key (reads from env if not provided)
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY not found in environment or constructor")
        
        self.base_url = "https://api.elevenlabs.io/v1"
    
    def clean_script(self, script: str, preserve_expressive_tags: bool = True) -> str:
        """
        Clean script text for voiceover generation.
        
        Removes:
        - Duration markers: (3s), (5 seconds)
        - Stage directions: (Excited), (Narrator)
        - Asterisks: *giggles*
        
        Preserves (when preserve_expressive_tags=True):
        - Expressive tags: [sad], [angry], [laughs], [whispers], etc.
        - Pause tags: [pause], [short pause], [long pause]
        
        Args:
            script: Raw script text
            preserve_expressive_tags: Keep ElevenLabs v3 expressive tags (default: True)
        
        Returns:
            Cleaned script text
        """
        clean = script
        
        # Remove duration markers
        clean = re.sub(r'\(\s*\d+\s*(s|seconds?)\s*\)', '', clean, flags=re.IGNORECASE)
        
        # Remove parenthetical stage directions (but not expressive tags in square brackets)
        # This removes things like (Excited), (Narrator), etc.
        clean = re.sub(r'\([^)]*[a-zA-Z]{4,}[^)]*\)', '', clean)
        
        # Remove asterisks
        clean = clean.replace('*', '')
        
        # Optionally remove square bracket content (but preserve expressive tags)
        if not preserve_expressive_tags:
            clean = re.sub(r'\[.*?\]', '', clean)
        
        # Clean up extra whitespace
        clean = ' '.join(clean.split())
        
        return clean.strip()
    
    def generate_voice(
        self,
        script: str,
        output_path: Optional[str] = None,
        voice_id: Optional[str] = None,
        voice_name: Optional[str] = "monika",
        model: str = "eleven_v3",  # Updated to v3 for expressive audio tags
        stability: float = 0.5,
        similarity_boost: float = 0.75,
        style: float = 0.0,
        use_speaker_boost: bool = True
    ) -> str:
        """
        Generate voiceover audio from script.
        
        Supports expressive audio tags:
        - Emotions: [sad], [angry], [happy]
        - Actions: [whispers], [shouts], [laughs], [clears throat], [sighs]
        - Pauses: [pause], [short pause], [long pause]
        
        Args:
            script: Text to convert to speech (supports expressive tags)
            output_path: Path to save audio file (optional, auto-generated if None)
            voice_id: ElevenLabs voice ID (overrides voice_name if provided)
            voice_name: Voice name from VOICES dict (default: "monika")
            model: ElevenLabs model (default: "eleven_v3" for expressive control)
            stability: Voice stability - v3 ONLY allows: 0.0 (Creative), 0.5 (Natural), 1.0 (Robust)
            similarity_boost: Voice clarity 0-1 (default: 0.75)
            style: Style exaggeration 0-1 (default: 0.0)
            use_speaker_boost: Enable speaker boost (default: True)
        
        Returns:
            Path to generated audio file
        """
        # Clean script
        clean_script = self.clean_script(script)
        print(f"📝 Cleaned script: '{clean_script[:60]}...'")
        
        # Determine voice ID
        if voice_id is None:
            voice_id = self.VOICES.get(voice_name.lower(), self.VOICES["rachel"])
        
        # Generate output path if not provided
        if output_path is None:
            output_path = "voiceover.mp3"
        
        # Build API request
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": clean_script,
            "model_id": model,
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity_boost,
                "style": style,
                "use_speaker_boost": use_speaker_boost
            }
        }
        
        print(f"🎙️  Generating voice: {voice_name} ({voice_id[:8]}...)")
        
        # Make API call
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            raise RuntimeError(f"ElevenLabs API failed: {response.status_code} - {response.text}")
        
        # Save audio file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        file_size_kb = len(response.content) / 1024
        print(f"✅ Voice generated: {output_path} ({file_size_kb:.1f}KB)")
        
        return output_path
    
    def list_voices(self) -> Dict[str, Any]:
        """
        List available voices from ElevenLabs account.
        
        Returns:
            Dictionary of voice data
        """
        url = f"{self.base_url}/voices"
        headers = {"xi-api-key": self.api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch voices: {response.status_code}")
        
        return response.json()


if __name__ == "__main__":
    # Quick test
    print("Voice Generator Agent Ready!")
    print(f"Available voices: {', '.join(VoiceGenerator.VOICES.keys())}")
    print("Usage: generator.generate_voice(script, voice_name='rachel')")

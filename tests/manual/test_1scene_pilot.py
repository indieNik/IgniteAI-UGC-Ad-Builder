#!/usr/bin/env python3
"""
Pilot Test: 1-Scene Video with Skills Integration

Tests:
- Voice Generator with eleven_v3 + expressive tags
- Caption Generator with chunked captions
- End-to-end workflow integration

Run: python3 test_1scene_pilot.py
"""

import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Set environment for 1-scene test
os.environ["LLM_PROVIDER"] = "gemini"
os.environ["IMAGE_PROVIDER"] = "veo"  # Veo for video generation
os.environ["PRODUCT_DESCRIPTION"] = "The Jaggery Point cafe in Bangalore - pilot test"
os.environ["NUM_SCENES"] = "1"  # Override to 1 scene only

# Import after env setup
from execution import workflow

def main():
    print("=" * 70)
    print("🧪 PILOT TEST: 1-Scene Video with Skills Integration")
    print("=" * 70)
    print("\n📋 Test Configuration:")
    print("   • Scenes: 1 (pilot test)")
    print("   • Voice: ElevenLabs v3 with expressive tags")
    print("   • Captions: Chunked 2-word style")
    print("   • Provider: Gemini + Veo")
    print("\n" + "=" * 70)
    
    # Minimal config for testing
    config = {
        "product_description": "The Jaggery Point cafe in Bangalore - cozy ambiance",
        "platform": "Instagram Reels",
        "duration": 15,  # Short 15s video for 1 scene
        "geography": "Bangalore, India",
        "language": "English",
        "captions_enabled": True,
        "use_ffmpeg_captions": True,  # Use new Caption Generator skill
        "visual_dna": {
            "product_type": "cafe",
            "mood": "warm, inviting",
            "style": "authentic, cozy"
        }
    }
    
    print("\n🚀 Starting workflow...\n")
    
    try:
        # Run the workflow
        result = workflow.run_workflow(config)
        
        print("\n" + "=" * 70)
        print("✅ PILOT TEST COMPLETED!")
        print("=" * 70)
        print(f"\n📹 Output Video: {result.get('final_video_path', 'N/A')}")
        print(f"⏱️  Total Duration: {result.get('duration', 0):.2f}s")
        
        # Check if skills were used
        print("\n🔍 Skills Integration Check:")
        
        if result.get('voiceover_path'):
            print("   ✅ Voice Generator: Used (eleven_v3)")
        
        if result.get('captions_burned'):
            print("   ✅ Caption Generator: Used (chunked captions)")
        
        print(f"\n💰 Credits Charged: {result.get('credits_charged', 0)}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ PILOT TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

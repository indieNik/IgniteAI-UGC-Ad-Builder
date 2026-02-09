#!/usr/bin/env python3
"""
Quick caption overlay test script.
Overlays test captions on existing video to rapidly iterate on styling.

Usage:
    python tests/manual/test_caption_overlay.py
"""

import os
import sys

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from execution.ffmpeg_rendering import burn_subtitles_ffmpeg

def create_test_srt(output_path: str, text: str, duration: float = 10.0):
    """
    Create a simple SRT file with test caption.
    
    Args:
        output_path: Path to save SRT file
        text: Caption text to display
        duration: Duration of caption in seconds
    """
    # Split long text into multiple lines for better readability
    # FFmpeg will handle wrapping, but we can pre-format
    
    # SRT format:
    # 1
    # 00:00:00,000 --> 00:00:10,000
    # Caption text
    
    srt_content = f"""1
00:00:00,000 --> 00:00:{int(duration):02d},000
{text}
"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(srt_content)
    
    print(f"✅ SRT file created: {output_path}")
    return output_path


def main():
    # Configuration
    video_input = "/Users/publicissapient/Projects/AI-Projects/AI UGC Ad Video Builder/docs/guides/video.mp4"
    caption_text = "Bengaluru, here we come."
    
    # Output paths
    output_dir = os.path.join(project_root, "docs/guides")
    srt_path = os.path.join(output_dir, "test_caption.srt")
    video_output = os.path.join(output_dir, "captioned_test_output.mp4")
    
    # Verify input exists
    if not os.path.exists(video_input):
        print(f"❌ Error: Input video not found: {video_input}")
        return 1
    
    print("🎬 Caption Overlay Test")
    print(f"   Input: {os.path.basename(video_input)}")
    print(f"   Caption: '{caption_text}'")
    print()
    
    # Step 1: Create SRT file
    print("📝 Step 1: Creating SRT file...")
    create_test_srt(srt_path, caption_text, duration=39.0)  # Match video duration
    
    # Step 2: Burn captions using FFmpeg
    print("\n🔥 Step 2: Burning captions into video...")
    print("   Settings:")
    print("   - Font: Arial")
    print("   - Size: 100px")
    print("   - Color: Yellow")
    print("   - Position: bottom")
    print("   - BG Opacity: 55%")
    print()
    
    try:
        burn_subtitles_ffmpeg(
            video_path=video_input,
            srt_path=srt_path,
            output_path=video_output,
            font_name="Arial",
            font_size=100,  # Increased from 20 to 100 for visibility
            font_color="yellow",
            bg_opacity=0.55,
            position="bottom"
        )
        
        print(f"\n✅ SUCCESS!")
        print(f"📹 Output video: {video_output}")
        print(f"\n💡 Tip: Adjust font_size, position, or other params in this script and re-run to test different styles")
        
        # Cleanup
        if os.path.exists(srt_path):
            os.remove(srt_path)
            print(f"🗑️  Cleaned up SRT file")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error burning captions: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

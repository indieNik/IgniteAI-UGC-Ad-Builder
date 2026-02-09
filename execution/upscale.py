import os
import subprocess
from typing import Optional

def upscale_video_4k(input_path: str, output_path: str = None) -> Optional[str]:
    """
    Upscales a video to 4K (2160x3840 for vertical) using FFmpeg.
    Uses Lanczos resampling for decent quality without AI overhead.
    """
    if not os.path.exists(input_path):
        print(f"Upscale Input not found: {input_path}")
        return None
        
    if not output_path:
        output_path = input_path.replace(".mp4", "_4k.mp4")
        
    print(f"--- Upscaling to 4K: {input_path} -> {output_path} ---")
    
    # 9:16 4K = 2160x3840
    # ffmpeg -i input.mp4 -vf scale=2160:3840:flags=lanczos -c:v libx264 -preset slow -crf 18 output.mp4
    
    cmd = [
        "ffmpeg",
        "-y", # Overwrite
        "-i", input_path,
        "-vf", "scale=2160:3840:flags=lanczos",
        "-c:v", "libx264",
        "-preset", "medium", # Balance speed/compression
        "-crf", "20", # High quality
        "-c:a", "copy", # Copy audio without re-encoding
        output_path
    ]
    
    try:
        # Run ffmpeg (capture output to hide noise unless error)
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        if result.returncode != 0:
            print(f"FFmpeg Upscale Failed: {result.stderr}")
            return None
            
        print(f"4K Upscale Complete: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Upscaling execution failed: {e}")
        return None

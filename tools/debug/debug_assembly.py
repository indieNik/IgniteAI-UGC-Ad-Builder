import os
import sys
from moviepy import VideoFileClip

# Test file from previous ls output
test_file = ".tmp/scene_1_9285b790-f270-42f1-bc6a-a30df1ff4fb1.mp4"

print(f"Testing load of {test_file}")
print(f"File exists: {os.path.exists(test_file)}")
print(f"File size: {os.path.getsize(test_file)} bytes")

try:
    clip = VideoFileClip(test_file)
    print("SUCCESS: Clip loaded.")
    print(f"Duration: {clip.duration}")
    print(f"Size: {clip.size}")
    print(f"FPS: {clip.fps}")
    print(f"Audio: {clip.audio}")
    
    print("Testing subclip...")
    # Try the method used in assembly.py
    sub = clip.subclip(0, 2.0)
    print("SUCCESS: subclip(0, 2.0) worked.")
    print(f"Subclip duration: {sub.duration}")
    
    # Also check if with_duration exists instead?
    print(f"Has with_duration: {hasattr(clip, 'with_duration')}")

except Exception as e:
    print("FAILURE: Could not load clip.")
    print(f"Error type: {type(e)}")
    print(f"Error message: {e}")
    import traceback
    traceback.print_exc()

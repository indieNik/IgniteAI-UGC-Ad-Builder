import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_moviepy():
    print("\n--- Testing MoviePy ---")
    try:
        # UPDATED IMPORT FOR v2 often involves direct submodule or top level
        try:
             from moviepy.video.VideoClip import ImageClip 
             print("Imported ImageClip from moviepy.video.VideoClip")
        except ImportError:
             from moviepy.editor import ImageClip
             print("Imported ImageClip from moviepy.editor")
        
        # specific check for ffmpeg
        try:
             from moviepy.config import get_setting
             print(f"FFMPEG Binary: {get_setting('FFMPEG_BINARY')}")
        except:
             print("Could not check FFMPEG binary (API changed?)")

        # Create a dummy image to test with
        from PIL import Image
        img_path = "debug_test.png"
        img = Image.new('RGB', (100, 100), color = 'red')
        img.save(img_path)
        
        out_path = "debug_test.mp4"
        clip = ImageClip(img_path).with_duration(1.0) # v2 method is with_duration, v1 is set_duration. Try both via conditional if needed? 
        # Actually v2 uses with_duration, v1 set_duration. Let's try set_duration first as it's more common in transition docs, or check attribute.
        if hasattr(clip, 'with_duration'):
            clip = clip.with_duration(1.0)
        else:
            clip = clip.set_duration(1.0)
            
        clip.write_videofile(out_path, fps=24, codec='libx264')
        print(f"MoviePy Success. File size: {os.path.getsize(out_path)}")
        
        # cleanup
        os.remove(img_path)
        if os.path.exists(out_path): os.remove(out_path)
        
    except Exception as e:
        print(f"MoviePy Failed: {e}")
        import traceback
        traceback.print_exc()

def test_elevenlabs():
    print("\n--- Testing ElevenLabs ---")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    print(f"API Key present: {bool(api_key)}")
    
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=api_key)
        
        # Correct call for v1.0+
        audio = client.text_to_speech.convert(
            text="Test", 
            voice_id="JBFqnCBsd6RMkjVDRZzb", 
            model_id="eleven_monolingual_v1"
        )
        
        out_path = "debug_audio.mp3"
        with open(out_path, "wb") as f:
            for chunk in audio:
                f.write(chunk)
                
        print(f"ElevenLabs Success. File size: {os.path.getsize(out_path)}")
        os.remove(out_path)
    except Exception as e:
        print(f"ElevenLabs Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_moviepy()
    test_elevenlabs()

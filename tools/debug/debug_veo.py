import os
import time
from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai not installed")
    exit(1)

load_dotenv()

def debug_veo():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    client = genai.Client(api_key=api_key)
    print("Client initialized.")
    
    # We saw 'veo-2.0-generate-001' in the list. Let's try that.
    # Also saw 'veo-3.0-generate-001' in user request, let's check if it exists in the list again to be sure,
    # or just try it.
    
    prompt = "A cinematic drone shot of a futuristic city at sunset"
    
    # Check for correct method. 
    # Usually it's generate_videos or similar for Veo in v2 SDK.
    # Looking at the SDK structure, assume client.models.generate_videos exists.
    
    try:
        print("Listing available models to confirm Veo...")
        veo_model = None
        for m in client.models.list():
            if "veo" in m.name.lower() and "generate" in m.name.lower():
                print(f"Found Veo Model: {m.name}")
                if "2.0" in m.name:
                     veo_model = m.name # Fallback
                if "3.0" in m.name:
                     veo_model = m.name # Prefer 3.0
        
        if not veo_model:
             # Use the one from docs if verified in list
             veo_model = "gemini-2.5-flash-image" #"veo-3.1-generate-preview"
             
        print(f"Testing generation with model: {veo_model}")
        
        # Construct config
        # Expecting GenerateVideosConfig or similar.
        # Let's try to find the config type dynamically or guess.
        
        # In newer SDKs:
        # response = client.models.generate_videos(model=..., prompt=..., config=...)
        
        print("Attempting to call client.models.generate_videos...")
        
        # Note: If generate_videos doesn't exist, we'll catch AttributeError
        response = client.models.generate_videos(
            model=veo_model,
            prompt=prompt,
            config=types.GenerateVideosConfig(
                number_of_videos=1,
                aspect_ratio="16:9"
            )
        )
        
        print(f"Generation call returned operation: {response.name}")
        
        # Poll the operation status
        while not response.done:
            print("Waiting for video generation to complete (10s)...")
            time.sleep(10)
            response = client.operations.get(response)
            
        print("Operation complete.")
        
        # Check for errors in operation
        # The snippet uses operation.response.generated_videos
        if response.response and response.response.generated_videos:
            generated_video = response.response.generated_videos[0]
            print("Video generated. Downloading...")
            
            # Save file
            # The snippet uses client.files.download(file=...) to get bytes? No, snippet says:
            # client.files.download(file=generated_video.video) AND generated_video.video.save("...")
            # generated_video.video might be a File object or similar wrapper.
            # Let's try the snippet's save method first if it exists, or standard download.
            
            try:
                # Try simple save if the SDK supports it as shown in docs
                generated_video.video.save("veo_test.mp4")
                print("Saved veo_test.mp4 via save()")
            except:
                # Fallback to downloading bytes if save() isn't available on the object
                vid_content = client.files.download(file=generated_video.video)
                with open("veo_test.mp4", "wb") as f:
                    f.write(vid_content)
                print("Saved veo_test.mp4 via download()")
                
        else:
            print("No generated videos in response.")
            if response.error:
                print(f"Operation Error: {response.error}")
            
    except Exception as e:
        print(f"Veo Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_veo()

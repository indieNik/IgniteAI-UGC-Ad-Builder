
import os
import time
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Load env from root
load_dotenv("../../.env")
load_dotenv(".env")


VIDEO_MODEL_NAME = "sora-2" 
# Chai-themed T-Shirt Prompt
PROMPT = "A photorealistic, cinematic close-up in a warm, sunlit environment in Bengaluru. We see a steaming glass of masala chai being poured, the hot liquid swirling. As the steam rises, the focus smoothly racks to a person wearing a solid black t-shirt. The t-shirt features a vintage-style graphic with the text 'MOOD? JUST CHAI' stacked inside a yellow border, with a simple line drawing of a teacup. The lighting is soft and diffused, highlighting the texture of the fabric and the steam. The camera movement mimics handheld smartphone footage, creating an authentic, intimate social media vibe."
# Set this to a string ID to bypass creation and just poll, or None to create new
EXISTING_VIDEO_ID = None
# EXISTING_VIDEO_ID = "video_6950047c91488198a95a9e8beae85c0909deb6b8c4dfcd3e" 

IMAGE_PATH = "/Users/publicissapient/Projects/AI-Projects/AI UGC Ad Video Builder/brand/product.png"

def test_sora():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found.")
        return

    client = OpenAI(api_key=api_key)
    
    print(f"🚀 Initializing Sora Test (Schema v2)...")
    print(f"Target Endpoint: https://api.openai.com/v1/videos")
    print(f"Model: {VIDEO_MODEL_NAME}")
    
    # 1. Try SDK Method (if available in this environment's version)
    try:
        print("\n--- Attempt 1: SDK client.videos.create (Image-to-Video) ---")
        if hasattr(client, 'videos'):
            
            if EXISTING_VIDEO_ID:
                print(f"⏩ Using Existing Video ID: {EXISTING_VIDEO_ID} (Skipping Creation)")
                video_id = EXISTING_VIDEO_ID
            else:
                print("✨ Creating New Video with Image Reference...")
                
                # Check if image exists
                if not os.path.exists(IMAGE_PATH):
                    print(f"❌ Error: Image not found at {IMAGE_PATH}")
                    return

                # --- 1. Resize Logic (Sora Strict Requirement) ---
                print(f"📏 Resizing image to match target: 720x1280...")
                from PIL import Image
                resized_path = "temp_resized_sora.png"
                
                img = Image.open(IMAGE_PATH)
                img = img.resize((720, 1280), Image.Resampling.LANCZOS)
                img.save(resized_path)
                
                # --- 2. Call SDK ---
                with open(resized_path, "rb") as img_file:
                    video = client.videos.create(
                        model=VIDEO_MODEL_NAME,
                        prompt=PROMPT,
                        seconds="8", 
                        size="720x1280",
                        input_reference=img_file 
                    )
                
                print("✅ SDK Success!")
                print(f"Video ID: {video.id}")
                video_id = video.id
            
            # --- Polling Logic ---
            start_time = time.time()
            
            print(f"⏳ Polling status for Video {video_id}...")
            
            while True:
                # Retrieve latest status
                # Note: 'retrieve' might be 'client.videos.retrieve(video_id)' or 'client.videos.get(video_id)' 
                # or finding it in list. Standard OpenAI CRUD is usually .retrieve()
                try:
                    updated_video = client.videos.retrieve(video_id)
                except Exception as poll_err:
                    print(f"Polling warning: {poll_err}")
                    time.sleep(5)
                    continue
                
                status = updated_video.status
                elapsed = int(time.time() - start_time)
                
                print(f"[{elapsed}s] Status: {status}")
                
                if status == "completed":
                    print("\n🎉 Video Generation Complete!")
                    
                    print("⬇️ Downloading Content via SDK...")
                    try:
                        # Use User-Provided Method
                        response = client.videos.download_content(video_id=video_id)
                        print(f"Download Response: {response}")
                        
                        # Read content
                        # User snippet: content = response.read()
                        content = response.read()
                        print(f"Content Size: {len(content)} bytes")
                        
                        output_file = "sora_output.mp4"
                        with open(output_file, "wb") as f:
                            f.write(content)
                            
                        print(f"✅ Saved to {output_file}")
                        
                    except Exception as e:
                        print(f"❌ Download Failed: {e}")
                        # Fallback dump
                        try:
                             print(updated_video.model_dump())
                        except:
                             print(updated_video)

                    break
                elif status == "failed":
                    print(f"\n❌ Video Generation Failed: {updated_video.error}")
                    break
                
                time.sleep(10) # Wait 10s between checks
            
            return
        else:
            print("⚠️ SDK does not have 'videos' attribute. Skipping.")
    except Exception as e:
        print(f"❌ SDK Method Failed: {e}")

    # 2. Try Direct HTTP Request (Fallback)
    try:
        print("\n--- Attempt 2: Direct HTTP POST ---")
        url = "https://api.openai.com/v1/videos"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": VIDEO_MODEL_NAME,
            "prompt": PROMPT,
            "seconds": "8", 
            "size": "720x1280" # Error fix: Specific size required
        }
        
        resp = requests.post(url, json=data, headers=headers)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            print("✅ HTTP Success!")
            print(resp.json())
        else:
            print(f"❌ HTTP Failed: {resp.text}")
            
    except Exception as e:
        print(f"❌ HTTP Exception: {e}")

if __name__ == "__main__":
    test_sora()

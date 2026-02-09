import os
from dotenv import load_dotenv

# Conditional import
try:
    from google import genai
    from google.genai import types
except ImportError:
    print("google-genai not installed")
    exit(1)

load_dotenv()

def debug_imagen_failure():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # The prompt that failed
    prompt = "SCENE ACTION: POV shot looking down at the chest wearing the 'Spill The Chai' graphic tee. A hand brings a steaming ceramic mug into frame, steam swirling in golden hour sunlight.. CHARACTER: Gen Z female creator, approx 24 years old, relatable 'cozy girl' aesthetic, Dark wavy hair tied in a casual, loose messy bun, wearing The Chai-themed T-shirt (slightly oversized) paired with light-wash mom jeans or beige sweatpants. PRODUCT: 'Spill The Chai' Graphic Tee (Minimalist eco-friendly poly mailer with a branded sticker). STYLE: Warm natural window light (golden hour) creating a cozy atmosphere, Handheld POV looking down at the shirt while holding a steaming mug, transitioning to a full-body mirror selfie. STYLE: authentic iPhone footage, amateur UGC style, natural uneven lighting, social media quality. Hyper-realistic, 4k, vertical aspect ratio. IMPORTANT: NO CGI, NO ILLUSTRATION, NO CARTOON, NO 3D RENDER. Must look like a real photo taken by a person."
    
    print(f"Testing Imagen 4.0 with prompt length: {len(prompt)}")
    
    try:
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="9:16", 
                output_mime_type="image/png",
                # relax safety if possible? 
                # include_safety_attributes=True
            )
        )
        
        # print(f"Response Name: {response.name}") # Invalid
        print(f"Response Object: {response}")
        
        if response.generated_images:
            print(f"Success! Got {len(response.generated_images)} images.")
        else:
            print("FAILURE: No images returned.")
            # Check for safety reasons if available (not always in response object for images in v2)
            # Try printing specific attributes if possible
            try:
                print(f"Response dict: {response.to_dict()}")
            except:
                pass
            
    except Exception as e:
        print(f"API Call Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_imagen_failure()

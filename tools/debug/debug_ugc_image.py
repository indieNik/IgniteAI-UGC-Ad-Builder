import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import io

load_dotenv()

def test_user_snippet_no_config():
    """
    Tests the user's provided snippet for Multimodal Image Generation, without forcing response_mime_type.
    """
    print("--- Testing User Snippet (No Config) ---")
    
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    image_path = "brand/designs/image.png"
    if not os.path.exists(image_path):
        print("Image not found.")
        return

    print(f"Loading image: {image_path}")
    image = Image.open(image_path)
    
    prompt_text = "Create a photorealistic picture of a young influencer wearing this t-shirt in a cozy cafe."
    
    # Try models again
    models_to_test = ["gemini-2.5-flash-image"] 
    
    for model in models_to_test:
        print(f"\nTesting Model: {model}")
        try:
            # User snippet basically:
            # response = client.models.generate_content(model="...", contents=[prompt, image])
            
            response = client.models.generate_content(
                model=model,
                contents=[prompt_text, image],
                # No config
            )
            
            found_image = False
            if response.parts:
                for part in response.parts:
                    if part.text:
                         print(f"  [Text Output]: {part.text[:100]}...")
                    
                    if part.inline_data:
                        print("  [Image Output Found in Inline Data]")
                        try:
                             if hasattr(part, 'as_image'):
                                 img_out = part.as_image()
                             else:
                                 # Fallback manual decode
                                 from PIL import Image as PILImage
                                 img_out = PILImage.open(io.BytesIO(part.inline_data.data))
                                 
                             output_file = f"output/debug/gemini_gen_noconfig_{model}.png"
                             img_out.save(output_file)
                             print(f"  SUCCESS! Saved to {output_file}")
                             found_image = True
                        except Exception as img_e:
                             print(f"  Image save failed: {img_e}")
            
            if not found_image:
                print("  No image found in response parts. (Model likely returned text description)")
                
        except Exception as e:
            print(f"  Failed: {e}")

if __name__ == "__main__":
    test_user_snippet_no_config()

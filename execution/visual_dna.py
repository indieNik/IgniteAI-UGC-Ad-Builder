import os
import json
from typing import Dict, Any
from dotenv import load_dotenv
from execution.llm_factory import generate_content_json

load_dotenv()

def extract_visual_dna(input_data: str, image_path: str = None, config: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Extracts 'Visual DNA' from an input description and optionally a product image.
    Returns a structured dictionary defining the consistent attributes.
    """
    geography = config.get("geography", "Bengaluru, India")
    print(f"--- Extracting Visual DNA for: {input_data[:50]}... (Geo: {geography}) ---")
    if image_path:
        print(f"--- Analyzing Product Image: {image_path} ---")

    system_prompt = f"""
    You are an expert creative director for Hyper-Realistic UGC (User Generated Content) ads targeted at {geography}.
    Your goal is to extract a "Visual DNA" that feels authentic, amateur-but-aesthetic, and shot on an iPhone.
    The setting, casting, and vibe must reflect the local culture and aesthetics of {geography}.
    
    If a product image is provided:
    1. MATCH THE PRODUCT DETAILS EXACTLY: logo, text, colors, packaging.
    2. INVENT A PERSONA: If the image contains no person, YOU MUST HALLUCINATE a suitable UGC Creator in {geography} who would be selling this.
       - NEVER return "N/A" for character description.
       - Create a specific persona (e.g., "Energetic Gen-Z student", "Sophisticated minimalist", "Gym rat").
    
    Avoid "glossy TV commercial" vibes. We want "TikTok/Reels" vibes.
    
    You must output valid JSON with the following structure:
    {{
        "character": {{
            "description": "Short description of the creator/actor (MANDATORY: Do not use N/A)",
            "hair": "Hair color and style",
            "clothing": "Clothing style and color",
            "vibe": "Personality vibe (e.g., energetic, calm)"
        }},
        "product": {{
            "name": "Product name (infer from image if possible, or input)",
            "visual_description": "DETAILED VISUAL DESCRIPTION of the product itself. For clothing: describe print, text, graphics, color, fit. For packaged goods: describe bottle/box shape, label colors, text. THIS IS CRITICAL FOR RE-GENERATION.",
            "text_on_product": "Exact text visible on the product (e.g., brand name, slogan)",
            "liquid_color": "Color of liquid/contents if applicable"
        }},
        "visual_style": {{
            "lighting": "Lighting setup (e.g., golden hour, ring light)",
            "camera_angle": "Dynamic camera angle (e.g., eye-level, handheld selfie, low angle). AVOID 'flat lay' unless the product is stationery. Prefer 'Lifestyle' or 'In-Use' angles."
        }}
    }}
    
    Make reasonable assumptions if details are missing to ensure a complete and consistent visual profile.
    REMEMBER: The character field MUST be filled with a believable persona, even if invisible in the source image.
    """

    try:
        if image_path:
             # Multimodal via LiteLLM (Unified)
             import base64
             
             # Read image and encode to base64
             with open(image_path, "rb") as f:
                 image_bytes = f.read()
                 encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                 
             prompt_text = f"Extract Visual DNA from this input text: '{input_data}' and the attached product image.\n\n{system_prompt}"
             
             # Construct Multimodal Message (OpenAI Format - LiteLLM handles conversion)
             # Note: Gemini via LiteLLM expects 'url' to be data uri for base64
             user_content = [
                 {"type": "text", "text": prompt_text},
                 {
                     "type": "image_url",
                     "image_url": {"url": f"data:image/jpeg;base64,{encoded_string}"} 
                 }
             ]
             
             dna = generate_content_json(system_prompt, user_content, use_case="image")
            
        else:
            # Text Only
            user_prompt = f"Extract Visual DNA from this input: {input_data}"
            dna = generate_content_json(system_prompt, user_prompt, use_case="text")
        
        # Debug Gemini output
        print(f"DEBUG: DNA Type: {type(dna)}")
        if isinstance(dna, list):
            print("WARNING: DNA is a list, taking first element.")
            if len(dna) > 0:
                dna = dna[0]
            else:
                 dna = {}
        
        print("Visual DNA Extracted successfully.")
        return dna

    except Exception as e:
        print(f"Error extracting Visual DNA: {e}")
        # Import exception class
        from execution.exceptions import PipelineFailureException
        
        # DO NOT USE FALLBACK - Raise exception to trigger pipeline failure and refund
        raise PipelineFailureException(
            stage="visual_dna",
            reason=str(e),
            user_message="❌ Failed to analyze your product image. Your credits have been refunded. Please try again with a different image or contact support.",
            requires_refund=True
        )

if __name__ == "__main__":
    # Test run
    sample_input = "A high energy video for a neon green energy drink called ZAP."
    result = extract_visual_dna(sample_input)
    print(json.dumps(result, indent=2))

import os
import json
from execution.llm_factory import generate_content_json, generate_content_json_with_fallback
from typing import Dict, Any, List


def generate_script_and_shots(input_data: str, visual_dna: Dict[str, Any], config: Dict[str, Any] = {}) -> Dict[str, Any]:
    """
    Generates a voiceover script and shotlist based on config.
    """
    print(f"--- Generating Script & Shotlist for: '{input_data}' ---")
    
    style = visual_dna.get("visual_style", {})
    product = visual_dna.get("product", {})
    character = visual_dna.get("character", {})
    
    # Config Parse
    duration_str = config.get("target_duration", "15s")
    language = config.get("language", "English")
    platform = config.get("platform_style", "TikTok")
    geography = config.get("geography", "Bengaluru, India")
    
    # Dynamic Scene Calculation
    seconds = int(duration_str.replace("s", ""))
    min_scene_duration = 5.0
    num_scenes = max(3, int(seconds // min_scene_duration))
    
    # Adjust for very short videos (e.g. 10s) -> 3 scenes of ~3.3s (dangerous but necessary)
    if seconds < 15:
        num_scenes = 3
        
    avg_duration = seconds / num_scenes
    
    # Generate Scene Definitions
    scene_defs = []
    ids = ["Hook", "Feature", "Lifestyle", "Benefit", "SocialProof", "CTA"]
    
    current_ids = []
    if num_scenes == 3:
        current_ids = ["Hook", "Feature", "CTA"]
    elif num_scenes == 4:
        current_ids = ["Hook", "Feature", "Lifestyle", "CTA"]
    else:
        # 5+ scenes
        current_ids = ids[:num_scenes-1] + ["CTA"]
        
    # Distribute remainder
    import math
    base_dur = math.floor(seconds / num_scenes)
    remainder = seconds - (base_dur * num_scenes)
    
    json_structure_example = ""
    for i, sid in enumerate(current_ids):
        dur = base_dur
        if i < remainder:
             dur += 1
        scene_defs.append(f'{{ "id": "{sid}", "description": "...", "duration_seconds": {dur}.0, "scene_script": "..." }}')
        
    json_structure_str = ",\n            ".join(scene_defs)

    system_prompt = f"""
    You are an expert TV Commercial Director and Copywriter for {platform}.
    Your goal is to create a high-energy, engaging {duration_str} video ad in {language}.
    
    Output must be valid JSON with the following structure, using exactly these {num_scenes} scene IDs:
    {{
        "scenes": [
            {json_structure_str}
        ]
    }}
    
    IMPORTANT GUIDELINES:
    1. STORYTELLING: Write a cohesive micro-story.
    2. VISUAL CONTINUITY: Consistency is key.
    3. TIMING: The sum of "duration_seconds" for all scenes MUST equal {seconds} seconds.
    4. CONSTRAINT: Use exactly {num_scenes} scenes. Keep descriptions visual and punchy.
    5. LANGUAGE: Write strictly in {language}. Eg: if 'Kannada', mix Kannada and English naturally like it is spoken in {geography}.
    6. PLATFORM VIBE: Match the style of {platform} (e.g. fast cuts for TikTok, aesthetic for Insta).
    7. NO CLICHÉ GESTURES: Avoid overused social media gestures like winking, pointing at camera, peace signs, or exaggerated reactions. Keep actions natural and authentic.
    
    CRITICAL - NARRATION SCRIPT FORMAT:
    - The "scene_script" field contains ONLY the exact words the voiceover artist will speak
    - DO NOT include: "VOICEOVER:", "(Excited):", stage directions, sound effects, or parenthetical notes
    - DO NOT include: "(Fast-paced music)", "[Action]", or any non-spoken text
    - Write ONLY the direct narration text that will be heard by viewers
    - Example GOOD: "Bengaluru, are you ready for an escape? Discover your new happy place!"
    - Example BAD: "VOICEOVER (Excited): Bengaluru, are you ready for an escape? (Fast-paced music starts)"
    
    The "description" field is for visual stage directions. The "scene_script" is ONLY spoken words.
    """
    
    brand = config.get("brand", {})
    brand_name = brand.get("name")
    brand_colors = ", ".join(brand.get("colors", []))
    brand_char = brand.get("character_prompt")

    user_prompt = f"""
    Product: {product.get('name', 'Product')}
    Product Info: {input_data}
    Target Vibe: {style.get('lighting', 'Dynamic')}
    
    Brand Info:
    - Name: {brand_name or 'Not specified'}
    - Primary Colors: {brand_colors or 'Not specified'}
    
    Visual DNA:
    - Character: {brand_char or character.get('description', 'Model')}
    - Style: {style.get('camera_angle', 'Cinematic')}
    
    Create a 4-scene story arc.
    Vary the Visuals: Use a mix of Selfie-style, Mid-shots, and Close-ups. Do NOT use 'Flat Lay' for every scene.
    """

    
    try:
        data = generate_content_json_with_fallback(system_prompt, user_prompt, use_case="text")
        
        # Backward compatibility / Convenience: Construct full script text
        scenes = data.get("scenes", [])
        full_script_text = " ".join([s.get("scene_script", "") for s in scenes])
        
        print("Script Generation Successful.")
        print(f"Script: {full_script_text}")
        # Extract Metadata
        usage_metadata = data.get("_meta", {})
        
        return {
            "script": full_script_text,
            "scenes": scenes,
            "usage_metadata": usage_metadata
        }
        
    except Exception as e:
        print(f"Script Generation Failed: {e}")
        # Import exception class
        from execution.exceptions import PipelineFailureException
        
        # DO NOT USE GENERIC FALLBACK - Raise exception to trigger refund
        raise PipelineFailureException(
            stage="script_generation",
            reason=str(e),
            user_message="❌ Failed to generate video script. Your credits have been refunded. Please try again or contact support.",
            requires_refund=True
        )

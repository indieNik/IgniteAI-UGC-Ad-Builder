import time
import os
import uuid
import requests
import base64
from typing import Dict, Any, Optional
from dotenv import load_dotenv


# Conditional import for Google GenAI
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# Conditional import for moviepy
try:
    # MoviePy v2
    from moviepy import ImageClip, vfx
except ImportError:
    try:
        # MoviePy v1
        from moviepy.editor import ImageClip
        import moviepy.video.fx.all as vfx
    except ImportError:
        ImageClip = None
        vfx = None

from PIL import Image, ImageDraw, ImageFont

def _get_font(size: int):
    """Helper to find a usable font across different OS environments."""
    possible_fonts = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "Arial.ttf",
        "DejaVuSans.ttf"
    ]
    for p in possible_fonts:
        try:
            if os.path.exists(p) or "/" not in p: # Try path or just name
                return ImageFont.truetype(p, size)
        except:
            continue
    return ImageFont.load_default()

# Helper for Image Watermarking
def _apply_watermark(image_path: str, text: str = "IGNITE AI"):
    """Applies a text watermark to an image file in place."""
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGBA")
            
            # Setup Draw
            txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
            draw = ImageDraw.Draw(txt_layer)
            
            # Font (Standard or Default)
            font_size = int(img.width * 0.05) # 5% of width
            font = _get_font(font_size)
            
            # Text Size
            # v10: draw.textbbox, v<10: draw.textsize
            # We'll stick to a simple placement (Bottom Right)
            # Just approximate for safety or use text
            
            x = img.width - (len(text) * font_size * 0.6) - 20
            y = img.height - font_size - 20
            
            # Draw Text (White with alpha)
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 128)) # 50% opacity
            
            # Composite
            watermarked = Image.alpha_composite(img, txt_layer)
            watermarked = watermarked.convert("RGB") # Remove alpha for saving as JPG/PNG
            watermarked.save(image_path)
            print(f"Watermark applied to {image_path}")
            
    except Exception as e:
        print(f"Failed to apply image watermark: {e}")

try:
    from projects.backend.services.rate_limiter import rate_limiter
except ImportError:
    rate_limiter = None

load_dotenv()

def generate_prompt(scene_data: Dict[str, Any], visual_dna: Dict[str, Any], config: Dict[str, Any] = {}) -> str:
    """
    Constructs a highly detailed prompt by merging scene action with visual DNA.
    """
    description = scene_data.get('description', '')
    scene_id = scene_data.get('id', 'X')
    # 1. Prompt Engineering for Consistency
    # We construct a "Master Prompt" that is applied to every scene to enforce continuity.
    char_dna = visual_dna.get("character", {})
    prod_dna = visual_dna.get("product", {})
    style_dna = visual_dna.get("visual_style", {})
    
    # Brand DNA Injection
    brand = config.get("brand", {})
    brand_name = brand.get("name")
    brand_colors = ", ".join(brand.get("colors", []))
    brand_char = brand.get("character_prompt")

    geography = config.get("geography", "Bengaluru, India")

    char_desc = char_dna.get("description")
    if not char_desc or char_desc == "None":
        char_desc = brand.get("character_prompt", "A person")
        
    char_look = char_dna.get("clothing", "casual clothes")
    lighting = style_dna.get("lighting", "natural light")
    
    # "Anchor" the generation
    # We define the entities (Character, Product) but DO NOT force an interaction/action yet.
    # The SCENE ACTION from the script will dictate the composition.
    
    product_name = prod_dna.get('name', 'Product')
    product_desc = prod_dna.get('visual_description', '')
    
    # NARRATIVE CONTEXT
    scene_narrative = scene_data.get('scene_script', '')
    narrative_context = f"NARRATIVE CONTEXT: The narrator is saying: '{scene_narrative}'." if scene_narrative else ""

    # Constructed Prompt
    full_prompt = (
        f"SETTING: {geography}. "
        f"BRAND: {brand_name or 'N/A'}. COLORS: {brand_colors or 'Corporate'}. "
        f"CHARACTER CONTEXT: {brand_char or char_desc} (Only show if scene requires a person). "
        f"PRODUCT CONTEXT: {product_name}. Visuals: {product_desc}. "
        f"{narrative_context} "
        f"SCENE VISUALS: {description}. "
        f"LIGHTING: {config.get('lighting') or lighting}. "
        f"STYLE: Handheld smartphone footage. "
        f"STYLE: {config.get('style') or config.get('aesthetic') or style_dna.get('camera_angle', 'Cinematic')}. "
        "IMPORTANT: The 'SCENE VISUALS' instruction is the primary directive for composition. "
        "IMPORTANT: NO TEXT OVERLAYS. NO CAPTIONS. CLEAN VIDEO ONLY. "
        "IMPORTANT: NO CGI, NO ILLUSTRATION, NO CARTOON. Photorealistic social media video. "
        "IMPORTANT: If a person is present, they MUST match the 'CHARACTER CONTEXT' description above EXACTLY. "
        "IMPORTANT: MAINTAIN VISUAL CONSISTENCY. The character defined in 'CHARACTER CONTEXT' is the specific actor for this video. Do not change their gender, ethnicity, or appearance from that description."
        "IMPORTANT: Avoid cliché gestures (winking, pointing at camera, peace signs, thumbs up). Keep character actions natural and subtle."
    )
    
    # REGENERATION ALLOWANCE (Cumulative)
    # 1. Historical Modifications (Persisted)
    modifications = scene_data.get("modifications", [])
    if modifications:
        print(f"🔄 Applying {len(modifications)} historical modifications.")
        for i, mod in enumerate(modifications):
            full_prompt += f" REVISION {i+1}: {mod}. "

    # 2. Current Regeneration Override (Ephemeral if not yet persisted, but workflow persists it now)
    # We check if it's already in modifications to avoid double applying
    current_regen = config.get("regenerate_prompt")
    if current_regen and (not modifications or current_regen != modifications[-1]):
        print(f"🔄 Applying Current Regeneration Prompt: {current_regen}")
        full_prompt += f" IMPORTANT CHANGE REQUEST: {current_regen}. PRIORITIZE THIS INSTRUCTION ABOVE ALL OTHERS."

    return full_prompt


def generate_scene(scene_data: Dict[str, Any], visual_dna: Dict[str, Any], config: Dict[str, Any] = {}, output_dir: str = "tmp", product_image_path: str = None, previous_scene_image: str = None, skip_image_generation: bool = False) -> tuple[str, str, Dict[str, str], Dict[str, Any]]:
    """
    Generates a single video scene.
    1. Constructs prompt.
    2. Smartly decides to use Original Image vs Generated Image.
    3. Calls Image Gen (DALL-E 3 or Imagen) if needed.
    4. Creates a Dynamic Ken Burns video clip from the image OR generates video directly via Veo.
    
    Args:
        skip_image_generation: If True, skips image generation (used for regeneration - only regenerate video, not image)
    """
    scene_id = scene_data.get("id", "unknown")
    description = scene_data.get("description", "")
    
    print(f"--- Processing Scene {scene_id} ---")
    print(f"🎯 DEBUG: Scene Description = '{description[:150] if description else 'EMPTY'}'")
    print(f"🎯 DEBUG: Scene Script = '{scene_data.get('scene_script', 'N/A')[:250]}'")
    
    # Parse Config
    aspect_ratio_str = config.get("aspect_ratio", "9:16")
    target_duration = float(scene_data.get("duration_seconds", 5.0))
    gen_duration = target_duration
    print(f"Target Duration: {target_duration}s")

    
    # PRIORITIZE CONFIG > ENV
    image_provider = config.get("image_provider", os.getenv("IMAGE_PROVIDER", "gemini")).lower()
    print(f"Selected Image Provider: {image_provider}")
    
    # 1. Construct Prompt
    # Extract details
    try:
         full_prompt = generate_prompt(scene_data, visual_dna, config=config)
    except TypeError:
         # Fallback for safety if signature mismatch persists
         full_prompt = f"Scene {scene_data.get('id')}: {scene_data.get('description')}"
         
    print(f"Generated Prompt: {full_prompt}")
    
    os.makedirs(output_dir, exist_ok=True)
    base_image_path = os.path.join(output_dir, f"scene_{scene_id}_{uuid.uuid4()}.png")
    
    # FIDELITY STRATEGY: "Head-Trimming"
    use_original = False
    
    # Robust Path Check (Handle URLs and local paths)
    def _is_valid_resource(p):
        return p and (os.path.exists(p) or p.startswith("http"))

    if _is_valid_resource(product_image_path):

        # Determine scene type
        desc_lower = description.lower()
        human_keywords = ["person", "man", "woman", "guy", "girl", "boy", "student", "model", "influencer", "creator", "artist", "barista", "wearing", "wear", "holds", "holding", "uses", "using", "face", "selfie", "smiling", "walking", "talking"]
        has_human = any(k in desc_lower for k in human_keywords)
        
        # Standard Logic (No Reveal/Trim)
        print(f"✨ Feature: Using Original Product Image for Scene {scene_id} (Product Focus).")
        gen_duration = target_duration # No buffer
        
        # Prepend instruction to use image
        full_prompt = (f"Start with this provided image, then animate: {full_prompt}")

        if ("gemini" in image_provider or "veo" in image_provider):
             # Analyze Product Image & Generate New Image (Multimodal)
             try:
                  if has_human:
                      # Robust fallback for character description
                      char_desc = visual_dna.get('character', {}).get('description')
                      if not char_desc or char_desc == "None":
                          char_desc = config.get("brand", {}).get("character_prompt", "a person")
                          
                      intro = f"Using the product in the input image, create a photorealistic scene of {char_desc} using it. Context: "
                  else:
                      intro = f"Using the product in the input image, create a photorealistic scene. Context: "
                      
                  final_prompt = f"{intro} {full_prompt}"
    
                  # Use image_provider directly (frontend sends actual model name)
                  image_model = image_provider
                  print(f"✨ Generating New Image via {image_model} (Multimodal)... Prompt: {final_prompt[:150]}...")
                  
                  _generate_multimodal_image(
                      final_prompt, 
                      product_image_path, 
                      base_image_path, 
                      previous_image_path=previous_scene_image, 
                      model_name=image_model,
                      aspect_ratio=aspect_ratio_str,
                      config=config
                  )
                  
                  use_original = True
                  
             except Exception as e:
                 print(f"Warning: Multimodal Generation failed: {e}. Falling back to default Text-to-Image.")
                 use_original = False
        else:
             print(f"Skipping Multimodal Generation (User selected {image_provider}). Proceeding to standard generation.")
             use_original = False

    # 2. Media Generation
    # Import factory here to avoid circular dep if placed at top, or just laziness (better to move to top later)
    from execution.media_factory import MediaFactory
    
    # Check if Veo is selected (Direct Video)
    if "veo" in image_provider or "veo" in config.get("video_model", "").lower():
        video_path = base_image_path.replace(".png", ".mp4")
        
        # REGENERATION OPTIMIZATION: Skip image generation if flagged
        if skip_image_generation and previous_scene_image:
            print(f"🔄 REGENERATION MODE: Skipping image generation, reusing existing image from previous version")
            # Use the previous scene image as the base image
            # Download it if it's a remote URL
            if previous_scene_image.startswith("http"):
                import requests
                from io import BytesIO
                print(f"Downloading existing image: {previous_scene_image}")
                resp = requests.get(previous_scene_image, timeout=15)
                resp.raise_for_status()
                with open(base_image_path, 'wb') as f:
                    f.write(resp.content)
            else:
                # Copy local file
                import shutil
                shutil.copy(previous_scene_image, base_image_path)
            
            use_original = True
            print(f"✅ Reused existing image for regeneration: {base_image_path}")
        elif not use_original:
            print(f"Generating High-Fidelity Base Image for Scene {scene_id}...")
            # Unified Image Gen
            try:
                MediaFactory.generate_image(full_prompt, base_image_path, config)
            except Exception as e:
                print(f"Base Image Generation Failed: {e}")
                raise e
                  
        # Configurable Max Duration
        MAX_DURATION = float(config.get("veo_max_duration", 8.0))
        MIN_DURATION = 6.0 
        
        import math
        veo_request_duration = math.ceil(min(max(gen_duration, MIN_DURATION), MAX_DURATION))

        # Video Model Selection
        video_model = config.get("video_model", "veo-3.1-fast-generate-preview")

        print(f"Generating Video via Veo ({video_model})... Requested: {veo_request_duration}s")
        
        try:
             # Unified Video Gen
             # We pass local config updated with duration
             vid_config = config.copy()
             vid_config["duration"] = veo_request_duration
             
             _, actual_dur, actual_model = MediaFactory.generate_video(
                 full_prompt, 
                 video_path, 
                 image_path=base_image_path, 
                 config=vid_config
             )
             
             print(f"Scene {scene_id} Video Generated. File: {video_path}")
             
             # Upload Veo Assets
             remote_assets = {}
             if os.path.exists(base_image_path):
                 url = _upload_asset(base_image_path, run_id=scene_data.get("run_id_ref"))
                 if url: remote_assets[f"{scene_id}_image"] = url
             if os.path.exists(video_path):
                 url = _upload_asset(video_path, run_id=scene_data.get("run_id_ref"))
                 if url: remote_assets[f"{scene_id}_video"] = url
                 
             usage_stats = {
                 "video_model": actual_model,
                 "video_duration": int(actual_dur),
                 "image_model": config.get("image_model") if not use_original else None 
             }
             return video_path, base_image_path, remote_assets, usage_stats
             
        except Exception as e:
             from execution.exceptions import QuotaExceededException
             
             # Check if this is a quota error - skip retries if so
             if isinstance(e, QuotaExceededException):
                 print(f"❌ Daily Quota Exceeded: {e}")
                 print("⚡ Skipping backup model retry. Falling back to Ken Burns immediately.")
                 # Continue to Ken Burns block below
             else:
                 print(f"MediaFactory Video Generation Failed: {e}")
                 
                 # Backup Model Retry Logic (only for non-quota errors)
                 backup_model = config.get("backup_video_model")
                 if backup_model and backup_model != video_model:
                      print(f"⚠️ Retrying with Backup Video Model: {backup_model}...")
                      try:
                           vid_config = config.copy()
                           vid_config["duration"] = veo_request_duration
                           # Force override of video_model in config
                           vid_config["video_model"] = backup_model
                           
                           _, actual_dur, actual_model = MediaFactory.generate_video(
                               full_prompt, 
                               video_path, 
                               image_path=base_image_path, 
                               config=vid_config
                           )
                           print(f"Scene {scene_id} Video Generated via Backup ({backup_model}).")
                           
                           # Upload Veo Assets (Backup)
                           remote_assets = {}
                           if os.path.exists(base_image_path):
                               url = _upload_asset(base_image_path, run_id=scene_data.get("run_id_ref"))
                               if url: remote_assets[f"{scene_id}_image"] = url
                           if os.path.exists(video_path):
                               url = _upload_asset(video_path, run_id=scene_data.get("run_id_ref"))
                               if url: remote_assets[f"{scene_id}_video"] = url
                               
                            # Return Stats (Backup)
                           usage_stats = {
                               "video_model": actual_model,
                               "video_duration": int(actual_dur),
                               "image_model": config.get("image_model") if not use_original else None
                           }
                           return video_path, base_image_path, remote_assets, usage_stats
                      except Exception as e2:
                           print(f"Backup MediaFactory Gen also failed: {e2}")
                           print("⚠️ Falling back to Ken Burns effect on base image.")
                 else:
                      print("Veo failed and no backup model configured/different from primary. Falling back to Ken Burns effect.")
             # Continue to Ken Burns block below...


    # Standard Image Path (if not Veo Video or if Veo failed)
    if not os.path.exists(base_image_path):
        print(f"Generating Base Image for Ken Burns...")
        MediaFactory.generate_image(full_prompt, base_image_path, config)
        
    print(f"Image saved to: {base_image_path}")
    
    # 3. Video Generation (Ken Burns Effect)
    # PERFORMANCE OPTIMIZATION: Use FFmpeg for 5-10x faster rendering
    print(f"Creating Dynamic Video Clip (Ken Burns) for Scene {scene_id}...")
    video_path = base_image_path.replace(".png", ".mp4")
    
    # Check if FFmpeg rendering is enabled (feature flag)
    use_ffmpeg = config.get("use_ffmpeg_rendering", True)  # Default: enabled
    ffmpeg_success = False
    
    if use_ffmpeg:
        try:
            from execution.ffmpeg_rendering import render_ken_burns_ffmpeg, check_ffmpeg_available
            
            if check_ffmpeg_available():
                print("🚀 Using FFmpeg for Ken Burns (5-10x faster)")
                render_ken_burns_ffmpeg(
                    image_path=base_image_path,
                    output_path=video_path,
                    duration=gen_duration,
                    zoom_start=1.0,
                    zoom_end=1.1,  # 10% zoom (matches MoviePy intent but safer)
                    width=1080,
                    height=1920,
                    fps=24,
                    pan_direction="none"
                )
                print(f"✅ FFmpeg Ken Burns complete: {video_path}")
                ffmpeg_success = True
            else:
                print("⚠️  FFmpeg not available, falling back to MoviePy")
        except Exception as e:
            print(f"⚠️  FFmpeg rendering failed: {e}")
            print("Falling back to MoviePy")
    
    # Fallback to MoviePy if FFmpeg is disabled or failed
    if not ffmpeg_success and ImageClip:
        try:
            # ASPECT RATIO FIX: Create clip at native 9:16 resolution
            TARGET_WIDTH = 1080
            TARGET_HEIGHT = 1920
            
            # Create a clip with dynamic duration
            clip = ImageClip(base_image_path)
            if hasattr(clip, 'with_duration'):
                clip = clip.with_duration(gen_duration)
            else:
                clip = clip.set_duration(gen_duration)

            # Normalize to 9:16 before applying Ken Burns effect
            original_w, original_h = clip.size
            print(f"Ken Burns: Source image is {original_w}x{original_h}")
            
            # Scale to fill 9:16 frame, then crop
            scale_factor = max(TARGET_WIDTH / original_w, TARGET_HEIGHT / original_h)
            scaled_w = int(original_w * scale_factor)
            scaled_h = int(original_h * scale_factor)
            
            print(f"Ken Burns: Scaling to {scaled_w}x{scaled_h} to fill 9:16 frame")
            
            if hasattr(clip, 'resized'):
                clip_resized = clip.resized((scaled_w, scaled_h))
            else:
                clip_resized = clip.resize((scaled_w, scaled_h))
            
            # Center crop to exact 9:16 dimensions
            print(f"Ken Burns: Cropping to {TARGET_WIDTH}x{TARGET_HEIGHT}")
            if hasattr(clip_resized, 'cropped'):
                clip_916 = clip_resized.cropped(
                    x_center=scaled_w/2,
                    y_center=scaled_h/2,
                    width=TARGET_WIDTH,
                    height=TARGET_HEIGHT
                )
            else:
                clip_916 = clip_resized.crop(
                    width=TARGET_WIDTH,
                    height=TARGET_HEIGHT,
                    x_center=scaled_w/2,
                    y_center=scaled_h/2
                )

            # Apply Ken Burns Effect (Slow Zoom In) on the 9:16 clip
            # 1. Resize/Zoom (dynamic scaling over time)
            try:
                # MoviePy v2 approach
                clip_zoomed = clip_916.with_effects([vfx.Resize(lambda t: 1 + 0.04 * t)])
            except:
                # MoviePy v1 style
                clip_zoomed = clip_916.resize(lambda t: 1 + 0.04 * t)

            # 2. Crop back to maintain 9:16 dimensions during zoom
            try:
                clip_final = clip_zoomed.with_effects([vfx.Crop(width=TARGET_WIDTH, height=TARGET_HEIGHT, x_center=TARGET_WIDTH/2, y_center=TARGET_HEIGHT/2)])
            except:
                clip_final = clip_zoomed.crop(width=TARGET_WIDTH, height=TARGET_HEIGHT, x_center=TARGET_WIDTH/2, y_center=TARGET_HEIGHT/2)

            print(f"✅ Writing Ken Burns video at {TARGET_WIDTH}x{TARGET_HEIGHT} (9:16)")
            clip_final.write_videofile(video_path, fps=24, codec='libx264', logger=None)
            
        except Exception as e:
            print(f"MoviePy creation failed: {e}")
            raise e
    elif not ffmpeg_success:
        # Only raise error if FFmpeg was NOT successful
        print("MoviePy not available (ImageClip is None).")
        raise ImportError("MoviePy ImageClip not available")

    # If we reach here, either FFmpeg succeeded or MoviePy succeeded
    # Skip to upload and stats section
    print(f"Scene {scene_id} Complete. File: {video_path}")
    
    remote_assets = {}
    if os.path.exists(base_image_path):
        url = _upload_asset(base_image_path, run_id=scene_data.get("run_id_ref"))
        if url: remote_assets[f"{scene_id}_image"] = url
        
    if os.path.exists(video_path):
        url = _upload_asset(video_path, run_id=scene_data.get("run_id_ref"))
        if url: remote_assets[f"{scene_id}_video"] = url

    usage_stats = {
        "video_model": "ken-burns",  # Fixed typo: "kenn-burns" → "ken-burns"
        "video_duration": 0,
        "image_model": config.get("image_model")
    }
    return video_path, base_image_path, remote_assets, usage_stats








def _load_image_robust(path: str):
    """Loads an image from a local path or a remote URL."""
    from PIL import Image
    import requests
    from io import BytesIO
    
    if path.startswith("http"):
        print(f"Downloading reference image from: {path}")
        resp = requests.get(path, timeout=15)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content))
    else:
        return Image.open(path)

def _generate_multimodal_image(prompt: str, reference_image_path: str, output_path: str, previous_image_path: str = None, model_name: str = "gemini-2.5-flash-image", aspect_ratio: str = "9:16", config: Dict[str, Any] = {}):

    """
    Uses Gemini 2.5 Flash Image to generate a new image based on a prompt and reference image.
    If previous_image_path is provided, it is included to enforce character consistency.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    reference_image = _load_image_robust(reference_image_path)
    
    contents = [prompt, reference_image]
    
    # Add consistency image if available
    if previous_image_path and (os.path.exists(previous_image_path) or previous_image_path.startswith("http")):
        print(f"Using previous scene image for consistency: {previous_image_path}")
        prev_image = _load_image_robust(previous_image_path)
        contents.append(prev_image)

        # Update prompt to reference it
        contents[0] = prompt + " IMPORTANT: The last image provided is the PREVIOUS SCENE. The character in the new generated image MUST LOOK EXACTLY like the character in that previous image (Same face, hair, body type). The first image provided is the PRODUCT REFERENCE."

    # Enforce Aspect Ratio via Prompt (Gemini Flash respects this)
    # 9:16 -> Vertical (1080x1920)
    # 16:9 -> Landscape (1920x1080)
    # 1:1 -> Square (1024x1024)
    
    ar_instruction = "vertical 9:16 aspect ratio"
    if aspect_ratio == "16:9":
        ar_instruction = "landscape 16:9 aspect ratio"
    elif aspect_ratio == "1:1":
        ar_instruction = "square 1:1 aspect ratio"
        
    if isinstance(contents[0], str):
        contents[0] += f" IMPORTANT: Generate a {ar_instruction} image."

    # Model: gemini-2.5-flash-image
    print(f"Calling Gemini 2.5-Flash-Image with prompt: {prompt[:200]}...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=contents
        )
        
        if response.parts:
            for part in response.parts:
                if part.inline_data:
                    # Decode and save
                    try:
                         if hasattr(part, 'as_image'):
                             img_out = part.as_image()
                         else:
                            import io
                            from PIL import Image as PILImage
                            img_out = PILImage.open(io.BytesIO(part.inline_data.data))
                            
                         img_out.save(output_path)
                         print(f"Multimodal Image Saved to: {output_path}")

                         # Apply Watermark
                         if config and config.get("watermark_enabled", True):
                             _apply_watermark(output_path, text=config.get("watermark_text", "IGNITE AI"))

                         return output_path, model_name
                    except Exception as e:
                        print(f"Failed to save image part: {e}")
                        raise e
        
        print("No image found in Gemini response parts.")
        raise ValueError("No image found in Gemini 2.5 response.")
        
    except Exception as e:
        print(f"Gemini 2.5 Generation Failed: {e}")
        raise e

def _upload_asset(local_path: str, run_id: str = None) -> Optional[str]:
    """Helper to upload asset to Firebase Storage immediately."""
    try:
        # Dynamic import to avoid circular dependency issues at toplevel
        from projects.backend.services.storage_service import storage_service
        
        # Determine destination
        # local: tmp/run_123/file.mp4 -> runs/run_123/file.mp4
        normalized = local_path.replace("\\", "/")
        if "tmp/" in normalized:
            parts = normalized.split("tmp/")
            relative_path = parts[-1]
            # Ensure no leading slash
            if relative_path.startswith("/"): relative_path = relative_path[1:]
            destination = f"runs/{relative_path}"
        elif run_id:
            # Fallback if path doesn't contain tmp (unlikely)
            filename = os.path.basename(local_path)
            destination = f"runs/{run_id}/{filename}"
        else:
             # Last resort
             destination = f"runs/misc/{os.path.basename(local_path)}"

        url = storage_service.upload_file(local_path, destination)
        print(f"☁️ Uploaded: {destination}")
        return url
    except Exception as e:
        print(f"⚠️ Upload Skipped: {e}")
        return None

def generate_end_card(product_image_path: str, cta_text: str, website: str, output_path: str, visual_dna: Dict[str, Any] = {}, config: Dict[str, Any] = {}):
    """
    Generates a static End Card image by:
    1. Using Generative AI to create a high-quality "Hero Shot" of the product.
    2. Overlaying clean CTA text and Website.
    3. Falls back to gradient background if product image is unavailable.
    """
    print(f"Generating End Card to {output_path}...")
    remote_url = None
    
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        
        # Check if product image exists
        product_image_exists = product_image_path and os.path.exists(product_image_path)
        
        # 1. Generate Aesthetic Background/Hero Shot
        print("Generating refreshing hero shot for End Card...")
        
        prod_desc = visual_dna.get("product", {}).get("visual_description", "product")
        
        bg = None
        
        if product_image_exists:
            # Prompt for a clean, refreshing look
            end_card_prompt = (
                f"Professional product photography of {prod_desc}. "
                "Placed centrally on a clean, aesthetic, refreshing surface (e.g., wooden table, marble, or pastel background). "
                "Soft, cinematic lighting. "
                "Composition must leave some negative space at the bottom for text. "
                "High resolution, 4k, photorealistic, advertising quality."
            )
            
            # Use existing multimodal function to generate this image
            # We reuse the output_path first to save the generated image
            try:
                _generate_multimodal_image(end_card_prompt, product_image_path, output_path, config=config)
                # Now output_path contains the generated hero shot
                bg = Image.open(output_path).convert("RGBA")
            except Exception as e:
                print(f"End Card Gen failed: {e}. Falling back to blurred original.")
                try:
                    img = Image.open(product_image_path).convert("RGBA")
                    bg = img.resize((1080, 1920), Image.Resampling.LANCZOS)
                    bg = bg.filter(ImageFilter.GaussianBlur(20))
                except Exception as img_err:
                    print(f"Failed to load product image for blur: {img_err}. Using gradient background.")
                    bg = None
        else:
            print("Product image not found. Using professional gradient background.")
        
        # Final fallback: Create professional gradient background
        if bg is None:
            print("Creating gradient background for end card...")
            target_size = (1080, 1920)
            
            # Create a beautiful gradient (dark blue to purple)
            bg = Image.new('RGBA', target_size, (0, 0, 0, 255))
            draw_grad = ImageDraw.Draw(bg)
            
            # Gradient from top to bottom
            for y in range(target_size[1]):
                # Interpolate between two colors
                ratio = y / target_size[1]
                # Dark blue (20, 30, 60) to deep purple (60, 20, 80)
                r = int(20 + (60 - 20) * ratio)
                g = int(30 + (20 - 30) * ratio)
                b = int(60 + (80 - 60) * ratio)
                draw_grad.rectangle([(0, y), (target_size[0], y + 1)], fill=(r, g, b, 255))
            
            bg = bg.convert("RGBA")
             
        # Ensure BG is 1080x1920 (Vertical Video)
        target_size = (1080, 1920)
        if bg.size != target_size:
            # Resize/Crop to fill
            ratio = max(target_size[0] / bg.width, target_size[1] / bg.height)
            new_size = (int(bg.width * ratio), int(bg.height * ratio))
            bg = bg.resize(new_size, Image.Resampling.LANCZOS)
            left = (bg.width - target_size[0]) / 2
            top = (bg.height - target_size[1]) / 2
            bg = bg.crop((left, top, left + target_size[0], top + target_size[1]))

        # 2. Add Subtle Dark Gradient for Text Readability at Bottom
        # Instead of full overlay, just gradient at bottom
        overlay = Image.new('RGBA', target_size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        
        # Simple gradient simulation: semi-transparent box at bottom
        draw_overlay.rectangle([(0, 1300), (1080, 1920)], fill=(0, 0, 0, 150))
        
        bg = Image.alpha_composite(bg, overlay)
        
        # Fonts
        font_cta = _get_font(90)
        font_url = _get_font(65)
        
        # 3. Add Text
        draw = ImageDraw.Draw(bg)
            
        # Draw CTA (Shop Now / Get Parsley ...)
        if not cta_text: cta_text = "Shop Now. Link in Bio!"
        
        # Centered Text Logic
        def draw_centered(text, y, font, fill):
             length = draw.textlength(text, font=font)
             x = (target_size[0] - length) // 2
             draw.text((x, y), text, font=font, fill=fill)
             
        draw_centered(cta_text, 1500, font_cta, "white")
        draw_centered(website, 1650, font_url, "#FFD700") # Gold color
        
        # 4. Brand Logo Overlay
        brand = config.get("brand", {})
        logo_url = brand.get("logo_url")
        if logo_url:
            print(f"Overlaying Brand Logo from {logo_url}")
            try:
                import requests
                from io import BytesIO
                resp = requests.get(logo_url, timeout=10)
                if resp.status_code == 200:
                    logo_img = Image.open(BytesIO(resp.content)).convert("RGBA")
                    # Resize logo (e.g. max width 400px)
                    logo_ratio = 400 / logo_img.width
                    logo_size = (400, int(logo_img.height * logo_ratio))
                    logo_img = logo_img.resize(logo_size, Image.Resampling.LANCZOS)
                    
                    # Position at Top Center
                    lx = (target_size[0] - logo_img.width) // 2
                    ly = 200
                    bg.paste(logo_img, (lx, ly), logo_img)
            except Exception as le:
                print(f"Failed to overlay brand logo: {le}")

        bg = bg.convert("RGB")
        bg.save(output_path)

        print("End Card Generated.")
        
        # Upload
        url = _upload_asset(output_path)
        if url: remote_url = url
        
    except Exception as e:
        print(f"Failed to generate end card: {e}")
        # Fallback: copy original
        import shutil
        shutil.copy(product_image_path, output_path)
        
    return remote_url

def generate_character(visual_dna: Dict[str, Any], config: Dict[str, Any] = {}, output_dir: str = "tmp", product_image_path: str = None) -> str:
    """
    Generates the "Anchor" character image. 
    This image serves as the consistency reference for all subsequent parallel scenes.
    """
    print(f"--- Generating Anchor Character ---")
    
    char_dna = visual_dna.get("character", {})
    prod_dna = visual_dna.get("product", {})
    style_dna = visual_dna.get("visual_style", {})
    geography = config.get("geography", "Bengaluru, India")
    
    # Prompt Focus: Character Portrait with Product
    prompt = (
        f"A photorealistic portrait of a {char_dna.get('description', 'person')} in {geography}. "
        f"Holding/Showing {prod_dna.get('name', 'the product/service')}. "
        f"Visuals: {prod_dna.get('visual_description', '')}. "
        f"Attire: {char_dna.get('clothing', 'casual')}. "
        f"Vibe: {char_dna.get('vibe', 'friendly')}. "
        f"Lighting: {style_dna.get('lighting', 'natural')}. "
        f"Style: High-quality social media photography, 9:16 vertical ratio. "
        f"IMPORTANT: This is the reference character for the entire video. Make them look consistent, authentic, and clear."
    )
    
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"character_anchor_{uuid.uuid4()}.png")
    
    # 1. Image Generation (Multimodal if product image exists)
    if product_image_path and os.path.exists(product_image_path):
        print(f"Using Multimodal Gen for Character Anchor...")
        try:
             _generate_multimodal_image(
                 prompt, 
                 product_image_path, 
                 output_path, 
                 config=config,
                 aspect_ratio=config.get("aspect_ratio", "9:16")
             )
        except Exception as e:
            print(f"Multimodal Character Gen failed: {e}. Falling back to Text-to-Image.")
            from execution.media_factory import MediaFactory
            MediaFactory.generate_image(prompt, output_path, config)
    else:
        # Standard Text-to-Image
        from execution.media_factory import MediaFactory
        MediaFactory.generate_image(prompt, output_path, config)
        
    print(f"Anchor Character Saved: {output_path}")
    
    # Upload immediately for persistent reference
    url = _upload_asset(output_path, run_id=config.get("run_id"))
    return output_path, url

from PIL import Image, ImageEnhance
import os

def create_breathing_loader(source_path, dest_path):
    if not os.path.exists(source_path):
        print(f"Error: Source image {source_path} not found.")
        return

    # Open image
    img = Image.open(source_path).convert("RGBA")
    
    # Resize for loader (e.g. 128px is good for overlay)
    size = 128
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    frames = []
    durations = []
    
    # Create breathing animation (Pulse Brightness/Opacity)
    # 30 frames loop
    num_frames = 20
    
    for i in range(num_frames):
        # Calculate pulse factor (sine wave approximation)
        # 0 to 1 to 0
        import math
        # x goes from 0 to pi
        x = (i / num_frames) * math.pi
        factor = 1.0 + (math.sin(x) * 0.5) # 1.0 to 1.5 to 1.0
        
        # Apply brightness/glow simulation
        enhancer = ImageEnhance.Brightness(img)
        frame = enhancer.enhance(factor)
        
        # Optionally pulse alpha slightly for "ghosting" effect
        # But brightness is usually enough for neon
        
        frames.append(frame)
        durations.append(50) # 50ms per frame = 20fps roughly

    # Save as GIF
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    frames[0].save(
        dest_path,
        save_all=True,
        append_images=frames[1:],
        duration=50,
        loop=0,
        disposal=2,
        optimize=True
    )
    print(f"Created animated loader: {dest_path}")

# Source (Using the generated high-res logo)
generated_image_path = "/Users/publicissapient/.gemini/antigravity/brain/59122bc3-fac1-43df-beba-dcec6cae4bba/ignite_ai_logo_v2_1766655179042.png"

# Dest
dest_path = "projects/frontend/public/assets/loader.gif"

create_breathing_loader(generated_image_path, dest_path)

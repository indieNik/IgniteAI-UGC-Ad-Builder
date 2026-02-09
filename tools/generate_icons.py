from PIL import Image
import os

def process_icon(source_path, size, dest_path):
    # Open source
    if not os.path.exists(source_path):
        print(f"Error: Source image {source_path} not found.")
        return

    img = Image.open(source_path).convert("RGBA")
    
    # Resize with high quality
    img_resized = img.resize((size, size), Image.Resampling.LANCZOS)
    
    # Save
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    img_resized.save(dest_path)
    print(f"Created {dest_path}")

# Source Config
generated_image_path = "/Users/publicissapient/.gemini/antigravity/brain/59122bc3-fac1-43df-beba-dcec6cae4bba/ignite_ai_logo_v2_1766655179042.png"

# Dest Config
base_dir = "projects/frontend/src"
assets_dir = os.path.join(base_dir, "assets/icons")

# Files
process_icon(generated_image_path, 192, os.path.join(assets_dir, "icon-192x192.png"))
process_icon(generated_image_path, 512, os.path.join(assets_dir, "icon-512x512.png"))
process_icon(generated_image_path, 32, os.path.join(base_dir, "favicon.ico"))

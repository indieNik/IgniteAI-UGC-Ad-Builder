import os
import sys
import base64
from PIL import Image

sys.path.append(os.getcwd())

from execution.visual_dna import extract_visual_dna

def create_dummy_image(path):
    img = Image.new('RGB', (100, 100), color = 'red')
    img.save(path)
    return path

def test_multimodal_dna():
    print("Testing Multimodal Visual DNA Extraction...")
    
    # create dummy image
    img_path = "tmp/test_product.jpg"
    os.makedirs("tmp", exist_ok=True)
    create_dummy_image(img_path)
    
    input_text = "A spicy red salsa jar."
    
    try:
        dna = extract_visual_dna(input_text, image_path=img_path)
        print(f"✅ DNA Extracted: {dna}")
        
        # Validation
        if "product" in dna:
            print("✅ Product Key Found")
        else:
            print("❌ Product Key Missing")
            
    except Exception as e:
        print(f"❌ Multimodal Test Failed: {e}")
        
if __name__ == "__main__":
    test_multimodal_dna()

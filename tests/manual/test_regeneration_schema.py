import sys
import os

# Add project root to sys.path
sys.path.append(os.getcwd())

try:
    print("Testing Imports...")
    from projects.backend.schemas import RegenerateSceneRequest
    print("✅ RegenerateSceneRequest imported successfully.")
    
    from projects.backend.routers.generation import regenerate_scene
    print("✅ generation.py imported successfully.")
    
    from execution.scene_generation import generate_prompt
    print("✅ scene_generation.py imported successfully.")
    
    # Test generate_prompt with regeneration config
    prompt = generate_prompt({"description": "test scene"}, {}, {"regenerate_prompt": "MAKE IT POP"})
    if "IMPORTANT CHANGE REQUEST: MAKE IT POP" in prompt:
        print("✅ generate_prompt correctly injects regeneration instruction.")
    else:
        print("❌ generate_prompt FAILED to inject instruction.")
        sys.exit(1)

except Exception as e:
    print(f"❌ Import/Logic Failed: {e}")
    sys.exit(1)

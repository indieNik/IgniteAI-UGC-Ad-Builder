import os
import sys
import subprocess
from dotenv import load_dotenv

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("==================================================")
    print("      AI UGC Ad Video Builder - Launcher")
    print("==================================================")

def run_workflow(llm_provider, image_provider, product_image_path=None, product_description=None):
    print(f"\n🚀 Launching with:")
    print(f"   LLM Provider:   {llm_provider.upper()}")
    print(f"   Visual Provider: {image_provider.upper()}")
    print("--------------------------------------------------\n")
    
    # Set environment variables for this process
    env = os.environ.copy()
    env["LLM_PROVIDER"] = llm_provider
    env["IMAGE_PROVIDER"] = image_provider
    if product_image_path:
        env["PRODUCT_IMAGE_PATH"] = product_image_path
    if product_description:
        env["PRODUCT_DESCRIPTION"] = product_description
    
    # Run the module
    try:
        subprocess.run([sys.executable, "-m", "execution.workflow"], env=env, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Execution failed with exit code {e.returncode}")
    except KeyboardInterrupt:
        print("\n⚠️  Execution interrupted by user.")

def main():
    load_dotenv()
    clear_screen()
    print_header()
    print("\nSelect an Operating Mode:\n")
    print("  [1] 🟢 Default        (OpenAI GPT-4o + DALL-E 3)")
    print("      -> Best for reliability and standard image animation.\n")
    
    print("  [2] 🔵 Google Hybrid  (Gemini 3 + Imagen 4)")
    print("      -> Uses Google's ecosystem with Image-to-Video animation.\n")
    
    print("  [3] 🟣 Google Video   (Gemini 3 + Veo 3.1)")
    print("      -> Creates NATIVE generative video (No static images).\n")
    
    print("  [4] 🧹 Clean Workspace (Remove temp files)")
    print("  [0] 🚪 Exit\n")
    
    choice = input("Enter selection [1-4]: ").strip()
    
    
    # Hardcoded Product Image Path
    DEFAULT_PRODUCT_IMAGE = "brand/designs/image.png"
    
    product_description = None
    
    if choice in ["1", "2", "3"]:
         if os.path.exists(DEFAULT_PRODUCT_IMAGE):
             product_image_path = DEFAULT_PRODUCT_IMAGE
             print(f"✅ Found Product Image: {DEFAULT_PRODUCT_IMAGE}")
         else:
             print(f"❌ CRITICAL ERROR: Product image not found at '{DEFAULT_PRODUCT_IMAGE}'")
             print("   Please place your product image design at this path and try again.")
             sys.exit(1)
             
         # Ask for Product Description
         print("\n📝 Product Context:")
         desc_input = input("   What product are we advertising? (Default: Chai themed Tshirt ad): ").strip()
         product_description = desc_input if desc_input else "Chai themed Tshirt ad"
         print(f"   Target: '{product_description}'\n")
    
    if choice == "1":
        run_workflow("openai", "openai", product_image_path, product_description)
    elif choice == "2":
        run_workflow("gemini", "gemini", product_image_path, product_description)
    elif choice == "3":
        run_workflow("gemini", "veo", product_image_path, product_description)
    elif choice == "4":
        print("Cleaning tmp/, output/, and temporary test files...")
        os.system("rm -rf tmp/* output/* assets/music .tmp projects/backend/.tmp tools/debug/test_*.py")
        # Re-create empty dirs
        os.makedirs("tmp", exist_ok=True)
        os.makedirs("output", exist_ok=True)
        print("Done.")
    elif choice == "0":
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Invalid selection. Using Default (OpenAI).")
        run_workflow("openai", "openai", None, "Generic Product Ad")

if __name__ == "__main__":
    main()

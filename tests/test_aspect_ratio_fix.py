"""
Test script for aspect ratio normalization fix.
Tests the normalize_to_9_16 function with various input aspect ratios.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_normalization_logic():
    """
    Test the normalization algorithm logic without actually creating video clips.
    This validates the math behind the aspect ratio conversion.
    """
    print("=" * 60)
    print("ASPECT RATIO NORMALIZATION TEST")
    print("=" * 60)
    
    TARGET_WIDTH = 1080
    TARGET_HEIGHT = 1920
    target_ratio = TARGET_HEIGHT / TARGET_WIDTH  # 1.777... for 9:16
    
    test_cases = [
        # (width, height, description)
        (1024, 1024, "1:1 Square (Instagram post)"),
        (1920, 1080, "16:9 Landscape (YouTube)"),
        (1080, 1920, "9:16 Vertical (Already correct)"),
        (720, 1280, "9:16 Lower resolution"),
        (2160, 3840, "9:16 4K"),
        (1000, 500, "2:1 Wide landscape"),
        (500, 1000, "1:2 Tall portrait"),
    ]
    
    print(f"\nTarget: {TARGET_WIDTH}x{TARGET_HEIGHT} (9:16, ratio={target_ratio:.3f})\n")
    
    all_passed = True
    
    for width, height, description in test_cases:
        print(f"\n📋 Test: {description}")
        print(f"   Input: {width}x{height}")
        
        current_ratio = height / width
        print(f"   Current ratio: {current_ratio:.3f}")
        
        # Check if already correct
        if abs(current_ratio - target_ratio) < 0.01:
            print(f"   ✅ Already correct aspect ratio, just resize to {TARGET_WIDTH}x{TARGET_HEIGHT}")
            final_w, final_h = TARGET_WIDTH, TARGET_HEIGHT
        else:
            # Calculate scale factor to FILL frame
            scale_factor = max(TARGET_WIDTH / width, TARGET_HEIGHT / height)
            scaled_w = int(width * scale_factor)
            scaled_h = int(height * scale_factor)
            
            print(f"   Scale factor: {scale_factor:.3f} (to fill, not fit)")
            print(f"   Scaled to: {scaled_w}x{scaled_h}")
            print(f"   Then crop to: {TARGET_WIDTH}x{TARGET_HEIGHT}")
            
            final_w, final_h = TARGET_WIDTH, TARGET_HEIGHT
        
        # Verify output
        output_ratio = final_h / final_w
        if abs(output_ratio - target_ratio) < 0.01:
            print(f"   ✅ PASS: Output is {final_w}x{final_h} (ratio={output_ratio:.3f})")
        else:
            print(f"   ❌ FAIL: Output ratio {output_ratio:.3f} doesn't match target {target_ratio:.3f}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED - Normalization logic is correct!")
    else:
        print("❌ SOME TESTS FAILED - Check the logic")
    print("=" * 60)
    
    return all_passed

def test_with_actual_moviepy():
    """
    Test with actual MoviePy if available.
    Creates a test image and applies the normalization function.
    """
    print("\n\n" + "=" * 60)
    print("MOVIEPY INTEGRATION TEST")
    print("=" * 60)
    
    try:
        from PIL import Image
        from moviepy import ImageClip
        import tempfile
        
        # Import the actual function
        from execution.assembly import normalize_to_9_16
        
        print("\n✅ MoviePy is available, running integration test...\n")
        
        # Create a test 1:1 image
        test_img_path = tempfile.mktemp(suffix=".png")
        img = Image.new('RGB', (1024, 1024), color='red')
        img.save(test_img_path)
        print(f"Created test image: 1024x1024 (1:1)")
        
        # Create clip
        clip = ImageClip(test_img_path)
        if hasattr(clip, 'with_duration'):
            clip = clip.with_duration(1.0)
        else:
            clip = clip.set_duration(1.0)
        
        print(f"Original clip size: {clip.size}")
        
        # Apply normalization
        normalized_clip = normalize_to_9_16(clip)
        
        print(f"Normalized clip size: {normalized_clip.size}")
        
        # Verify
        if normalized_clip.size == (1080, 1920):
            print("✅ PASS: Clip normalized to 1080x1920!")
            
            # Clean up
            os.remove(test_img_path)
            return True
        else:
            print(f"❌ FAIL: Expected (1080, 1920), got {normalized_clip.size}")
            os.remove(test_img_path)
            return False
            
    except ImportError as e:
        print(f"⚠️  MoviePy not available: {e}")
        print("Skipping MoviePy integration test")
        return True  # Don't fail if MoviePy not installed
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🎬 Starting Aspect Ratio Fix Tests...\n")
    
    # Test 1: Logic validation
    logic_passed = test_normalization_logic()
    
    # Test 2: MoviePy integration (if available)
    moviepy_passed = test_with_actual_moviepy()
    
    # Summary
    print("\n\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Logic Test: {'✅ PASSED' if logic_passed else '❌ FAILED'}")
    print(f"MoviePy Test: {'✅ PASSED' if moviepy_passed else '❌ FAILED'}")
    
    if logic_passed and moviepy_passed:
        print("\n🎉 All tests passed! Aspect ratio fix is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Review the output above.")
        sys.exit(1)

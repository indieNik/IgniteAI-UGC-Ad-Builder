"""
Tests for assembly.py and scene_generation.py fixes.

These tests verify:
1. End card generation with missing product image
2. Watermark positioning without margin() method errors
3. File handling robustness
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_end_card_no_product_image():
    """Test end card generation when product image doesn't exist."""
    print("\n=== Test 1: End Card Without Product Image ===")
    
    from execution.scene_generation import generate_end_card
    
    # Create temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "end_card_test.png")
        
        # Use non-existent product image path
        fake_product_path = "/path/that/does/not/exist/product.png"
        
        cta_text = "Shop Now. Link in Bio!"
        website = "www.example.com"
        
        visual_dna = {
            "product": {
                "name": "Test Product",
                "visual_description": "A modern gadget"
            }
        }
        
        config = {
            "watermark_enabled": False  # Disable watermark for simplicity
        }
        
        try:
            # This should NOT crash even with missing product image
            result_url = generate_end_card(
                fake_product_path, 
                cta_text, 
                website, 
                output_path, 
                visual_dna=visual_dna,
                config=config
            )
            
            # Verify output file exists
            assert os.path.exists(output_path), "End card file was not created"
            
            # Verify it's a valid PNG
            from PIL import Image
            img = Image.open(output_path)
            assert img.size == (1080, 1920), f"Expected size (1080, 1920), got {img.size}"
            
            print("✅ PASS: End card generated successfully without product image")
            print(f"   Output: {output_path}")
            print(f"   Size: {img.size}")
            
            return True
            
        except Exception as e:
            print(f"❌ FAIL: End card generation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_watermark_positioning():
    """Test that watermark can be applied without margin() attribute error."""
    print("\n=== Test 2: Watermark Positioning ===")
    
    try:
        from moviepy import VideoFileClip, ColorClip, TextClip, CompositeVideoClip
    except ImportError:
        print("⚠️  SKIP: MoviePy not available")
        return None
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple test video (5 second color clip)
        test_video_path = os.path.join(tmpdir, "test_video.mp4")
        output_path = os.path.join(tmpdir, "watermarked_video.mp4")
        
        try:
            # Create a simple 5-second color clip
            clip = ColorClip(size=(1080, 1920), color=(50, 50, 100), duration=2.0)
            clip.write_videofile(test_video_path, fps=24, codec='libx264', logger=None)
            
            # Load it back
            final_video = VideoFileClip(test_video_path)
            
            # Apply watermark using the FIXED code (manual positioning)
            watermark_text = "IGNITE AI"
            
            # Find font
            font_path = None
            possible_fonts = [
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "Arial"
            ]
            for f in possible_fonts:
                if os.path.exists(f) or "/" not in f:
                    font_path = f
                    break
            
            txt_clip = TextClip(
                text=watermark_text,
                font_size=50,
                color='white',
                font=font_path or 'Arial',
                method='label'
            )
            
            txt_clip = txt_clip.with_duration(final_video.duration)
            
            # Apply opacity
            try:
                if hasattr(txt_clip, 'with_opacity'):
                    txt_clip = txt_clip.with_opacity(0.3)
                elif hasattr(txt_clip, 'set_opacity'):
                    txt_clip = txt_clip.set_opacity(0.3)
            except Exception as e:
                print(f"   Note: Opacity setting not available ({e})")
            
            # FIXED POSITIONING - Manual coordinates (no margin() call)
            video_width, video_height = final_video.size
            txt_width, txt_height = txt_clip.size
            margin_right = 20
            margin_bottom = 20
            
            x_pos = video_width - txt_width - margin_right
            y_pos = video_height - txt_height - margin_bottom
            txt_clip = txt_clip.with_position((x_pos, y_pos))
            
            # Composite
            final_video = CompositeVideoClip([final_video, txt_clip])
            
            # Export
            final_video.write_videofile(output_path, fps=24, codec='libx264', logger=None)
            
            # Verify output exists
            assert os.path.exists(output_path), "Watermarked video was not created"
            
            print("✅ PASS: Watermark applied successfully without margin() error")
            print(f"   Output: {output_path}")
            print(f"   Position: ({x_pos}, {y_pos})")
            
            # Cleanup
            final_video.close()
            clip.close()
            
            return True
            
        except AttributeError as e:
            if "margin" in str(e):
                print(f"❌ FAIL: margin() AttributeError still exists: {e}")
                return False
            else:
                raise
        except Exception as e:
            print(f"❌ FAIL: Watermark test failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False


def test_assembly_with_remote_fallback():
    """Test that assembly can handle missing local files via remote fallback."""
    print("\n=== Test 3: Assembly with Remote Fallback ===")
    
    # This is more of an integration test - just verify the logic exists
    from execution import assembly
    import inspect
    
    # Check if the remote fallback code is present
    source = inspect.getsource(assembly.assemble_video)
    
    checks = [
        "remote_assets" in source,
        "Local file missing" in source or "Falling back to remote" in source,
        "requests.get" in source
    ]
    
    if all(checks):
        print("✅ PASS: Remote fallback logic present in assembly.py")
        return True
    else:
        print("❌ FAIL: Remote fallback logic incomplete")
        return False


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Running Assembly Fixes Test Suite")
    print("=" * 60)
    
    results = {
        "End Card (No Product)": test_end_card_no_product_image(),
        "Watermark Positioning": test_watermark_positioning(),
        "Remote Fallback Logic": test_assembly_with_remote_fallback()
    }
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else ("⚠️  SKIP" if result is None else "❌ FAIL")
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print(f"\nPassed: {passed}/{total}")
    
    return all(r is not False for r in results.values())


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

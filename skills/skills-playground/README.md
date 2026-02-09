# Skills Playground

Test ground for experimenting with individual skills and combinations.

## 🎬 Available Tests

### Caption + Voice Sync Test
**File:** `test_caption_voice_sync.py`

Demonstrates both skills working together to create a video with synced voiceover and captions.

**Test Input:**
- Video: `input_video.mp4`
- Script: `"[excited] Cafe? The Jaggery Point in Bangalore. Anytime! [laugh]"`

**What it does:**
1. ✅ Generates voiceover (auto-cleans `[excited]` and `[laugh]`)
2. ✅ Overlays audio onto video
3. ✅ Burns captions (perfectly synced with voiceover duration)

**Run:**
```bash
python3 skills/skills-playground/test_caption_voice_sync.py
```

**Output:**
- `voiceover.mp3` - Generated audio
- `video_with_audio.mp4` - Video + voiceover
- `final_output.mp4` - Complete video with audio + captions

---

## 📁 Setup

Place your test video:
```bash
cp path/to/your/video.mp4 skills/skills-playground/input_video.mp4
```

Then run any test script!

## 🎯 Purpose

This playground lets you:
- Test skills independently
- Experiment with combinations
- Verify integration before using in production
- Rapidly iterate on parameters

## 🚀 Quick Test

```bash
# 1. Add test video
cp docs/guides/video.mp4 skills/skills-playground/input_video.mp4

# 2. Run integration test
python3 skills/skills-playground/test_caption_voice_sync.py

# 3. Check output
open skills/skills-playground/final_output.mp4
```

Enjoy experimenting! 🎉

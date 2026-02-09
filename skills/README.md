# Skills Directory

Reusable, standalone agents that can be used independently or integrated into larger workflows.

## Available Skills

### 🎬 [Caption Generator](./caption_generator/)
Add stylized captions to videos with precise positioning control.

**Quick Start:**
```python
from skills.caption_generator.agent import CaptionGenerator

gen = CaptionGenerator()
output = gen.burn_captions(
    video_path="video.mp4",
    caption_text="Hello, world!",
    position="bottom"
)
```

---

### 🎙️ [Voice Generator](./voice_generator/)
Generate professional voiceovers from text using ElevenLabs TTS.

**Quick Start:**
```python
from skills.voice_generator.agent import VoiceGenerator

gen = VoiceGenerator()
audio = gen.generate_voice(
    script="Welcome!",
    voice_name="rachel"
)
```

---

## Philosophy

Each skill:
- ✅ **Standalone**: Works independently without external dependencies
- ✅ **Documented**: Includes README with examples
- ✅ **Testable**: Has example scripts for verification
- ✅ **Reusable**: Can be used in any project

## Usage

Import skills directly:
```python
from skills.caption_generator.agent import CaptionGenerator
from skills.voice_generator.agent import VoiceGenerator
```

Or run examples:
```bash
python3 skills/caption_generator/example.py
python3 skills/voice_generator/example.py
```

## Integration

Skills are automatically integrated into the main video generation workflow via:
- `execution/voice_generation.py` → Uses Voice Generator
- `execution/final_assembly.py` → Uses Caption Generator

## License

All skills are reusable - integrate freely!

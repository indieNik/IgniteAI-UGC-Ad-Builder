# Voice Tags vs Caption Text - Best Practices

## The Rule

**Expressive tags `[tag]` are ONLY for voice generation, NOT for captions.**

## Why?

- **Voice**: Tags control TTS emotion/timing → `[excited]`, `[laugh]`, `[pause]`
- **Captions**: Display clean, readable text for viewers

## Implementation

### ✅ Correct: Separate Processing

```python
from skills.voice_generator.agent import VoiceGenerator

script = "[excited] Cafe? The Jaggery Point in Bangalore. Anytime! [laugh]"
gen = VoiceGenerator()

# For VOICE: Keep expressive tags
voice_text = gen.clean_script(script, preserve_expressive_tags=True)
# Result: "[excited] Cafe? The Jaggery Point in Bangalore. Anytime! [laugh]"
audio = gen.generate_voice(script=voice_text)

# For CAPTIONS: Remove expressive tags
caption_text = gen.clean_script(script, preserve_expressive_tags=False)
# Result: "Cafe? The Jaggery Point in Bangalore. Anytime!"
caption_gen.burn_captions(caption_text=caption_text)
```

### ❌ Wrong: Same Text for Both

```python
# BAD: Captions will show "[excited]" on screen
cleaned = gen.clean_script(script)  # Keeps tags by default
audio = gen.generate_voice(script=cleaned)
caption_gen.burn_captions(caption_text=cleaned)  # Shows tags!
```

## Visual Example

**Input Script:**
```
[excited] Cafe? The Jaggery Point in Bangalore. Anytime! [laugh]
```

**Voice Output (TTS):**
- Hears: Excited tone + "Cafe? The Jaggery Point in Bangalore. Anytime!" + laugh sound
- Tags control emotion/actions

**Caption Output (Display):**
```
Cafe? The Jaggery Point in Bangalore. Anytime!
```
- Clean text only
- No `[excited]` or `[laugh]` visible

## Quick Reference

| Use Case | preserve_expressive_tags | Example Output |
|----------|-------------------------|----------------|
| Voice generation | `True` (default) | `[happy] Hello!` |
| Caption display | `False` | `Hello!` |
| Script logging | `True` | `[whispers] Secret...` |

## Integration Test Pattern

```python
# Step 1: Generate voice WITH tags
voice_text = gen.clean_script(script, preserve_expressive_tags=True)
audio = gen.generate_voice(script=voice_text)

# Step 2: Generate captions WITHOUT tags
caption_text = gen.clean_script(script, preserve_expressive_tags=False)
caption_gen.burn_captions(caption_text=caption_text)
```

This ensures:
- ✅ Voice has emotional expressions
- ✅ Captions are clean and readable
- ✅ No confusing `[tags]` on screen

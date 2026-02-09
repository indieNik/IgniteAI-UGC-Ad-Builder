# Voice Generator Skill

Standalone agent for generating high-quality voiceovers from text using ElevenLabs TTS.

## Features

- 🎙️ **ElevenLabs v3 Integration**: Latest model with expressive audio tags
- 🎭 **Expressive Audio Tags**: [sad], [angry], [laughs], [whispers], [shouts]
- ⏸️ **Pause Control**: [pause], [short pause], [long pause]
- 🧹 **Smart Script Cleaning**: Auto-removes stage directions, timing markers
- 🎭 **6 Pre-configured Voices**: Male and female options
- ⚙️ **Customizable Settings**: Control stability, clarity, and style
- 🔌 **Plug-and-Play**: Works standalone or integrated

## Quick Start

```python
from skills.voice_generator.agent import VoiceGenerator

# Initialize with API key
generator = VoiceGenerator(api_key="your_elevenlabs_api_key")

# Generate voiceover
audio_path = generator.generate_voice(
    script="Welcome to the best cafe in Bengaluru!",
    voice_name="riley",  # Calm, clear female voice
    output_path="voiceover.mp3"
)

print(f"✅ Audio: {audio_path}")
```

## Expressive Audio Tags (ElevenLabs v3)

### Emotions
```python
script = "[happy] Welcome! [pause] [sad] We're closing soon."
audio = generator.generate_voice(script=script)
```

**Available emotion tags:**
- `[sad]` - Sad tone
- `[angry]` - Angry tone
- `[happy]` - Happy tone

### Actions
```python
script = "[whispers] Secret menu available. [shouts] Order now! [laughs]"
audio = generator.generate_voice(script=script)
```

**Available action tags:**
- `[whispers]` - Whispered voice
- `[shouts]` - Shouting voice
- `[laughs]` - Laughter
- `[clears throat]` - Throat clearing
- `[sighs]` - Sighing sound

### Pauses
```python
script = "Step 1: Order. [short pause] Step 2: Enjoy. [long pause] Step 3: Return!"
audio = generator.generate_voice(script=script)
```

**Available pause tags:**
- `[pause]` - Standard pause
- `[short pause]` - Brief pause
- `[long pause]` - Extended pause

## Available Voices

| Name | ID | Description |
|------|----|----|
| **riley** | `hA4zG...` | Calm, clear female (default) |
| **rachel** | `21m00...` | Calm, clear female |
| **domi** | `AZnzl...` | Strong, confident female |
| **bella** | `EXAVl...` | Soft, gentle female |
| **antoni** | `ErXwo...` | Well-rounded male |
| **josh** | `TxGEq...` | Deep, narrative male |
| **arnold** | `VR6Ae...` | Crisp, authoritative male |

## Script Cleaning

The agent automatically cleans scripts before generation while **preserving** expressive tags:

**Input:**
```
VOICEOVER (Excited): [happy] Welcome to Bengaluru! (3s) [laughs]
```

**Output:**
```
[happy] Welcome to Bengaluru! [laughs]
```

**Removed:**
- `VOICEOVER` prefixes
- Stage directions: `(Excited)`, `(Narrator)`
- Timing markers: `(3s)`, `(5 seconds)`
- Asterisks: `*giggles*`

**Preserved:**
- Expressive tags: `[happy]`, `[laughs]`, `[sad]`, `[whispers]`, etc.
- Pause tags: `[pause]`, `[short pause]`, `[long pause]`

## API Reference

### `VoiceGenerator.generate_voice()`

Generate voiceover from text.

**Parameters:**
- **script** (`str`): Text to convert to speech (supports expressive tags)
- **output_path** (`str`, optional): Audio file save path
- **voice_id** (`str`, optional): ElevenLabs voice ID
- **voice_name** (`str`, default=`"riley"`): Pre-configured voice name
- **model** (`str`, default=`"eleven_v3"`): TTS model (v3 for expressive tags)
- **stability** (`float`, default=`0.5`): Voice consistency - **v3 ONLY allows: 0.0, 0.5, 1.0**
  - `0.0` = Creative (more variation)
  - `0.5` = Natural (balanced) ⭐ **Recommended**
  - `1.0` = Robust (very consistent)
- **similarity_boost** (`float`, default=`0.75`): Voice clarity (0-1)
- **style** (`float`, default=`0.0`): Style exaggeration (0-1)
- **use_speaker_boost** (`bool`, default=`True`): Enhance speaker presence

**Returns:** `str` - Path to generated audio file

**Limitations:**
- 5,000 character limit per request
- Not designed for real-time applications

## Dependencies

- ElevenLabs API key (set `ELEVENLABS_API_KEY` env variable)
- `requests` library
- Python 3.7+

## Example: Expressive Cafe Ad

```python
script = """
[happy] Hey Bengaluru! [short pause]
[whispers] Want to know a secret? [pause]
[excited] The Jaggery Point has the BEST coffee! [laughs]
[pause]
[calm] Visit us today.
"""

generator = VoiceGenerator()
audio = generator.generate_voice(
    script=script,
    voice_name="riley"
)
```

## Integration

```python
# Use in your video pipeline
from skills.voice_generator.agent import VoiceGenerator

def add_voiceover(script_text):
    gen = VoiceGenerator()
    return gen.generate_voice(script=script_text, voice_name="riley")
```

## License

Reusable skill - integrate freely into any project!

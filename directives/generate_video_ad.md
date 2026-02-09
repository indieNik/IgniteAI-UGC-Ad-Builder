# Directive: Generate Video Ad

**Goal**: Generate a 15-30s UGC-style video ad for a product.

## Inputs
-   **Topic**: Product Name or specific angle (e.g., "AI Video Generator", "Summer Sale").
-   **Product Image**: Path to the product image file.
-   **Duration**: Target duration (15s, 30s).
-   **Vibe**: Desired mood (e.g., "Energetic", "Relaxed", "Professional").
-   **Config**: `brand/configuration.json` (optional overrides).

## Process Flow

### 1. Visual DNA Extraction (`execution/visual_dna.py`)
-   **Input**: Product Image, Topic.
-   **Output**: JSON with `character` (age, style), `product` (description), `setting` (lighting).
-   **Why**: Ensures consistency across all generated scenes.

### 2. Script Generation (`execution/script_generation.py`)
-   **Input**: Topic, Duration, Visual DNA.
-   **Output**: JSON Shotlist (Scenes + Voiceover).
-   **Constraint**: Must match target duration.

### 3. Scene Generation (`execution/scene_generation.py`)
-   **Input**: Shotlist, Visual DNA, Config.
-   **Execution**:
    -   **Parallel Execution**: Generate all scenes simultaneously.
    -   **Mode**: `veo` (Video) or `imagen` (Image + Ken Burns).
-   **Output**: List of video file paths.

### 4. Voice Generation (`execution/voice_generation.py`)
-   **Input**: Script Text.
-   **Output**: MP3 file (ElevenLabs).

### 5. Music Generation (`execution/music_selection.py`)
-   **Input**: Vibe, Visual DNA.
-   **Output**: MP3 file (Background Music).
-   **Logic**: Maps "Vibe" to musical prompts (e.g., "Energetic" -> "Upbeat Lo-Fi").

### 6. Assembly (`execution/assembly.py`)
-   **Input**: Scene Videos, Voiceover, BGM.
-   **Output**: Final MP4.
-   **Logic**: Syncs video duration to audio duration. Loops BGM.

## Execution Tools
-   `execution/visual_dna.py`
-   `execution/script_generation.py`
-   `execution/scene_generation.py`
-   `execution/voice_generation.py`
-   `execution/music_selection.py`
-   `execution/assembly.py`

## Outputs
-   **Final Video**: `output/final_ad_[timestamp].mp4`
-   **Intermediates**: `tmp/` (scenes, audio).

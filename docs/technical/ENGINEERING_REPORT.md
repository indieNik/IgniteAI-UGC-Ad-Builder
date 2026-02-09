# Engineering Report: AI UGC Ad Video Builder

**Date**: December 25, 2025
**Version**: 1.0.0
**Status**: Final Implementation

## 1. Executive Summary

The **AI UGC Ad Video Builder** is a programmatic content generation system designed to produce high-fidelity "User Generated Content" (UGC) style video ads. Unlike standard "text-to-video" tools that generate a single chaotic stream, this system uses a **structured, agentic pipeline** to decompose the creative process into discrete, controllable steps: Visual DNA extraction, Scripting, Scene Generation, Voice Synthesis, and Assembly.

This report details the implementation architecture, specific engineering decisions, and the "Why" behind every major component.

---

## 2. System Architecture

The system follows a strict **3-Layer Architecture** to separate intent from execution:

1.  **Layer 1: Directive (Intent)**: User inputs (Topic, Product Image) and Configuration (`brand/configuration.json`).
2.  **Layer 2: Orchestration (LangGraph)**: A state machine (`execution/workflow.py`) that manages the flow of data, error handling, and parallel execution.
3.  **Layer 3: Execution (Deterministic Tools)**: Stateless Python modules in `execution/` that interface with external APIs (OpenAI, Google Gemini/Veo, ElevenLabs).

### Data Flow
```
[Input] -> [Visual DNA] -> [Script] -> [Scenes (Parallel)] -> [Voice] -> [Assembly] -> [Output]
```

---

## 3. Module Implementation Details

### 3.1 Visual DNA (`execution/visual_dna.py`)
**Goal**: Enforce visual consistency across unrelated generation calls.

*   **Implementation**: We extract a JSON object containing `character` (age, look, clothing), `product` (visual description), and `setting` (lighting, location).
*   **Why**: Generative models are stochastic. If you ask for a "girl drinking coffee" 5 times, you get 5 different girls. By locking the description in `Visual DNA` and prepending it to *every* subsequent prompt, we significantly reduce character drift without needing training LORAs.

### 3.2 Script Generation (`execution/script_generation.py`)
**Goal**: Generate a structured shotlist that parses easily into code.

*   **Implementation**: Uses a large context LLM (Gemini 2.0 Flash or GPT-4o) to output a JSON object with `script` (VO) and `scenes` (List of visual actions).
*   **Why**: We enforce a specific JSON schema. This allows us to iterate over the `scenes` list programmatically.
*   **Prompt Engineering**: The system prompt explicitly forbids "TV Commercial" language (e.g., "Welcome to...") and enforces "Short-form social" vibes (e.g., "POV: You found...").

### 3.3 Scene Generation (`execution/scene_generation.py`)
**Goal**: Create visual assets (Video or Image) for each shot.

*   **Hybrid Engine**: The system supports swappable backends:
    *   **Google Veo 3.1**: Generates native 6s video clips.
    *   **Google Imagen 4**: Generates high-fidelity static images.
    *   **OpenAI DALL-E 3**: Fallback for static images.

*   **The "Ken Burns" Fallback**:
    *   **Problem**: Native video generation (Veo) is expensive and slow.
    *   **Solution**: For static image modes, we use `MoviePy` to apply a dynamic zoom (Ken Burns effect).
    *   **Logic**: `clip.resize(lambda t: 1 + 0.04 * t)` creates a subtle 4% zoom over the clip duration, mimicing camera movement.

*   **Smart End Card Feature**:
    *   We generate a specific "Hero Shot" for the final scene and overlay text programmatically using `Pillow` (PIL). This ensures the CTA is readable and not "hallucinated" by the AI.

### 3.4 Voice Generation (`execution/voice_generation.py`)
**Goal**: Authentic, non-robotic narration.

*   **Implementation**: Uses ElevenLabs API.
*   **Smart Caching**: Files are named by the hash of their content (`md5(text).mp3`). This prevents regenerating audio if the script hasn't changed, saving API costs.
*   **Sync Logic**: The generation function returns the *exact duration* of the audio file, which drives the video timing in the Assembly phase.

### 3.5 Assembly (`execution/assembly.py`)
**Goal**: Stitch assets into a cohesive MP4.

*   **Engine**: `MoviePy` (Python wrapper for FFmpeg).
*   **Audio-Driven Editing**:
    *   The visual clip duration is forced to match the audio narration duration for that scene.
    *   If the video is too short, it loops. if too long, it's trimmed.
*   **Crossfades**: A 0.5s crossfade is applied between audio clips for smoothness.

---

## 4. Key Engineering Decisions & Rationale

### 4.1 Why LangGraph?
We chose **LangGraph** over a simple imperative script because:
1.  **State Management**: It passes a strictly typed `AgentState` object between nodes, reducing global variable chaos.
2.  **Resilience**: It allows for easy implementation of retries or "human-in-the-loop" approval steps in the future without rewriting the core logic.

### 4.2 Why "Head Trimming" for Veo?
*   **Problem**: When doing Image-to-Video generation, the first ~1 second often looks "frozen" or static as the model transitions from the reference frame to motion.
*   **Decision**: We generate 1-2 seconds *more* than needed, and programmatically trim the start.
*   **Why**: This yields a video that starts *in motion*, feeling much more professional.

### 4.3 Why not use LangChain for everything?
We purposely avoided heavy `LangChain` abstractions for the *Execution* layer (API calls).
*   **Why**: Debugging deep LangChain stacks is difficult. We prefer raw `requests` or official SDK clients (Google GenAI SDK, OpenAI SDK) for the actual API interaction. This makes the code readable and easy to fix if an API signature changes.

### 4.4 The "Multimodal" Consistency Hack
For consistency, we pass the *previous scene's generated image* as a reference input to the *next scene's* generation call (when using Gemini Multimodal).
*   **Why**: This provides the model with visual context of "what the actor looks like" in the previous shot, improving continuity significantly compared to text-only prompting.

---

## 5. Current Metrics & Limits

*   **Execution Time**:
    *   OpenAI Mode: ~2-3 minutes per ad.
    *   Google Veo Mode: ~5-8 minutes (Video generation is heavy).
*   **Resolution**:
    *   Vertical 9:16 (1080x1920) is the hardcoded standard for Reels/TikTok.
*   **Cost**:
    *   Roughly $0.10 - $0.50 per ad depending on model choice (Veo is premium).

---

## 6. Conclusion

The pipeline is now stable. By treating creativity as a structured data transformation problem rather than a "one-shot" generation task, we achieved the ability to debug, iterate, and scale video ad production reliably.

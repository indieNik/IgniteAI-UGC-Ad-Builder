# 📘 IgniteAI System Architecture: The Deep Dive

**"The Owner's Manual"**

This document explains the internal machinery of the **IgniteAI Video Builder**. It covers the agentic workflow, the fail-safe mechanisms, and the communication logic.

---

## 🏗️ The Big Picture: 3-Layer Architecture

1.  **Direct (Frontend)**: The Angular Web UI. It's the "Director." It sends intent ("Make a gym ad") and displays results.
2.  **Orchestrator (Backend API)**: The FastAPI Server. It receives the order, manages the job ID (`run_id`), and routes tasks.
3.  **Agents (Execution)**: The Python scripts that actually do the work (Write, Draw, Speak, Edit).

---

## 🧩 Station 1: The Brain (Scripting & Logic)
**File:** `execution/script_generation.py`

*   **Visual DNA**: Extracts the "Soul" of the ad (e.g., "Gen Z, Lo-fi aesthetic"). usage this to ensure consistency across scenes.
*   **Dynamic Pacing**:
    *   Input: `target_duration` (e.g., 30s).
    *   Logic: Splits time into 4 strict buckets: Hook (20%), Feature (30%), Lifestyle (30%), CTA (20%).
    *   Output: JSON Shotlist with exact second-counts for every scene.

---

## 🤖 Station 2: The Visual Factory (Images & Video)
**File:** `execution/scene_generation.py`

This is the most complex station with a built-in **"Safety Net"**.

### The Flow (Robustness Pipeline)
1.  **Intent**: User selects "Default (OpenAI)" + "Veo 2.0".
2.  **Step A (Base Image)**: System calls `DALL-E 3` to generate the perfect keyframe.
3.  **Step B (Animation - Primary)**:
    *   System sends the DALL-E image to **Google Veo 2.0**.
    *   *Success?* We get an MP4.
    *   *Fail?* (Quota/Safety) -> Go to Step C.
4.  **Step C (Fallback)**:
    *   System catches the error and applies the **Ken Burns Effect** (Pan & Zoom) to the static image.
    *   **Guarantee**: The system **ALWAYS** returns a video file. No crashes.

---

## 🗣️ Station 3: Audio & Sync
**File:** `execution/voice_generation.py`

*   **Smart Scoring**: Generates background music that matches the `music_mood` from the UI.
*   **Voice Casting**: Selects an AI voice ID based on the script's emotional tags.

---

## 📡 Station 4: The Bridge (API & Real-time Status)
**File:** `projects/backend/routers/generation.py`

*   **WebSockets**: Streams live logs ("Generating Scene 1...") to the content overlay.
*   **Asset Polling**:
    *   The Backend creates named assets: `Hook_image.png`, `Feature_image.png`.
    *   The Frontend checks the status every 2 seconds.
    *   When an image is ready, it **instantly appears** on the Storyboard card in the UI.

---

## 🎬 Station 5: The Editor (Assembly)
**File:** `execution/assembly.py`

This is where it all comes together.

1.  **Gathering**: It takes the Video Clips from Station 2 and the Audio from Station 3.
2.  **Stitching**: It lines them up in order (Hook, Feature, Lifestyle, CTA).
3.  **Smart Looping**: If a video clip is shorter than the desired duration, it loops smoothly.
4.  **Audio Mixing**: It blends the Voiceover and the Background Music (at 20% volume).
5.  **Export**: It saves the final result to the session folder `tmp/{run_id}/final_ad_{timestamp}.mp4`.

---

## 🕹️ Configuration & Env

Global settings are managed via `.env` but can be overridden by the UI.

*   `OPENAI_API_KEY`: Required for "Default" mode.
*   `GEMINI_API_KEY`: Required for Veo and Imagen.
*   `ELEVENLABS_API_KEY`: Required for Voice.

---

## 🔮 Future Upgrades

*   **New Models**: Add them to `execution/llm_factory.py`.
*   **New UI Features**: Edit `projects/frontend/src/app`.
*   **New Workflow**: Modify `execution/workflow.py` (LangGraph).

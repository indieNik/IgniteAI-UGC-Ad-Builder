# Product Requirements Document (PRD): Parallel AI Video Generator

**Version:** 1.0  
**Status:** Approved  
**Date:** January 2026  

## 1. Overview
The **Parallel AI Video Generator** is a high-performance system designed to create broadcast-quality UGC (User Generated Content) ads programmatically. It shifts from a sequential "daisy-chain" model to a "Character-First" parallel topology, ensuring visual consistency while maximizing generation speed.

## 2. Problem Statement
*   **Speed**: Sequential generation is too slow for real-time user gratification.
*   **Consistency**: Characters "drift" between scenes (User A in Scene 1 looks different in Scene 3).
*   **Polish**: Current outputs lack professional transitions, dynamic captions, and 4K resolution.

## 3. The 10-Step Workflow (Core Requirement)
The system MUST execute the following 10 steps for every generation:

1.  **Storyline Creation**: Generate a narrative flow/script based on the product image and user description.
2.  **Character Anchor**: Generate a consistent "Actor" image using/showcasing the product. This creates the "Visual DNA" for all subsequent scenes.
3.  **Parallel Scene Execution**:
    *   **Input**: Storyline + Character Anchor.
    *   **Process**: For each scene (Hook, Feature, Lifestyle, CTA) run concurrently:
        *   3a. **Generate Image**: High-fidelity scene composition.
        *   3b. **Generate Video**: Animate using Veo (Image-to-Video).
        *   3c. **Fallback**: If Veo fails, use dynamic Ken Burns effect.
4.  **End Card**: Generate a dynamic end card tailored to the product type.
5.  **Transitions**: Apply **White Fade-Out** transitions between all scenes.
6.  **Voiceover (VO)**: Check for native audio; if missing, generate AI VO (ElevenLabs).
7.  **Captions**:
    *   **Engine**: Google Speech-to-Text (STT).
    *   **Style**: Single-word animation.
    *   **Position**: Bottom 1/3, vertically centered.
    *   **Design**: Solid/Gradient background with high contrast.
8.  **Background Music (BGM)**:
    *   **Volume**: Strictly **20%** of final mix (0.2).
    *   **Logic**: Must not overpower VO.
9.  **Watermark**: "IGNITEAI" text/logo at **Bottom Right** with **20px margin**.
10. **4K Upscaling**: If "Premium" tier is active, upscale final output to 2160x3840.

## 4. Technical Architecture
*   **Topology**: Star Topology (Character -> [Schools]).
*   **Orchestration**: LangGraph.
*   **Concurrency**: Python `ThreadPoolExecutor` with robust Rate Limiting.
*   **Services**:
    *   **LLM**: Gemini 1.5 Pro / GPT-4o
    *   **Image**: Imagen 2.5 (Multimodal)
    *   **Video**: Google Veo
    *   **Voice**: ElevenLabs
    *   **Captions**: Google Cloud Speech-to-Text
    *   **Assembly**: MoviePy

## 5. Success Metrics
*   **Consistency**: The same character is recognizable in at least 90% of scenes.
*   **Speed**: Total generation time < 2 minutes (parallelism gain).
*   **Quality**: 4K resolution output with readable, synchronized captions.

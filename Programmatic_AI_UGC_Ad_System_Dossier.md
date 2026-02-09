# 📘 Programmatic AI-Generated UGC Ad System — Dossier

## 1. The Problem

High-performing UGC ads (like Rhode-style content) require:
- Strong hooks
- Structured shot lists
- Consistent characters & products
- Voiceovers
- Tight editing

This traditionally means creators, editors, reshoots, delays, and high costs.

**Core problem:**  
UGC ads are creative, but the *process* is repetitive and non-scalable.

Most AI approaches try to generate everything in one prompt, resulting in:
- Inconsistency
- Non-repeatable output
- No debugging or iteration path

---

## 2. Design Philosophy

**Key Insight:** Creativity should live in structure, not randomness.

Principles:
- Programmatic-first
- Deterministic workflows
- Stateless agents
- Scene-level retries
- Human-editable inputs
- Machine-enforced consistency

Think factory, not magic.

---

## 3. End-to-End Process

```
Creative Intent
 → Shot List
 → Scene Assets
 → Voice
 → QC
 → Assembly
 → Final Ad
```

### Step Breakdown

1. **Input & Intent**
   - Base image
   - Platform
   - Duration
   - Goal  
   Output: Structured creative brief (JSON)

2. **Shot List**
   - Inspired by Rhode workflow
   - Managed via Google Sheets
   - A-roll / B-roll, script, visual action, duration

3. **Visual Consistency Lock**
   - Extract character & product attributes
   - Create reusable “Visual DNA”

4. **Scene Prompt Construction**
   - One prompt per scene
   - Always reference Visual DNA
   - No ambiguity

5. **Scene Generation**
   - Image / video generation APIs
   - Seeded & isolated per scene

6. **Voice Generation**
   - ElevenLabs
   - Consistent UGC-style voice
   - Duration captured for sync

7. **Quality Control**
   - Face similarity (embeddings)
   - Product presence
   - Text distortion
   - Lighting deviation
   - Scene-level retries only

8. **Assembly**
   - FFmpeg / MoviePy
   - Order scenes
   - Align with voice
   - Export final 9:16 video

---

## 4. Tools & Stack

### Orchestration
- LangGraph

### Backend
- Python

### Input Layer
- Google Sheets

### AI & APIs
- OpenAI (multimodal, vision, embeddings)
- Image / Video Generation API
- ElevenLabs (voice)

### Storage
- Google Cloud Storage (pipeline assets)
- Google Drive (final outputs)
- PostgreSQL (metadata & logs)

### Assembly
- FFmpeg
- MoviePy

---

## 5. Architecture

```
Trigger (API / Sheet)
   ↓
LangGraph Orchestrator
   ↓
Stateless Agents
   ↓
GCS (Artifacts)
   ↓
QC Loop
   ↓
Assembly
   ↓
Final Video → Drive
```

Properties:
- Deterministic
- Replayable
- Scalable
- Debuggable

---

## 6. Final Solution

The system enables:
- Consistent UGC ads from a single image
- Shot-list-driven storytelling
- Fully programmatic execution
- Scene-level retries
- High scalability
- Full auditability

Avoids:
- One-prompt failures
- Manual editing
- Visual drift
- Tool lock-in

---

## 7. Why It Matters

This system acts as a **Creative Operating System**:
- Creativity as structure
- AI where it’s strong
- Engineering where it’s reliable

New products → new sheets  
New ads → new runs  
Improvements → versioned agents

---

## Status

**Architecture: Locked  
Process: Defined  
Tools: Locked**

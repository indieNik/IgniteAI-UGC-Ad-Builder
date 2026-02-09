---
title: IgniteAI
emoji: 🎬
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
# ⚠️ CRITICAL: DO NOT REMOVE THIS YAML FRONTMATTER
# Required for Hugging Face Spaces deployment
# Removing this will cause "Missing configuration in README" error
---

# IgniteAI: Production-Grade Agentic UGC Video Factory

**"Creativity as Structure."**

IgniteAI is a state-of-the-art AI video generation platform that transforms creative intent into high-performing User Generated Content (UGC) ads. Built for brands that demand consistency, scalability, and 100% production reliability.

---

## 🏗️ System Architecture

### Three-Layer Agentic Model

IgniteAI operates on a deterministic, fault-tolerant architecture designed for zero-failure production environments:

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (Angular 17)                  │
│  - Glassmorphic UI with real-time WebSocket updates     │
│  - Scene-by-scene regeneration with history tracking    │
│  - Visual DNA configuration & brand presets             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│               Backend (FastAPI + LangGraph)              │
│  ┌─────────────────────────────────────────────────┐    │
│  │  LangGraph State Machine (Directed Graph)       │    │
│  │  ├─ Visual DNA Node (character consistency)     │    │
│  │  ├─ Script Generation Node (GPT-4o/Gemini)      │    │
│  │  ├─ Scene Generation Nodes (parallel)           │    │
│  │  │   ├─ Hook                                    │    │
│  │  │   ├─ Feature                                 │    │
│  │  │   ├─ Lifestyle                               │    │
│  │  │   └─ CTA                                     │    │
│  │  ├─ Voice Generation Node (ElevenLabs)          │    │
│  │  ├─ Music Composition Node (ElevenLabs)         │    │
│  │  └─ Assembly Node (FFmpeg + MoviePy)            │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│            Model Factory (Tiered Fallback)               │
│  Video: Veo 3.1 → Veo 2.0 → Ken Burns (always succeeds) │
│  Image: Imagen 4.0 → DALL-E 3 → Stable Diffusion        │
│  Audio: ElevenLabs → Google TTS                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🧬 Visual DNA™ Technology

Our proprietary consistency engine that guarantees character/product appearance across all frames:

### Algorithm
```python
def extract_visual_dna(product_image_path: str) -> Dict:
    """
    Extracts semantic attributes for cross-frame consistency.
    
    Process:
    1. Multimodal analysis (Gemini 2.0 Flash Thinking)
    2. Extract: gender, age, ethnicity, clothing, setting
    3. Store as immutable DNA for scene generation
    4. Inject DNA into every prompt for coherence
    
    Returns:
        {
            "character": {
                "gender": "female",
                "age_range": "25-30",
                "ethnicity": "South Asian",
                "appearance": "casual modern attire",
                "expression": "friendly, approachable"
            },
            "product": {
                "name": "...",
                "visual_description": "...",
                "key_features": [...]
            },
            "brand_palette": ["#FF6B6B", "#4ECDC4"]
        }
    """
```

### Self-Consistency for Regeneration
When a scene is regenerated, it uses its **own previous version** as the reference (not the preceding scene), preventing character drift:

```python
if regenerate_scene_id == scene_id:
    # Use self as reference (not previous scene)
    base_image = remote_assets.get(f"{scene_id}_image")
else:
    # Use previous scene for initial generation
    base_image = last_generated_image
```

---

## 📚 Assets Library

Centralized hub for browsing and managing all generated assets from your campaigns.

### Features

**Campaign Grouping**
- Assets organized by campaign ID with collapsible sections
- Visual status indicators (green = completed, red = failed)
- Campaign metadata: ID, name, timestamp, asset count

**Interactive Preview**
- Auto-play on hover for video assets (muted preview)
- Click any asset to open full-screen preview modal
- Navigate between assets with prev/next controls
- Download assets directly from preview

**Smart Asset Extraction**
- Automatically collects all assets from each campaign:
  - Final rendered videos
  - Individual scene videos/images
  - Remote assets from Firebase Storage
- Sorted by newest first

### Usage

Navigate to `/library` route to access the Assets Library. All assets from completed and failed campaigns are automatically available.

```typescript
// Asset structure
interface Asset {
  type: 'video' | 'image';
  url: string;
  sourceRunId: string;
  createdAt: number;
  label: string;
}

// Campaign grouping
interface CampaignGroup {
  run_id: string;
  status: 'completed' | 'failed' | 'running';
  timestamp: number;
  project_name: string;
  assets: Asset[];
}
```

---

## 🎬 Video Generation Pipeline

### End-to-End Flow

```
Input: Product Image + Prompt
  ↓
1. Visual DNA Extraction (Gemini Multimodal)
  ↓
2. Script Generation (GPT-4o / Gemini 2.0 Flash)
   - Hook: Attention-grabbing opener
   - Feature: Product benefit showcase
   - Lifestyle: Emotional connection
   - CTA: Call-to-action with end card
  ↓
3. Scene Generation (Parallel, 4 threads)
   For each scene:
     a. **[SMART RATE LIMITING]** Token Bucket check (only waits if quota full)
     b. Generate prompt with DNA injection
     c. Call MediaFactory (Veo 3.1 primary)
     d. On failure → Backup model (Veo 2.0)
     e. On failure → Ken Burns (guaranteed success)
     f. Upload to Firebase Storage
  ↓
4. Voice Generation (ElevenLabs)
   - Skip if native audio detected (Veo)
   - Fallback: Google TTS
  ↓
5. Music Composition (ElevenLabs Music API)
   - Genre: Based on mood (Upbeat/Relaxed/Professional/Dark)
   - Duration: Match video length (~20s loopable)
  ↓
6. Assembly (FFmpeg + MoviePy v2)
   - **Aspect Ratio Normalization**: All clips scaled/cropped to 1080x1920 (9:16)
   - Concatenate scenes (no letterboxing/black padding)
   - Audio ducking (BGM -6dB when voice present)
   - Watermark overlay (text + logo)
   - Export: 1080x1920, 24fps, H.264, 8Mbps
  ↓
Output: Final MP4 + Assets ZIP (Native 9:16, Zero Manual Editing Required)
```

### Rate Limiting & Throttling

**Token Bucket Algorithm** for optimal throughput:

```python
# Smart rate limiting - only waits when necessary
rate_limiter.check_and_wait("veo-3.1-fast-generate-preview")

# Algorithm:
# 1. Track requests in rolling 60-second window
# 2. If under RPM limit (2 requests) → proceed instantly ✅
# 3. If at RPM limit → wait until oldest request expires
# 4. Check daily limit (10 RPD) → fail if exceeded

# Example (2 RPM limit):
# Request 1 at 10:00:00 → instant (0s wait)
# Request 2 at 10:00:10 → instant (0s wait)
# Request 3 at 10:00:20 → waits 41s (until 10:01:01)
# Request 4 at 10:01:05 → instant (slot available)
```

**Per-User Cooldown** (2 minutes between generations):
```python
if time_since_last_gen(user_id) < 120:
    raise HTTPException(429, f"Wait {remaining}s")
```

**Global Throttle** (30 seconds between ANY user's generation):
```python
if time_since_last_global_gen() < 30:
    raise HTTPException(429, f"System busy, wait {remaining}s")
```

**State Persistence**: All rate limit state saved to `/tmp/rate_limit_state.json` and `/tmp/throttle_state.json` across server restarts.

---

## 🔧 Technical Stack

### Backend
- **Framework**: FastAPI 0.104+ (async/await, WebSockets)
- **Orchestration**: LangGraph (StateGraph for workflow)
- **Video Processing**: MoviePy 2.0, FFmpeg
- **Database**: Firebase Firestore
- **Storage**: Firebase Storage
- **Authentication**: Firebase Auth (JWT tokens)

### Frontend
- **Framework**: Angular 17 (standalone components)
- **State**: RxJS observables
- **UI**: Custom glassmorphic design system
- **Real-time**: WebSocket streaming from backend

### AI Models
| Task | Primary | Backup | Fallback |
|------|---------|--------|----------|
| Video | Veo 3.1 Fast | Veo 2.0 | Ken Burns |
| Image | Imagen 4.0 | DALL-E 3 | Stable Diffusion |
| Script | Gemini 2.0 Flash | GPT-4o | - |
| Voice | ElevenLabs | Google TTS | - |
| Music | ElevenLabs Music | - | - |

---

## 📡 API Reference

### Core Endpoints

#### Generate Video
```http
POST /api/generate
Content-Type: application/json
Authorization: Bearer {firebase_token}

Request:
{
  "prompt": "Sell wireless earbuds to fitness enthusiasts",
  "product_image_path": "tmp/run_123/product.png",
  "config": {
    "duration": 15,
    "aspect_ratio": "9:16",
    "music_mood": "Upbeat & Energetic",
    "video_model": "veo-3.1-fast-generate-preview",
    "watermark_enabled": true
  }
}

Response:
{
  "run_id": "run_1735123456",
  "status": "queued",
  "message": "Success! 10 credits deducted. Generation started."
}
```

#### Regenerate Scene
```http
POST /api/regenerate-scene/{run_id}/{scene_id}
Authorization: Bearer {firebase_token}

Response:
{
  "status": "started",
  "message": "Regenerating Lifestyle. 2 credits deducted."
}
```

#### Check Status
```http
GET /api/status/{run_id}

Response:
{
  "status": "running",
  "progress": 60,
  "current_stage": "assembly",
  "remote_assets": {
    "Hook_video": "https://storage.googleapis.com/...",
    "final_video": "https://storage.googleapis.com/..."
  },
  "cost_usd": 0.45
}
```

---

## 🛡️ Fault Tolerance & Reliability

### Guaranteed Success Architecture

Every operation has multiple fallback layers:

```python
def generate_scene(scene_data, visual_dna, config):
    try:
        # Primary: Veo 3.1
        return veo_3_1_generate(...)
    except VeoAPIError:
        try:
            # Backup: Veo 2.0
            return veo_2_0_generate(...)
        except VeoAPIError:
            # Fallback: Ken Burns (always succeeds)
            return ken_burns_effect(base_image)
```

**Result**: 100% success rate. No generation ever fails completely.

### Error Handling

- **API Timeouts**: Exponential backoff (1s, 2s, 4s)
- **Rate Limits**: Automatic queue with wait notifications
- **Invalid Inputs**: Validation before credit deduction
- **Model Failures**: Cascade to backup models
- **Storage Failures**: Retry up to 3 times with increasing delays

---

## 💰 Cost Structure

### Credits System
- **Generation**: 10 credits (full video)
- **Regeneration**: 2 credits (single scene)
- **Admin bypass**: Free generations for admin users

### Pricing Tiers
```python
PRICING_TIERS = {
    "free_trial": {"credits": 30, "price_usd": 0},
    "starter": {"credits": 100, "price_usd": 49},
    "growth": {"credits": 500, "price_usd": 149},
    "business": {"credits": 2000, "price_usd": 499}
}
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# System dependencies
- Python 3.10+
- Node.js 18+
- FFmpeg 6.0+
- Docker (for HF deployment)

# API Keys (set in .env)
- GEMINI_API_KEY
- OPENAI_API_KEY
- ELEVENLABS_API_KEY
- ELEVENLABS_API_KEY (required for voice + music)
```

### Local Development
```bash
# 1. Clone repository
git clone https://github.com/indieNik/AI-UGC-Ad-Video-Builder.git
cd AI-UGC-Ad-Video-Builder

# 2. Backend setup
cd projects/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 3. Frontend setup (new terminal)
cd projects/frontend
npm install
npm start  # Runs on http://localhost:4200

# 4. Access application
# Navigate to http://localhost:4200
# Backend API docs: http://localhost:8000/docs
```

### Production Deployment

#### Hugging Face Spaces
```bash
# Requires Dockerfile (already configured)
git push huggingface main
# Space auto-builds and deploys
```

#### Docker
```bash
docker build -t igniteai .
docker run -p 8000:8000 --env-file .env igniteai
```

---

## 📊 Performance Metrics

### Generation Times (Average)
- Script Generation: 8-12 seconds
- Visual DNA Extraction: 3-5 seconds
- **Smart Rate Limiting**: 0-45 seconds per scene (only waits when quota full)
- Scene Generation (per scene): 30-60 seconds (Veo), 2-3 seconds (Ken Burns)
- Voice Generation: 5-10 seconds
- Music Composition: 20-30 seconds
- Assembly: 10-15 seconds

**Total**: 3-5 minutes for 15-second video (4 scenes)
- *Uses Token Bucket algorithm - first 2 requests instant, subsequent requests wait only when necessary*

### Resource Usage
- CPU: 2-4 cores recommended
- RAM: 4GB minimum, 8GB recommended
- Disk: 10GB+ (for temp files, can be cleaned)
- Network: High bandwidth (video uploads/downloads)

---

## 🔐 Security

### Authentication
- Firebase JWT tokens for all API calls
- Admin role system (bypass credits, manage users)
- Rate limiting per user (2-minute cooldown)

### Data Protection
- Product images: Temporary storage, deleted after 24 hours
- User credentials: Never stored locally
- API keys: Environment variables only (never committed)

### Best Practices
- **Never commit**: `.env`, `credentials.json`, `token.json`
- **Never commit**: PDFs, large images (>500KB)
- See `GIT_BEST_PRACTICES.md` for full guidelines

---

## 🧪 Testing

### Run Tests
```bash
# Assembly fixes
python3 tests/test_assembly_fixes.py

# Rate limiter
python3 test_rate_limiter.py

# Model verification
python3 tests/verify_models.py
```

### Manual Testing Workflow
1. Upload product image
2. Set configuration (duration, mood, etc.)
3. Generate video (monitor logs)
4. Verify watermark placement
5. Test scene regeneration
6. Check credit deduction

---

## 📚 Documentation

- **[Git Best Practices](GIT_BEST_PRACTICES.md)**: Binary file warnings, cleanup guides
- **[Decks Regeneration](DECKS_REGENERATION.md)**: How to regenerate investor/tech decks
- **[Usage & Pricing](USAGE_AND_PRICING.md)**: Credit system, pricing tiers

---

## 🏛️ Project Structure

```
AI-UGC-Ad-Video-Builder/
├── api/
│   └── index.py                 # HF Spaces entry point
├── execution/
│   ├── workflow.py              # LangGraph orchestration
│   ├── scene_generation.py      # Scene + end card generation
│   ├── assembly.py              # Video assembly (FFmpeg + MoviePy)
│   ├── visual_dna.py            # Consistency engine
│   ├── script_generation.py     # Script creation
│   ├── voice_generation.py      # ElevenLabs integration
│   └── media_factory.py         # Unified model interface
├── projects/
│   ├── backend/
│   │   ├── main.py              # FastAPI app
│   │   ├── routers/             # API endpoints
│   │   │   ├── generation.py   # Generation, regeneration
│   │   │   ├── admin.py         # Admin dashboard
│   │   │   ├── payments.py     # Razorpay integration
│   │   │   └── brand.py         # Brand presets
│   │   └── services/
│   │       ├── db_service.py            # Firestore
│   │       ├── storage_service.py       # Firebase Storage
│   │       ├── rate_limiter.py          # Per-model limits
│   │       └── throttling_service.py    # User cooldowns
│   └── frontend/
│       └── src/
│           ├── app/
│           │   ├── pages/
│           │   │   ├── editor/          # Main editor UI
│           │   │   ├── projects/        # Project library
│           │   │   └── landing-page/    # Public homepage
│           │   └── services/
│           │       ├── api.service.ts   # Backend communication
│           │       └── auth.service.ts  # Firebase Auth
│           └── styles.css               # Glassmorphic design
├── tests/                       # Test suite
├── Dockerfile                   # HF Spaces container
├── requirements.txt             # Python dependencies
└── .env.example                 # Environment template
```

---

## 🤝 Contributing

This is a production system. For contributions:
1. Follow existing code structure
2. Add tests for new features
3. Never commit binary files (see `GIT_BEST_PRACTICES.md`)
4. Maintain backward compatibility
5. Document API changes


---

## 🔄 Recent Updates (January 2026)

### v1.5.2 - Public Editor & Guest Interaction
**Released:** January 21, 2026

#### 🚀 Public Editor Experience
- **Open Access**: Extracted `/editor` as a public route, allowing instant access to the creator tool for all visitors.
- **Guest Shield**: Implemented a "Unlock Creator Studio" modal that gently guides guest users to sign in only when they attempt to interact.
- **Improved UX**: Removed forced redirects, providing a "try before you buy" feel to the landing experience.
- **Security**: Hardened backend endpoints (generate, download, regenerate) to strictly verify auth tokens, preventing client-side bypasses.

### v1.2.26 - Community & Mobile Overhaul
**Released:** January 15, 2026

#### 🎨 Community Features
- **Liked Videos Tab**: Users can now filter and view their favorite community videos
- **View Counting**: Real-time view tracking on video hover/play
- **Enhanced Metadata**: Fixed timestamp display bugs ("-20,000 days ago" → accurate dates)
- **User Experience**: "Anonymous" creators now show as "Community Member" for better UX
- **Square Grid**: Enforced 1:1 aspect ratio for a premium, Instagram-like feed

#### 📱 Mobile Responsiveness
- **Critical Fix**: Resolved desktop grid layout crushing mobile content
- **Off-Canvas Sidebar**: Implemented smooth slide-in navigation for mobile devices
- **Responsive Grids**: Video grids now adapt to full-width on small screens (<480px)
- **Touch Optimization**: Improved hamburger menu and backdrop interactions

#### 🔧 Technical Improvements
- **Data Flow Alignment**: Fixed frontend/backend collection mismatch (executions vs community)
- **WebChannel Transparency**: Added console logging for "invisible" Firestore API calls
- **Timestamp Standardization**: Unified Python (Seconds) and JS (Milliseconds) formats
- **Read-After-Write Verification**: Explicit validation for critical operations

**Architecture Patterns Established:**
- Read-After-Write verification for data persistence
- WebChannel transparency via `[IgniteAI]` console logs
- Mobile-First Grid (1fr base, fixed columns only for desktop)
- Off-Canvas Sidebar pattern for mobile navigation

---

## 🎯 Roadmap


- [ ] Multi-language support (Spanish, Hindi)
- [ ] Advanced A/B testing (generate variants)
- [ ] Voice cloning (custom brand voices)
- [ ] Sora integration (when API available)
- [ ] Batch generation (multiple products)

---

## 📄 License

Proprietary. All rights reserved.

---

**IgniteAI: Creativity as Structure.**

Built with ❤️ by the IgniteAI team.

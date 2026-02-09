# Pipeline Reliability & User Value Protection PRD

**Document Owner:** Engineering Team  
**Date:** February 7, 2026  
**Status:** Approved for Implementation  
**Priority:** P0 - Critical  
**Target Release:** v1.6.0

---

## Executive Summary

**Problem:** Production analysis of run `run_1770457296` revealed that the system can succeed technically while delivering zero commercial value. A user paid 10 credits (~$4) for a video with generic fallback content, 75% Ken Burns static animations, and no brand-specific messaging, despite the system reporting "success."

**Impact:**
- Customer trust erosion
- High refund/chargeback risk
- Negative brand perception
- Revenue loss from churned users

**Goal:** Implement "fail fast with grace" architecture where users either receive high-quality output OR immediate transparent failure with full credit refund.

**Philosophy:** *"No video is better than a bad video that wastes user money."*

---

## Background & Context

### Current Architecture Issues

1. **Silent Degradation:** System falls back to generic content when core services fail, without user notification
2. **Empty State Propagation:** Failed Visual DNA extraction cascades through entire pipeline, producing worthless output
3. **Pre-payment Risk:** Credits deducted before validation, exposing users to failed generations
4. **Celebrity Filter Blind Spot:** Images rejected by Veo safety filters after payment
5. **Fallback != Value:** Ken Burns static animations charged at same rate as Veo video generation

### Incident Details

**Run ID:** `run_1770457296`  
**User Product:** OverSight (Executive dashboard)  
**Credits Charged:** 10 ($4.00)  
**Value Delivered:** ~$0 (generic fallback video)

**Failure Cascade:**
```
Visual DNA extraction failed (gemini-2.0-flash-exp model not found)
  ↓
Script generation failed (same model error)
  ↓
Generic fallback scenes used ("Product shot in bright light")
  ↓
Celebrity filter rejected 3/4 scenes (face detected in input)
  ↓
75% Ken Burns fallback (static pan/zoom)
  ↓
Voice casting failed (same model error, default voice used)
  ↓
Final output: Generic video with no OverSight branding
```

---

## Success Metrics

### User-Facing Metrics
- **Credit Waste Rate:** < 5% (credits charged for failed/low-quality generations)
- **Refund Request Rate:** < 2%
- **User Satisfaction (CSAT):** > 85% for generation quality
- **Retry Rate:** < 15% (users regenerating due to quality issues)

### System Metrics
- **Pipeline Success Rate:** > 95% (full quality, no fallbacks)
- **Graceful Failure Rate:** 100% (users notified + refunded when quality degraded)
- **Celebrity Filter Pre-Detection:** > 90% (warn before generation)
- **Mean Time to User Notification:** < 5 seconds (for failures)

---

## Requirements

### 1. Graceful Pipeline Failure (P0)

**User Story:**  
As a user, when Visual DNA extraction fails, I should be immediately notified and refunded, not receive a generic worthless video.

**Acceptance Criteria:**
- [ ] System detects Visual DNA extraction failure
- [ ] Credits immediately refunded (within 1 second)
- [ ] User receives clear error message via WebSocket
- [ ] Error message includes actionable guidance:
  - "Try a different product image"
  - "Ensure image is high quality (>512x512)"
  - "Contact support if issue persists"
- [ ] Run marked as `failed` in Firestore with reason

**Technical Specification:**
```python
def extract_dna_node(state: AgentState):
    try:
        dna = extract_visual_dna(state["input_data"], ...)
        
        # Validate DNA has required fields
        if not dna or not dna.get("character") or not dna.get("product"):
            raise PipelineFailure("Visual DNA extraction incomplete")
            
        return {"visual_dna": dna}
        
    except Exception as e:
        # Immediate refund
        user_id = state.get("user_id")
        run_id = state.get("run_id")
        credits_charged = state.get("credits_charged", 10)
        
        db_service.refund_credits(user_id, credits_charged)
        db_service.save_run(run_id, user_id, "failed", error={
            "stage": "visual_dna",
            "reason": str(e),
            "refunded": True
        })
        
        # Notify user via WebSocket
        emit_websocket_event(run_id, {
            "status": "failed",
            "stage": "visual_dna",
            "message": "❌ Failed to analyze product image. Credits refunded.",
            "guidance": [
                "Try uploading a clearer image",
                "Ensure image shows your product clearly",
                "Contact support if this persists"
            ]
        })
        
        raise PipelineFailure("DNA extraction failed - user refunded")
```

---

### 2. Quality Degradation Transparency (P0)

**User Story:**  
As a user, when my video uses Ken Burns fallback instead of Veo, I should be notified and offered options (accept/retry/refund).

**Acceptance Criteria:**
- [ ] System tracks fallback usage per scene
- [ ] User notified when >50% scenes use Ken Burns
- [ ] Notification includes quality comparison:
  - "3 out of 4 scenes used static images instead of video"
  - "This is due to API rate limits / safety filters"
- [ ] User presented with options:
  - Accept video (no refund)
  - Retry with different settings (free retry)
  - Full refund
- [ ] User choice recorded in run history

**Frontend Modal Design:**
```typescript
interface QualityDegradationModal {
  title: "⚠️ Video Quality Reduced"
  message: string  // "3 of 4 scenes degraded to static images"
  breakdown: {
    scene_id: string
    expected: "veo-3.1-video"
    actual: "ken-burns-static"
    reason: "Celebrity detected in image"
  }[]
  options: [
    { label: "Accept This Version", action: "keep", credits: 0 },
    { label: "Retry with Different Image", action: "retry", credits: 0 },
    { label: "Get Full Refund", action: "refund", credits: +10 }
  ]
}
```

---

### 3. Pre-Flight Image Analysis (P0)

**User Story:**  
As a user, before I pay credits, I should be warned if my image will likely be rejected by Veo's safety filters.

**Acceptance Criteria:**
- [ ] Face detection runs before credit deduction
- [ ] Warning shown if faces detected:
  - "⚠️ This image contains faces and may be rejected"
  - "Recommendation: Use product-only image for best results"
- [ ] User can override with "Proceed Anyway" button
- [ ] Warning acknowledged status stored for audit trail
- [ ] No credit deduction until user confirms

**Technical Specification:**
```python
def pre_flight_image_check(image_path: str) -> dict:
    """
    Run before credit deduction to detect potential Veo rejections.
    """
    warnings = []
    recommendations = []
    
    # Face detection
    face_count = detect_faces_cv2(image_path)
    if face_count > 0:
        warnings.append({
            "severity": "high",
            "code": "FACES_DETECTED",
            "message": f"{face_count} face(s) detected. Veo may reject this image.",
            "recommendation": "Use product-only image or illustration"
        })
    
    # Image quality check
    img = Image.open(image_path)
    if img.width < 512 or img.height < 512:
        warnings.append({
            "severity": "medium",
            "code": "LOW_RESOLUTION",
            "message": "Image resolution is low (<512px)",
            "recommendation": "Upload higher resolution image for better quality"
        })
    
    return {
        "safe_to_proceed": len([w for w in warnings if w["severity"] == "high"]) == 0,
        "warnings": warnings,
        "user_confirmation_required": len(warnings) > 0
    }
```

---

### 4. Smart Fallback Script Generation (P1)

**User Story:**  
As a user, when Gemini script generation fails, the system should retry with a backup model (GPT-4o), not use generic fallback scenes.

**Acceptance Criteria:**
- [ ] Primary: Gemini 2.5 Flash
- [ ] Backup: GPT-4o Mini (cheaper, more reliable)
- [ ] Fallback: GPT-3.5 Turbo (last resort)
- [ ] Only use generic scenes if all models fail
- [ ] If all fail → refund user (don't proceed with garbage)

**Technical Specification:**
```python
def generate_script_node(state: AgentState):
    models = [
        ("gemini-2.5-flash", "primary"),
        ("gpt-4o-mini", "backup"),
        ("gpt-3.5-turbo", "fallback")
    ]
    
    for model, tier in models:
        try:
            script_data = generate_script_with_model(
                model, 
                state["input_data"], 
                state["visual_dna"]
            )
            
            # Validate quality
            if validate_script_quality(script_data):
                return {
                    "script": script_data["script"],
                    "scenes_list": script_data["scenes"],
                    "model_used": model,
                    "tier": tier
                }
        except Exception as e:
            logger.warning(f"Script gen failed with {model}: {e}")
            continue
    
    # All models failed - refund and fail
    raise PipelineFailure("All script generation models failed")
```

---

### 5. User-Friendly Rate Limit Messages (P1)

**User Story:**  
As a user waiting for video generation, I should see clear progress updates, not technical API jargon.

**Acceptance Criteria:**
- [ ] WebSocket messages use plain language
- [ ] Technical details hidden in collapsible "Debug Info" section
- [ ] Progress bar shows estimated time remaining
- [ ] Messages explain WHY there's a wait:
  - "⏳ High demand - your video is queued (30s)"
  - "🎬 Generating scene 2 of 4..."
  - "✓ Scene 3 complete - assembling final video..."

**Before:**
```
⏳ Rate Limit (RPM): Waiting 58.9s for veo-3.1-fast-generate-preview slot...
```

**After:**
```
⏳ System busy - your video is in queue
   Estimated wait: 59 seconds
   Status: Waiting for video generation slot
   
   [Show technical details ▼]
   API: veo-3.1-fast-generate-preview
   Rate limit: 2 requests/minute
   Queue position: 3rd
```

---

### 6. Regeneration Pipeline Fix (P1)

**User Story:**  
As a user regenerating a scene, I should get a fresh attempt with working DNA/script, not re-render of broken pipeline state.

**Acceptance Criteria:**
- [ ] Regeneration checks if Visual DNA is valid
- [ ] If DNA is empty/broken → re-extract DNA first
- [ ] If script is generic → re-generate script with user prompt
- [ ] THEN regenerate the scene with fresh context
- [ ] User informed of "deep regeneration" if needed

**Technical Specification:**
```python
def regenerate_scene(run_id: str, scene_id: str, user_id: str):
    # Load existing state
    state = db.get_run_state(run_id)
    
    # Validate DNA quality
    dna = state.get("visual_dna", {})
    if not dna or not dna.get("character"):
        logger.info(f"DNA invalid for {run_id}, re-extracting...")
        dna = extract_visual_dna(
            state["input_data"],
            state.get("product_image_path")
        )
        state["visual_dna"] = dna
        db.update_run_state(run_id, {"visual_dna": dna})
    
    # Validate script quality
    script = state.get("script", "")
    if "Fallback" in script or not script:
        logger.info(f"Script invalid for {run_id}, re-generating...")
        script_data = generate_script_and_shots(
            state["input_data"],
            dna,
            config=state["config"]
        )
        state["script"] = script_data["script"]
        state["scenes_list"] = script_data["scenes"]
        db.update_run_state(run_id, {
            "script": script_data["script"],
            "scenes_list": script_data["scenes"]
        })
    
    # NOW regenerate scene with fresh context
    scene = next(s for s in state["scenes_list"] if s["id"] == scene_id)
    new_video = generate_scene(scene, dna, config=state["config"])
    
    return {"status": "success", "video_url": new_video}
```

---

## Implementation Plan

### Phase 1: Critical Fixes (Week 1)
- [ ] Implement graceful pipeline failure (Req #1)
- [ ] Add pre-flight image analysis (Req #3)
- [ ] Update all LLM references from `gemini-2.0-flash-exp` to `gemini-2.5-flash`
- [ ] Add Visual DNA validation gates

**Deliverables:**
- No more empty DNA propagation
- Users warned about problematic images before payment
- Failed runs refunded automatically

### Phase 2: Transparency (Week 2)
- [ ] Quality degradation modal (Req #2)
- [ ] User-friendly WebSocket messages (Req #5)
- [ ] Fallback usage tracking in Firestore

**Deliverables:**
- Users see clear explanations for degraded quality
- Accept/retry/refund options available
- Progress messages in plain language

### Phase 3: Intelligent Fallbacks (Week 3)
- [ ] Multi-model script generation (Req #4)
- [ ] Regeneration pipeline fix (Req #6)
- [ ] Cost tracking per fallback tier

**Deliverables:**
- Backup models prevent generic fallback usage
- Regeneration re-runs broken pipeline stages
- Accurate cost attribution

---

## Technical Dependencies

### New Services Required
1. **Face Detection Service**
   - Library: OpenCV (`cv2.CascadeClassifier`)
   - Model: Haar Cascade frontal face detection
   - Latency: <500ms for 1080p image

2. **Pipeline Health Monitor**
   - Track: DNA quality, script quality, fallback usage
   - Alert: When degradation >30% for any user
   - Dashboard: Real-time pipeline health metrics

3. **Credit Refund Service**
   - Atomic operation: Deduct → Validate → Refund on failure
   - Idempotent: Prevent double refunds
   - Audit trail: All credit movements logged

### API Model Updates
- Primary LLM: `gemini/gemini-2.5-flash` (not `gemini-2.0-flash-exp`)
- Image Gen: `gemini-2.5-flash-image` ($0.039/image)
- Video Gen: `veo-3.1-fast-generate-preview` ($0.15/second)
- Music Gen: **ElevenLabs Music** (not Suno AI)
- Voice Gen: ElevenLabs TTS

---

## Cost Impact Analysis

### Current State (Bad Output)
- COGS per failed run: $1.45
- User pays: $4.00
- Margin: 64%
- **Business value: $0** (user churns)

### After Fix (Refund Failed Runs)
- Failed runs: Refunded (COGS absorbed)
- Successful runs: $4.11 COGS, $4.00 revenue
- Margin on success: -3% (acceptable, user retains trust)
- **Business value: High** (user retains, refers others)

### Expected Failure Rate
- Current: ~20% silent failures
- After fix: ~5% graceful failures (refunded)
- Revenue impact: -$0.80 per failed run (better than churn)

---

## User Education & Documentation

### Update Required Documents
1. `README.md`
   - Remove Suno AI references
   - Add ElevenLabs Music generation
   - Update model names (gemini-2.5-flash)
   
2. `USAGE_AND_PRICING.md`
   - Clarify Ken Burns fallback pricing
   - Add "Quality Guarantee" section
   - Document refund policy

3. New: `QUALITY_STANDARDS.md`
   - Define what constitutes "success"
   - Document fallback behavior
   - Explain refund triggers

### Frontend Help Text
```typescript
const qualityStandards = {
  title: "Our Quality Guarantee",
  points: [
    "✓ Your video will match your brand and product",
    "✓ Professional video generation (not static images)",
    "✓ Custom script based on your description",
    "✓ If we can't deliver quality, you get a full refund"
  ],
  fallbackExplanation: `
    Sometimes API limits require us to use static image animations. 
    If >50% of your video uses static animations, you'll be offered:
    - Accept the video as-is (no charge)
    - Retry with different settings (free)
    - Full credit refund
  `
}
```

---

## Monitoring & Alerting

### Key Metrics Dashboard
```
Pipeline Health Dashboard
├─ Visual DNA Success Rate: 95% ✓
├─ Script Generation Success Rate: 92% ⚠️
├─ Veo Acceptance Rate: 78% ⚠️
├─ Ken Burns Fallback %: 22%
├─ User Refund Rate: 3% ✓
└─ Average COGS per Run: $3.20
```

### Alerts
- **P0:** DNA success rate < 90% (pipeline broken)
- **P1:** Veo acceptance rate < 70% (celebrity filter spike)
- **P2:** Refund rate > 5% (quality issues)

---

## Success Criteria

### Definition of Done
- [ ] All P0 requirements implemented
- [ ] User receives transparent failure notifications
- [ ] Credits auto-refunded for failed/degraded runs
- [ ] Pre-flight checks prevent 80%+ of celebrity filter rejections
- [ ] WebSocket messages are user-friendly (no technical jargon)
- [ ] Test coverage > 85% for refund logic
- [ ] Documentation updated (README, pricing, quality standards)

### Launch Checklist
- [ ] Feature flag: `ENABLE_GRACEFUL_FAILURES` (default: true)
- [ ] Monitoring dashboard live
- [ ] Alerts configured in Slack/PagerDuty
- [ ] User support team trained on new refund policy
- [ ] A/B test: 10% of users see new flow for 1 week
- [ ] Rollout to 100% if metrics improve

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Higher refund rate initially | Revenue loss | Medium | Monitor closely, tune thresholds |
| Face detection false positives | User friction | Low | Allow override with warning |
| Multi-model script gen adds latency | Poor UX | Low | Parallel execution, 5s timeout per model |
| Users exploit refund system | Revenue loss | Very Low | Rate limit refunds (max 3/week/user) |

---

## Appendix: Production Run Log Details

**Full incident analysis:** See `production_run_analysis.md`

**Key Takeaways:**
1. System succeeded technically but failed commercially
2. Empty state propagation created worthless output
3. No user notification of quality degradation
4. Credits charged despite delivering zero value

**Never Again:** With this PRD implemented, similar incidents will result in immediate user notification and full refund, preserving trust and brand reputation.

---

**Version:** 1.0  
**Last Updated:** February 7, 2026  
**Next Review:** Post-implementation (March 1, 2026)

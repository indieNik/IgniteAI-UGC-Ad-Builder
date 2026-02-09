# Credit System Deep Dive Analysis

**Date:** January 23, 2026  
**Analyst:** CTO + CEO Review  
**Purpose:** Clarify credit-to-video ratio and validate pricing fairness

---

## 🔍 Current Implementation Reality

### What Happens When User Clicks "Generate"

**From `generation.py` Line 453:**
```python
COST_PER_GEN = 10  # Credits deducted per generation
```

**From `workflow.py` (execution flow):**
1. **Extract Visual DNA** (brand colors, style, character)
2. **Generate Script** → Creates 3-4 **scenes** based on duration
3. **Generate Scenes** → Loops through each scene, generates:
   - Image (static frame) using Imagen 4
   - Video (5-6 seconds) using Veo 3.1
4. **Generate Voiceover** → One voiceover for entire campaign
5. **Assembly** → Stitches all scenes + voiceover + BGM into **ONE final video**

---

## 📊 The Truth: What 10 Credits Actually Buys

### Output: **ONE Multi-Scene Campaign Video**

**Typical 15-second video structure:**
- **Scene 1 (Hook):** 5 seconds - Product intro
- **Scene 2 (Feature):** 5 seconds - Product in use  
- **Scene 3 (Lifestyle):** 3 seconds - Lifestyle shot
- **Scene 4 (CTA):** 2 seconds - Call to action
- **+ End Card:** Static image with CTA text

**Total:** 4 individual scene videos → Assembled into **1 final campaign video**

---

## 💰 Cost Breakdown Per "Generation"

**From USAGE_AND_PRICING.md + Workflow Analysis:**

| Component | Quantity | Unit Cost | Total |
|-----------|----------|-----------|-------|
| **Video clips** | 4 scenes × 6s each = 24s | $0.15/sec (Veo 3.1) | $3.60 |
| **Images** | 5 images (4 scenes + end card) | $0.04/image (Imagen 4) | $0.20 |
| **Voiceover** | ~100 words (~500 chars) | $0.30/1k chars | $0.15 |
| **Script (LLM)** | ~5k tokens | $0.50/1M tokens | <$0.01 |
| **TOTAL COGS** | - | - | **$3.96** |

**Credits Charged:** 10  
**Credit Value:** $3.96 ÷ 10 = **$0.396 per credit**

---

## ⚠️ The Confusion: "Video" vs "Scene" vs "Campaign"

### Terminology Clarity

| Term | What It Means | Count |
|------|---------------|-------|
| **Scene** | Individual 5s video clip (Hook, Feature, CTA) | 3-4 per campaign |
| **Campaign** | Full assembled 15s video with all scenes | 1 per generation |
| **Generation** | One complete workflow (Script → Scenes → Assembly) | 10 credits |

**User Mental Model:**
- "I clicked generate → I got 1 campaign video → Cost: 10 credits"

**Actual Output:**
- 4 individual scene video files (Hook.mp4, Feature.mp4, Lifestyle.mp4, CTA.mp4)
- 1 final assembled video (campaign.mp4)
- 4 static images (one per scene)
- 1 end card image
- 1 voiceover audio file

---

## 🤔 Is The Current Pricing Fair?

### Scenario Analysis

**Free User (10 Credits):**
- Gets: **1 complete campaign** (4 scenes assembled into 15s video)
- COGS: $3.96
- Company loss: $3.96 ✅ (Acceptable CAC)

**Starter Pack User ($99 / 50 credits):**
- Gets: **5 complete campaigns** (5 × 15s videos)
- COGS: $19.80
- Revenue: $99
- Margin: **80%** ✅ (Very healthy!)

**Creator Pack User ($239 / 150 credits):**
- Gets: **15 complete campaigns** (15 × 15s videos)
- COGS: $59.40
- Revenue: $239
- Margin: **75%** ✅ (Sustainable)

---

## 🔄 Scene Regeneration Logic

**From `generation.py` Line 733:**
```python
REGEN_COST = 2  # Credits per scene regeneration
```

**What Happens:**
1. User dislikes "Feature" scene in their campaign
2. Clicks "Regenerate Feature Scene"
3. System:
   - Charges **2 credits**
   - Regenerates ONLY the Feature scene (~5s video)
   - Keeps Hook, Lifestyle, CTA unchanged
   - Re-assembles final video with new Feature scene

**COGS for Regeneration:**
- Video: 6s × $0.15 = $0.90
- Image: $0.04 (if regenerated)
- **Total:** ~$0.94

**Credits Charged:** 2  
**Credit Value:** $0.94 ÷ 2 = **$0.47 per credit**

**Margin:** ($0.396 × 2 - $0.94) / ($0.396 × 2) = **-19%** ⚠️

> [!WARNING]
> **Regeneration is UNPROFITABLE at 2 credits!** Should be 3-4 credits to break even.

---

## 💡 Recommendations

### Option 1: Keep Current Model (Campaign-Based)
**Pros:**
- Simple: "10 credits = 1 video campaign"
- Encourages iteration (users get 4 scenes to test)
- Premium feel (not nickel-and-diming per scene)

**Cons:**
- Scene regeneration loses money (2 credits vs $0.94 COGS)
- Doesn't scale if users want longer videos (7+ scenes)

**Fix:** Increase regen cost to **3 credits** (50% margin)

---

### Option 2: Per-Scene Pricing
**Structure:**
- **Scene Generation:** 2.5 credits each
- **Full Campaign (4 scenes):** Still 10 credits (no change)
- **Scene Regeneration:** 2.5 credits (profitable)

**Pros:**
- Fair: Pay more for longer videos (7 scenes = 17.5 credits)
- Regeneration becomes profitable
- Scales better for future features

**Cons:**
- More complex to explain
- Nickels-and-dimes feel
- Requires UI changes ("This campaign will cost 12.5 credits")

---

### Option 3: Hybrid (Recommended)

**Tiered Campaign Pricing:**
- **Short Video (10-15s, 3-4 scenes):** 10 credits
- **Medium Video (20-30s, 5-7 scenes):** 15 credits
- **Long Video (30-45s, 8-10 scenes):** 25 credits

**Scene Regeneration:** 3 credits (fixed, regardless of campaign tier)

**Pros:**
- ✅ Simple tiers (easy to understand)
- ✅ Profitable on both campaigns and regenerations
- ✅ Scales for future long-form content
- ✅ Encourages users to buy larger credit packs

**Cons:**
- Requires frontend UI to show credit cost before generate
- Current users only see one tier (10 credits)

---

## 📋 Revised Unit Economics (Hybrid Model)

### Campaign Generation

| Duration | Scenes | COGS | Credits | $/Credit | Margin |
|----------|--------|------|---------|----------|--------|
| 10-15s | 3-4 | $3.96 | 10 | $0.40 | **90%** (vs Starter $1.98/credit) |
| 20-30s | 5-7 | $7.92 | 15 | $0.53 | **89%** |
| 30-45s | 8-10 | $11.88 | 25 | $0.48 | **88%** |

### Scene Regeneration

| Action | COGS | Credits | $/Credit | Margin |
|--------|------|---------|----------|--------|
| Regen 1 Scene | $0.94 | 3 | $0.31 | **76%** (vs Starter $1.98/credit) |

---

## 🎯 Final Recommendation

### **Keep 10 Credits/Campaign, Fix Regeneration**

**Changes Needed:**
1. ✅ **Keep:** 10 credits per campaign (15s video, 3-4 scenes)
2. 🔄 **Change:** Scene regeneration from 2 → **3 credits**
3. 🆕 **Add (Future):** Longer video tiers (20s = 15 credits, 30s = 25 credits)

**Rationale:**
- Current users already understand "10 credits = 1 video"
- Regeneration fix is simple backend change (line 733 in generation.py)
- Future-proofs for long-form content expansion
- Maintains high margins (75-80%)

---

## 🔢 Corrected Pricing Strategy Metrics

**Free Tier (10 credits):**
- Output: **1 campaign video** (not "2-3 videos")
- COGS: $3.96
- Loss: -100% ✅ (CAC investment)

**Starter Pack ($99 / 50 credits):**
- Output: **5 campaign videos** (not "12 videos")
- COGS: $19.80
- Revenue: $99
- **Margin: 80%** ✅

**Creator Pack ($239 / 150 credits):**
- Output: **15 campaign videos** (not "37 videos")
- COGS: $59.40
- Revenue: $239
- **Margin: 75%** ✅

**Growth Pack ($599 / 500 credits):**
- Output: **50 campaign videos** (not "125 videos")
- COGS: $198
- Revenue: $599
- **Margin: 67%** ✅

**Scale Pack ($2,999 / 2,000 credits):**
- Output: **200 campaign videos** (not "500 videos")
- COGS: $792
- Revenue: $2,999
- **Margin: 74%** ✅

---

## ✅ Action Items

### Immediate (Week of Jan 23)
1. [ ] Update `generation.py` Line 733: `REGEN_COST = 3` (was 2)
2. [ ] Update all strategic docs with corrected video counts
3. [ ] Update marketing copy: "50 credits = 5 videos" (not 12)
4. [ ] Update pricing page feature descriptions

### Near-Term (Q1 2026)
1. [ ] Add "Credits Required" indicator on generate button
2. [ ] Add duration selector (10s/15s/20s/30s) with dynamic credit cost
3. [ ] Track actual scene counts per campaign (analytics)
4. [ ] A/B test longer video tiers (20s = 15 credits)

### Long-Term (Q2+ 2026)
1. [ ] Build "credit calculator" on pricing page
2. [ ] Add "scenes included" to credit pack descriptions
3. [ ] Consider per-scene a la carte option for power users

---

## 📝 Summary

**Current Reality:**
- **10 credits = 1 complete campaign video** (4 scenes assembled)
- **NOT:** 10 credits = 10 individual video clips
- **NOT:** 10 credits = 2-3 videos

**Pricing Fairness:**
- ✅ **YES, it's fair** (75-80% margins, still 90% cheaper than UGC creators)
- ⚠️ **BUT:** Scene regeneration at 2 credits is unprofitable (fix: 3 credits)

**Communication Gap:**
- Marketing materials incorrectly calculated "videos per pack"
- Assumed 4 credits/video when actual is 10 credits/campaign
- Need to update all docs with corrected output expectations

---

**Approved By:** CTO + CEO  
**Date:** January 23, 2026  
**Next Review:** After implementing regen cost fix

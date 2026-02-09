# 🚨 CRITICAL FLAW: Duration-Based Pricing Missing

**Discovered:** January 23, 2026  
**Severity:** 🔴 **CRITICAL** (2.25x COGS overrun potential)  
**Status:** ⏳ Pre-production (no active users affected)  
**Impact:** Could lose $1,970 extra per 1,000 users if unfixed

---

## Problem Statement

**Current System:**
- **10 credits = FIXED cost** for ANY video length
- User can select 15s, 30s, or 45s duration
- System generates 3-9 scenes based on duration
- **No price adjustment** based on scene count

**Example Exploit:**
```
Free user (10 credits):
- Selects "Premium Lifestyle" preset (30s, 6 scenes)
- COGS: $5.93 (vs expected $3.96 for 15s)
- Company loss: $5.93 (50% worse than budgeted)
```

---

## Root Cause Analysis

### Code Location: `projects/backend/routers/generation.py`

**Line 453:**
```python
COST_PER_GEN = 10  # FIXED - No duration consideration!
```

### Workflow Location: `execution/script_generation.py`

**Lines 23-45:**
```python
# Dynamic Scene Calculation
seconds = int(duration_str.replace("s", ""))
num_scenes = max(3, int(seconds // min_scene_duration))

if num_scenes == 3:
    current_ids = ["Hook", "Feature", "CTA"]
elif num_scenes == 4:
    current_ids = ["Hook", "Feature", "Lifestyle", "CTA"]
else:
    # 5+ scenes
    current_ids = ids[:num_scenes-1] + ["CTA"]
```

**The Gap:** Frontend allows duration selection, backend generates appropriate scenes, but **credit deduction ignores scene count**.

---

## Financial Impact

### COGS by Duration

| Duration | Scenes | Video (36s @ $0.15/s) | Images (7 @ $0.04) | Voice | **Total COGS** |
|----------|--------|----------------------|-------------------|-------|----------------|
| 15s | 4 | $3.60 | $0.20 | $0.15 | **$3.95** |
| 30s | 6 | $5.40 | $0.28 | $0.25 | **$5.93** (+50%) |
| 45s | 9 | $8.10 | $0.40 | $0.35 | **$8.85** (+124%) |

### At Scale (Per 1,000 Users)

**Scenario A: All users choose 15s (expected):**
- COGS: 1,000 × $3.95 = **$3,950**

**Scenario B: All users choose 45s (exploit):**
- COGS: 1,000 × $8.85 = **$8,850**
- **Extra loss:** $4,900 (124% overrun!)

**Realistic Mix (50% short, 30% medium, 20% long):**
- 500 × $3.95 = $1,975
- 300 × $5.93 = $1,779
- 200 × $8.85 = $1,770
- **Total:** $5,524 vs budgeted $3,950
- **Overrun:** $1,574 (40% higher COGS)

---

## Proposed Fix

### Tiered Credit Pricing

| Duration | Scenes | COGS | **New Credits** | Margin @ Starter ($1.98/credit) |
|----------|--------|------|-----------------|--------------------------------|
| **Short (10-15s)** | 3-4 | $3.95 | **10** | 80% ✅ |
| **Medium (20-25s)** | 5 | $4.95 | **13** | 68% ✅ |
| **Long (30-35s)** | 6-7 | $5.93 | **18** | 62% ✅ |
| **Extra Long (40-45s)** | 8-9 | $8.85 | **25** | 57% ✅ |

### Code Implementation

**File:** `projects/backend/routers/generation.py`

```python
def calculate_credit_cost(config: dict) -> int:
    """
    Calculate credits based on video duration.
    Longer videos = more scenes = higher COGS.
    """
    duration_str = config.get("target_duration", "15s")
    seconds = int(duration_str.replace("s", ""))
    
    if seconds <= 15:
        return 10  # Short (3-4 scenes)
    elif seconds <= 25:
        return 13  # Medium (5 scenes)
    elif seconds <= 35:
        return 18  # Long (6-7 scenes)
    else:
        return 25  # Extra Long (8-9 scenes)

# In trigger_generation (line 453):
# OLD: COST_PER_GEN = 10
# NEW:
COST_PER_GEN = calculate_credit_cost(request.config or {})
```

**File:** `projects/frontend/src/app/editor/editor.component.ts`

```typescript
// Add credit cost indicator
getCreditCost(duration: string): number {
  const seconds = parseInt(duration.replace('s', ''));
  if (seconds <= 15) return 10;
  if (seconds <= 25) return 13;
  if (seconds <= 35) return 18;
  return 25;
}

// In template (before generate button):
<div class="credit-cost-indicator">
  This will cost {{ getCreditCost(selectedDuration) }} credits
</div>
```

---

## Updated Pricing Tables

### Free Tier (10 credits)

**Before Fix:**
- 10-15s: 1 video ✅
- 30s: 1 video ❌ (loses $5.93)
- 45s: 1 video ❌❌ (loses $8.85)

**After Fix:**
- 10-15s: 1 video ✅
- 30s: Can't afford (need 18 credits)
- 45s: Can't afford (need 25 credits)

### Starter Pack ($99 / 50 credits)

**Before Fix:**
- 15s videos: 5 videos (COGS $19.75, margin 80%)
- 30s videos: 5 videos (COGS $29.65, margin 70%) ⚠️
- 45s videos: 5 videos (COGS $44.25, margin 55%) ⚠️⚠️

**After Fix:**
- 15s: 5 videos (50÷10) - COGS $19.75, margin 80%
- 30s: 2 videos (50÷18) - COGS $11.86, margin 88% ✅
- 45s: 2 videos (50÷25) - COGS $17.70, margin 82% ✅

### Creator Pack ($239 / 150 credits)

**Before Fix:**
- 15s: 15 videos, margin 75%
- 45s: 15 videos, margin 44% ⚠️

**After Fix:**
- 15s: 15 videos (150÷10), margin 75%
- 30s: 8 videos (150÷18), margin 80% ✅
- 45s: 6 videos (150÷25), margin 78% ✅

---

## Migration Strategy

### Existing Users (If Any)

**Grandfather Clause:**
- All users registered before Feb 1, 2026: Old pricing for 30 days
- Database flag: `legacy_flat_pricing_until: 2026-03-01`
- After expiry: Automatically switch to tiered pricing

**Communication Template:**
```
Subject: New Fair Pricing: Pay for What You Generate

Hi [Name],

Good news! We're introducing transparent, duration-based pricing:

SHORT videos (15s): 10 credits
MEDIUM videos (25s): 13 credits  
LONG videos (35s): 18 credits

Why? Longer videos require more AI processing (more scenes, more compute).

Your existing credits work exactly the same—just choose your duration!

As a thank you for being an early user, you have 30 days of old 
pricing (10 credits for any length). After March 1, new pricing applies.

Questions? Reply to this email.
```

---

## Testing Checklist

### Before Deployment

- [ ] Backend: Test `calculate_credit_cost()` function
- [ ] Backend: Verify credit check rejects insufficient balance
- [ ] Frontend: Display correct credit cost for each duration
- [ ] Frontend: Update "Generate" button with cost ("Generate - 18 credits")
- [ ] E2E: Generate 15s video → Deducts 10 credits
- [ ] E2E: Generate 30s video → Deducts 18 credits
- [ ] E2E: Generate 45s video → Deducts 25 credits
- [ ] E2E: User with 12 credits tries 30s → Error 402 "Insufficient credits"

### Edge Cases

- [ ] User edits duration mid-workflow → Cost updates dynamically
- [ ] Scene regeneration still costs 3 credits (fixed price)
- [ ] Admin bypass still works (free generation)
- [ ] Grandfather clause correctly identifies legacy users

---

## Success Metrics (Post-Fix)

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Avg COGS/credit | $0.40 | $0.31-0.35 | <$0.40 ✅ |
| COGS variance | ±150% | ±10% | <20% ✅ |
| Margin (Starter) | 55-80% | 78-88% | >70% ✅ |
| User complaints | N/A | TBD | <5% |

---

## Priority: 🔴 CRITICAL

**Deploy Before:** Launch Day (no active users yet)  
**Estimated Effort:** 4-6 hours (backend + frontend + testing)  
**Risk if Unfixed:** $5-10K monthly loss at scale  

**Approved By:** CEO + CTO  
**Implementation Owner:** Engineering  
**Target Date:** January 25, 2026

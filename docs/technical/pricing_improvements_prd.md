# Product Requirements Document: Pricing System Improvements

**Document Type:** Product Requirements Document (PRD)  
**Owner:** CEO/CFO  
**Assignee:** CTO  
**Priority:** P0 (CRITICAL - Negative margins currently)  
**Target Launch:** Phase 1 by February 1, 2026  
**Related Documents:**
- [CFO Report to CEO](../../.gemini/antigravity/brain/2d61d8ef-536d-4375-99b4-44a908603a2e/cfo_report_to_ceo.md)
- [Pricing Strategy 2026](../reports/pricing_strategy_2026.md)

---

## Executive Summary

**Problem:** Current pricing model creates negative unit economics due to lack of duration-based and weighted credit systems. Videos >45 seconds lose money ($0.40 revenue vs $11.22 COGS).

**Solution:** Implement 4-phase pricing improvements to prevent margin bleeding and prepare for USD subscription transition.

**Impact:**
- Phase 1: Stop losing money on long videos (immediate)
- Phase 2-4: Enable $1.2M+ ARR potential with 85% margins

**Timeline:**
- Phase 1 (Emergency): 2 weeks
- Phase 2 (Subscriptions): 4-6 weeks
- Phase 3 (Self-Hosted): 8-12 weeks
- Phase 4 (Agency): 12-16 weeks

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Goals & Success Metrics](#goals--success-metrics)
3. [Phase 1: Emergency COGS Protection](#phase-1-emergency-cogs-protection-p0)
4. [Phase 2: USD Subscription System](#phase-2-usd-subscription-system-p1)
5. [Phase 3: Self-Hosted Infrastructure](#phase-3-self-hosted-infrastructure-p1)
6. [Phase 4: Agency Features](#phase-4-agency-features-p2)
7. [Technical Architecture](#technical-architecture)
8. [Testing Requirements](#testing-requirements)
9. [Deployment Strategy](#deployment-strategy)
10. [Risk Mitigation](#risk-mitigation)

---

## Problem Statement

### Current State

**Pricing Model:**
- INR one-time credit purchases
- 1 credit = any video (regardless of length or features)
- Credits never expire

**Critical Issues:**

1. **Negative Unit Economics**
   ```
   30s video: Revenue $0.40 | COGS $5.61 | Loss -$5.21
   60s video: Revenue $0.40 | COGS $11.22 | Loss -$10.82
   90s video: Revenue $0.40 | COGS $16.83 | Loss -$16.43
   ```

2. **No Feature-Based Pricing**
   - Generative background: 5x normal cost, same price
   - 4K export: 3x normal cost, same price
   - Premium TTS: 2x normal cost, same price

3. **Deferred Liability**
   - Non-expiring credits = unbounded future costs
   - No predictable revenue stream

4. **Competitive Misalignment**
   - Market: $49-220/month subscriptions
   - Us: $6-144 one-time purchases
   - Signal: "Budget tool" not premium SaaS

---

## Goals & Success Metrics

### Phase 1 Goals (Emergency)

**Primary Goal:** Stop bleeding money on current customers

**Success Metrics:**
- ✅ Zero videos with negative margins
- ✅ Average margin per video >40%
- ✅ Admin can monitor margins in real-time
- ✅ No existing user complaints (grandfather transition smoothly)

### Phase 2 Goals (Subscriptions)

**Primary Goal:** Launch USD subscription model

**Success Metrics:**
- ✅ 50+ new subscription signups in Month 1
- ✅ 30% of existing users migrate to subscriptions
- ✅ MRR >$10K within 60 days
- ✅ Churn rate <10% monthly

### Phase 3 Goals (Infrastructure)

**Primary Goal:** Reduce COGS by 90%+

**Success Metrics:**
- ✅ COGS per video <$0.50 (from $5.61)
- ✅ Gross margin >80%
- ✅ Video quality maintained (user satisfaction ≥ current)
- ✅ Generation speed maintained or improved

### Phase 4 Goals (Agency)

**Primary Goal:** Enable white-label agency tier

**Success Metrics:**
- ✅ 10+ agency customers signed
- ✅ Agency MRR >$5K
- ✅ API uptime >99.9%
- ✅ Zero data leakage between agencies

---

## Phase 1: Emergency COGS Protection (P0)

**Timeline:** 2 weeks  
**Priority:** CRITICAL  
**Start Date:** Immediately upon CEO approval

### 1.1 Duration-Based Pricing

**Requirement:** Charge credits proportional to video length

**Business Logic:**
```typescript
function calculateDurationCredits(videoLengthSeconds: number): number {
  const BASE_DURATION = 30; // seconds
  return Math.ceil(videoLengthSeconds / BASE_DURATION);
}

// Examples:
// 15s video = 1 credit
// 30s video = 1 credit
// 45s video = 2 credits
// 60s video = 2 credits
// 90s video = 3 credits
```

**Backend Changes:**

**File:** `projects/backend/services/pricing_service.py`

```python
def calculate_video_credits(
    duration_seconds: int,
    features: Dict[str, bool]
) -> int:
    """
    Calculate credit cost based on duration and features.
    
    Args:
        duration_seconds: Video length in seconds
        features: Dict of enabled features {
            'generative_background': bool,
            'premium_tts': bool,
            '4k_resolution': bool
        }
    
    Returns:
        Total credits to charge
    """
    BASE_DURATION = 30
    
    # Duration-based credits (1 credit per 30s)
    duration_credits = math.ceil(duration_seconds / BASE_DURATION)
    
    # Weighted feature credits (Phase 1: placeholder)
    feature_credits = 0
    
    return duration_credits + feature_credits
```

**Database Changes:**

**New column in `campaigns` table:**
```sql
ALTER TABLE campaigns 
ADD COLUMN video_duration_seconds INTEGER DEFAULT 30;

ALTER TABLE campaigns
ADD COLUMN credits_charged INTEGER DEFAULT 1;

-- Backfill existing campaigns
UPDATE campaigns 
SET video_duration_seconds = 30, 
    credits_charged = 1 
WHERE video_duration_seconds IS NULL;
```

**API Changes:**

**Endpoint:** `POST /api/campaigns/generate`

**Request (add field):**
```json
{
  "campaign_name": "Summer Sale",
  "video_duration_seconds": 60,  // NEW FIELD (required)
  "scenes": [...]
}
```

**Response (add fields):**
```json
{
  "campaign_id": "abc123",
  "credits_charged": 2,  // NEW FIELD
  "credits_remaining": 13,  // NEW FIELD
  "estimated_cost_breakdown": {  // NEW FIELD
    "duration_credits": 2,
    "feature_credits": 0,
    "total_credits": 2
  }
}
```

**Frontend Changes:**

**File:** `projects/frontend/src/app/campaigns/editor.component.ts`

```typescript
// Add duration selector
export class EditorComponent {
  videoDuration: number = 30; // default
  
  durationOptions = [
    { value: 15, label: '15 seconds', credits: 1 },
    { value: 30, label: '30 seconds', credits: 1 },
    { value: 45, label: '45 seconds', credits: 2 },
    { value: 60, label: '60 seconds', credits: 2 },
    { value: 90, label: '90 seconds', credits: 3 }
  ];
  
  calculateEstimatedCredits(): number {
    return Math.ceil(this.videoDuration / 30);
  }
  
  async generateCampaign() {
    const estimatedCredits = this.calculateEstimatedCredits();
    
    // Confirm if credits insufficient
    if (this.userCredits < estimatedCredits) {
      this.showUpgradeModal();
      return;
    }
    
    // Show credit cost before generating
    const confirmed = await this.confirmDialog(
      `This will use ${estimatedCredits} credits. Continue?`
    );
    
    if (!confirmed) return;
    
    // Include duration in request
    const payload = {
      ...this.campaignData,
      video_duration_seconds: this.videoDuration
    };
    
    // Generate campaign
    this.apiService.post('/api/campaigns/generate', payload).subscribe(...);
  }
}
```

**HTML Changes:**

```html
<!-- Add before Generate button -->
<div class="duration-selector">
  <label>Video Duration</label>
  <select [(ngModel)]="videoDuration">
    <option *ngFor="let opt of durationOptions" [value]="opt.value">
      {{ opt.label }} ({{ opt.credits }} credit{{ opt.credits > 1 ? 's' : '' }})
    </option>
  </select>
  
  <div class="credit-estimate">
    Estimated cost: {{ calculateEstimatedCredits() }} credit(s)
  </div>
</div>
```

**Acceptance Criteria:**
- [ ] Backend calculates duration credits correctly
- [ ] Database stores duration and credits charged
- [ ] Frontend shows duration selector with credit costs
- [ ] Users cannot generate if insufficient credits
- [ ] Confirmation dialog shows credit cost before generating
- [ ] Existing campaigns backfilled with default values
- [ ] Unit tests for all credit calculations (100% coverage)

---

### 1.2 Weighted Credits System

**Requirement:** Charge additional credits for premium features

**Business Logic:**
```typescript
// Credit weights
const FEATURE_WEIGHTS = {
  generative_background: 2,  // +2 credits
  premium_tts: 1,            // +1 credit
  '4k_resolution': 1         // +1 credit
};

// Example calculation:
// 60s video (2 credits) + genBG (2) + premium TTS (1) + 4K (1) = 6 credits total
```

**Backend Changes:**

**File:** `projects/backend/services/pricing_service.py`

```python
# Credit cost configuration
FEATURE_CREDITS = {
    'generative_background': 2,
    'premium_tts': 1,
    '4k_resolution': 1,
    'custom_avatar': 1  # Future use
}

def calculate_video_credits(
    duration_seconds: int,
    features: Dict[str, bool]
) -> Dict[str, int]:
    """Calculate total credits with breakdown."""
    BASE_DURATION = 30
    
    # Duration credits
    duration_credits = math.ceil(duration_seconds / BASE_DURATION)
    
    # Feature credits
    feature_credits = sum(
        FEATURE_CREDITS[feature]
        for feature, enabled in features.items()
        if enabled and feature in FEATURE_CREDITS
    )
    
    total = duration_credits + feature_credits
    
    return {
        'duration_credits': duration_credits,
        'feature_credits': feature_credits,
        'total_credits': total,
        'breakdown': {
            feature: FEATURE_CREDITS[feature]
            for feature, enabled in features.items()
            if enabled and feature in FEATURE_CREDITS
        }
    }
```

**Database Changes:**

```sql
-- Store feature flags per campaign
ALTER TABLE campaigns 
ADD COLUMN features_used JSONB DEFAULT '{}';

-- Example value:
-- {"generative_background": true, "premium_tts": true, "4k_resolution": false}
```

**Frontend Changes:**

**File:** `projects/frontend/src/app/campaigns/editor.component.html`

```html
<div class="premium-features">
  <h3>Premium Features</h3>
  
  <div class="feature-toggle">
    <label>
      <input type="checkbox" [(ngModel)]="features.generative_background">
      Generative Background
      <span class="credit-badge">+2 credits</span>
    </label>
    <p class="feature-desc">AI-generated backgrounds instead of static images</p>
  </div>
  
  <div class="feature-toggle">
    <label>
      <input type="checkbox" [(ngModel)]="features.premium_tts">
      Premium Voice (ElevenLabs)
      <span class="credit-badge">+1 credit</span>
    </label>
    <p class="feature-desc">Ultra-realistic voice synthesis</p>
  </div>
  
  <div class="feature-toggle">
    <label>
      <input type="checkbox" [(ngModel)]="features.4k_resolution">
      4K Export (3840×2160)
      <span class="credit-badge">+1 credit</span>
    </label>
    <p class="feature-desc">Premium quality for paid ads</p>
  </div>
  
  <div class="total-cost">
    <strong>Total Cost:</strong> {{ calculateTotalCredits() }} credits
    <div class="breakdown">
      ({{ durationCredits }} duration + {{ featureCredits }} features)
    </div>
  </div>
</div>
```

**Acceptance Criteria:**
- [ ] Each premium feature adds correct credit cost
- [ ] Frontend shows cost breakdown (duration + features)
- [ ] Backend validates feature flags before processing
- [ ] Database stores which features were used
- [ ] Credit deduction matches exact calculation
- [ ] Users can see cost update in real-time as they toggle features
- [ ] Integration tests for all feature combinations

---

### 1.3 Admin Margin Monitoring Dashboard

**Requirement:** Real-time visibility into margins and COGS per user/campaign

**Backend Changes:**

**New Endpoint:** `GET /api/admin/margins`

```python
@router.get("/admin/margins")
async def get_margin_analytics(
    current_user: User = Depends(get_current_admin_user),
    time_range: str = "7d"  # 7d, 30d, all
):
    """
    Get margin analytics for admin dashboard.
    Requires admin role.
    """
    campaigns = await get_campaigns_in_range(time_range)
    
    analytics = []
    for campaign in campaigns:
        # Calculate actual COGS from logs
        cogs = await calculate_actual_cogs(campaign.id)
        
        # Calculate revenue from credits charged
        credits_charged = campaign.credits_charged
        revenue_per_credit = get_plan_price(campaign.user_id) / get_plan_credits(campaign.user_id)
        revenue = credits_charged * revenue_per_credit
        
        margin = revenue - cogs
        margin_percent = (margin / revenue * 100) if revenue > 0 else 0
        
        analytics.append({
            'campaign_id': campaign.id,
            'user_id': campaign.user_id,
            'created_at': campaign.created_at,
            'duration_seconds': campaign.video_duration_seconds,
            'features_used': campaign.features_used,
            'credits_charged': credits_charged,
            'revenue_usd': round(revenue, 2),
            'cogs_usd': round(cogs, 2),
            'margin_usd': round(margin, 2),
            'margin_percent': round(margin_percent, 1),
            'status': 'healthy' if margin > 0 else 'negative'
        })
    
    # Aggregate stats
    total_revenue = sum(a['revenue_usd'] for a in analytics)
    total_cogs = sum(a['cogs_usd'] for a in analytics)
    overall_margin = ((total_revenue - total_cogs) / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        'time_range': time_range,
        'total_campaigns': len(analytics),
        'total_revenue_usd': round(total_revenue, 2),
        'total_cogs_usd': round(total_cogs, 2),
        'overall_margin_percent': round(overall_margin, 1),
        'negative_margin_count': sum(1 for a in analytics if a['margin_usd'] < 0),
        'campaigns': analytics[:100]  # Limit to 100 most recent
    }
```

**COGS Tracking:**

**File:** `projects/backend/services/cogs_tracker.py` (NEW FILE)

```python
from datetime import datetime
from typing import Dict
import firebase_admin.firestore as firestore

class CogsTracker:
    """Track actual API costs per campaign for margin analysis."""
    
    def __init__(self):
        self.db = firestore.client()
    
    async def log_api_call(
        self,
        campaign_id: str,
        api_name: str,  # 'runway', 'elevenlabs', 'storage'
        cost_usd: float,
        metadata: Dict = None
    ):
        """Log an API call cost."""
        doc_ref = self.db.collection('cogs_logs').document()
        await doc_ref.set({
            'campaign_id': campaign_id,
            'api_name': api_name,
            'cost_usd': cost_usd,
            'metadata': metadata or {},
            'timestamp': datetime.utcnow()
        })
    
    async def get_campaign_cogs(self, campaign_id: str) -> float:
        """Get total COGS for a campaign."""
        logs = self.db.collection('cogs_logs')\
            .where('campaign_id', '==', campaign_id)\
            .stream()
        
        total_cogs = sum(log.to_dict()['cost_usd'] for log in logs)
        return total_cogs
```

**Usage in video generation:**

```python
# In video_service.py
cogs_tracker = CogsTracker()

# When calling Runway API
video_result = await runway_client.generate(...)
await cogs_tracker.log_api_call(
    campaign_id=campaign.id,
    api_name='runway',
    cost_usd=10.00,  # Runway charges $10 per 60s
    metadata={'duration_seconds': 60, 'resolution': '1080p'}
)

# When calling ElevenLabs
audio_result = await elevenlabs_client.generate(...)
await cogs_tracker.log_api_call(
    campaign_id=campaign.id,
    api_name='elevenlabs',
    cost_usd=1.00,
    metadata={'characters': len(script), 'voice': 'premium'}
)
```

**Frontend Dashboard:**

**File:** `projects/frontend/src/app/admin/margin-dashboard.component.ts` (NEW FILE)

```typescript
export class MarginDashboardComponent implements OnInit {
  analytics: any;
  loading = false;
  
  timeRange = '7d'; // 7d, 30d, all
  
  async ngOnInit() {
    await this.loadAnalytics();
  }
  
  async loadAnalytics() {
    this.loading = true;
    const response = await this.apiService.get(`/api/admin/margins?time_range=${this.timeRange}`);
    this.analytics = response;
    this.loading = false;
  }
  
  getStatusColor(campaign: any): string {
    if (campaign.margin_percent > 50) return 'green';
    if (campaign.margin_percent > 0) return 'yellow';
    return 'red';
  }
}
```

**HTML Template:**

```html
<div class="admin-dashboard">
  <h1>Margin Analytics</h1>
  
  <div class="summary-cards">
    <div class="card">
      <h3>Total Revenue</h3>
      <div class="value">${{ analytics.total_revenue_usd }}</div>
    </div>
    
    <div class="card">
      <h3>Total COGS</h3>
      <div class="value">${{ analytics.total_cogs_usd }}</div>
    </div>
    
    <div class="card" [class.negative]="analytics.overall_margin_percent < 0">
      <h3>Overall Margin</h3>
      <div class="value">{{ analytics.overall_margin_percent }}%</div>
    </div>
    
    <div class="card warning" *ngIf="analytics.negative_margin_count > 0">
      <h3>Negative Margins</h3>
      <div class="value">{{ analytics.negative_margin_count }} campaigns</div>
    </div>
  </div>
  
  <table class="campaigns-table">
    <thead>
      <tr>
        <th>Campaign ID</th>
        <th>User</th>
        <th>Duration</th>
        <th>Credits</th>
        <th>Revenue</th>
        <th>COGS</th>
        <th>Margin</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <tr *ngFor="let campaign of analytics.campaigns" 
          [class.negative]="campaign.margin_usd < 0">
        <td>{{ campaign.campaign_id }}</td>
        <td>{{ campaign.user_id }}</td>
        <td>{{ campaign.duration_seconds }}s</td>
        <td>{{ campaign.credits_charged }}</td>
        <td>${{ campaign.revenue_usd }}</td>
        <td>${{ campaign.cogs_usd }}</td>
        <td [style.color]="getStatusColor(campaign)">
          {{ campaign.margin_percent }}%
        </td>
        <td>
          <span class="badge" [class]="campaign.status">
            {{ campaign.status }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

**Acceptance Criteria:**
- [ ] Admin can view margin analytics (admin role required)
- [ ] Dashboard shows aggregate stats (revenue, COGS, margin %)
- [ ] Table lists all campaigns with per-campaign margins
- [ ] Negative margin campaigns highlighted in red
- [ ] COGS tracked accurately for all API calls
- [ ] Analytics can filter by time range (7d, 30d, all)
- [ ] Dashboard updates in real-time (or on refresh)
- [ ] Export to CSV functionality for deeper analysis

---

### 1.4 Grandfather Clause for Existing Users

**Requirement:** Existing users keep their purchased credits at old rates

**Backend Changes:**

**Database Migration:**

```sql
-- Add grandfather flag to users
ALTER TABLE users 
ADD COLUMN grandfathered BOOLEAN DEFAULT FALSE;

ADD COLUMN grandfathered_at TIMESTAMP;

-- Mark all existing users as grandfathered
UPDATE users 
SET grandfathered = TRUE,
    grandfathered_at = NOW()
WHERE created_at < '2026-02-01';  -- Before Phase 1 launch

-- Add to users table
ALTER TABLE credit_transactions
ADD COLUMN credit_calculation_version VARCHAR(10) DEFAULT 'v1';
-- v1 = old (1 credit/video), v2 = new (duration + weighted)
```

**Pricing Service Update:**

```python
def calculate_video_credits(
    user_id: str,
    duration_seconds: int,
    features: Dict[str, bool]
) -> int:
    """Calculate credits, respecting grandfather clause."""
    
    # Check if user is grandfathered
    user = get_user(user_id)
    
    if user.grandfathered and user.credits_remaining > 0:
        # Use old pricing (1 credit per video)
        return 1
    else:
        # Use new pricing (duration + weighted)
        return calculate_dynamic_credits(duration_seconds, features)
```

**Frontend Notice:**

```html
<!-- Show badge for grandfathered users -->
<div class="credit-display" *ngIf="user.grandfathered">
  <span class="badge grandfathered">
    ⭐ Grandfathered Pricing
  </span>
  <p class="small">
    You're using old pricing (1 credit/video) until your current balance runs out.
    <a href="/pricing">Learn about new pricing</a>
  </p>
</div>
```

**Acceptance Criteria:**
- [ ] All existing users flagged as grandfathered before launch
- [ ] Grandfathered users charged 1 credit per video (old system)
- [ ] Once grandfathered credits depleted, new pricing applies
- [ ] Users notified of grandfather status in UI
- [ ] Credit transactions logged with version (v1 vs v2)
- [ ] No complaints from existing users
- [ ] Clear migration path documented

---

## Phase 2: USD Subscription System (P1)

**Timeline:** 4-6 weeks  
**Priority:** HIGH  
**Dependencies:** Phase 1 complete

### 2.1 Stripe Integration

**Requirement:** Accept USD payments via Stripe for subscriptions

**Backend Changes:**

**New File:** `projects/backend/services/stripe_service.py`

```python
import stripe
from typing import Dict
import os

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class StripeService:
    """Handle Stripe subscription management."""
    
    PRICE_IDS = {
        'starter_monthly': 'price_starter_monthly',
        'starter_annual': 'price_starter_annual',
        'growth_monthly': 'price_growth_monthly',
        'growth_annual': 'growth_annual',
        'agency_monthly': 'price_agency_monthly',
        'agency_annual': 'price_agency_annual'
    }
    
    async def create_checkout_session(
        self,
        user_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """Create Stripe checkout session for subscription."""
        
        session = stripe.checkout.Session.create(
            customer_email=get_user_email(user_id),
            mode='subscription',
            line_items=[{
                'price': price_id,
                'quantity': 1
            }],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={'user_id': user_id}
        )
        
        return {
            'session_id': session.id,
            'url': session.url
        }
    
    async def handle_webhook(self, payload: bytes, sig_header: str):
        """Handle Stripe webhooks for subscription events."""
        
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
        
        if event.type == 'checkout.session.completed':
            await self._handle_checkout_completed(event.data.object)
        elif event.type == 'invoice.payment_succeeded':
            await self._handle_payment_succeeded(event.data.object)
        elif event.type == 'customer.subscription.deleted':
            await self._handle_subscription_canceled(event.data.object)
    
    async def _handle_checkout_completed(self, session):
        """Award credits on successful checkout."""
        user_id = session.metadata.user_id
        subscription_id = session.subscription
        
        # Get subscription details
        subscription = stripe.Subscription.retrieve(subscription_id)
        price_id = subscription['items']['data'][0]['price']['id']
        
        # Map price to credits
        credits = self._get_credits_for_price(price_id)
        
        # Award credits
        await award_credits(
            user_id=user_id,
            credits=credits,
            source='stripe_subscription',
            reference_id=subscription_id
        )
        
        # Update user subscription status
        await update_user_subscription(
            user_id=user_id,
            stripe_subscription_id=subscription_id,
            plan=self._get_plan_for_price(price_id),
            status='active'
        )
```

**New Endpoint:** `POST /api/payments/create-subscription`

```python
@router.post("/payments/create-subscription")
async def create_subscription(
    data: CreateSubscriptionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session for subscription."""
    
    stripe_service = StripeService()
    
    session = await stripe_service.create_checkout_session(
        user_id=current_user.uid,
        price_id=data.price_id,
        success_url=f"{data.redirect_base}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{data.redirect_base}/pricing"
    )
    
    return session
```

**Database Changes:**

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    plan VARCHAR(50) NOT NULL,  -- 'starter', 'growth', 'agency'
    interval VARCHAR(20) NOT NULL,  -- 'monthly', 'annual'
    status VARCHAR(50) NOT NULL,  -- 'active', 'canceled', 'past_due'
    current_period_start TIMESTAMP,
    current_period_end TIMESTAMP,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_stripe_id ON subscriptions(stripe_subscription_id);
```

**Acceptance Criteria:**
- [ ] Stripe integration configured in backend
- [ ] Checkout session creation works
- [ ] Webhook handling awards credits correctly
- [ ] Subscription status tracked in database
- [ ] Monthly credit renewal automated
- [ ] Payment failures handled gracefully
- [ ] Users can view subscription status
- [ ] Users can cancel subscription (via Stripe portal)

---

### 2.2 Frontend Subscription Management

**New Pricing Page:** `projects/frontend/src/app/pricing-new/pricing-new.component.html`

```html
<div class="pricing-page">
  <div class="toggle">
    <button [class.active]="billingCycle === 'monthly'" (click)="billingCycle = 'monthly'">
      Monthly
    </button>
    <button [class.active]="billingCycle === 'annual'" (click)="billingCycle = 'annual'">
      Annual
      <span class="badge">Save 20%</span>
    </button>
  </div>
  
  <div class="plans-grid">
    <!-- Starter Plan -->
    <div class="plan-card">
      <h3>Starter</h3>
      <div class="price">
        <span class="amount">${{ billingCycle === 'monthly' ? 49 : 39 }}</span>
        <span class="period">/month</span>
      </div>
      <p class="billing-note" *ngIf="billingCycle === 'annual'">
        Billed $470 annually
      </p>
      
      <ul class="features">
        <li>✅ 40 credits/month</li>
        <li>✅ 1080p exports</li>
        <li>✅ No watermarks</li>
        <li>✅ Email support</li>
      </ul>
      
      <button (click)="subscribe('starter', billingCycle)">
        Start Free Trial
      </button>
      <p class="trial-note">7-day free trial, cancel anytime</p>
    </div>
    
    <!-- Similar cards for Growth and Agency -->
  </div>
</div>
```

**Component Logic:**

```typescript
export class PricingNewComponent {
  billingCycle: 'monthly' | 'annual' = 'monthly';
  
  async subscribe(plan: string, cycle: string) {
    const priceId = this.getPriceId(plan, cycle);
    
    const response = await this.apiService.post('/api/payments/create-subscription', {
      price_id: priceId,
      redirect_base: window.location.origin
    });
    
    // Redirect to Stripe checkout
    window.location.href = response.url;
  }
  
  getPriceId(plan: string, cycle: string): string {
    const key = `${plan}_${cycle}`;
    const priceIds = {
      'starter_monthly': 'price_...',
      'starter_annual': 'price_...',
      // etc
    };
    return priceIds[key];
  }
}
```

**Acceptance Criteria:**
- [ ] Pricing page shows monthly/annual toggle
- [ ] Plans display correctly with features
- [ ] Subscribe button redirects to Stripe checkout
- [ ] Success page shows after payment
- [ ] Credits awarded immediately after payment
- [ ] User redirected to dashboard after success
- [ ] Cancel flow works (via account settings)

---

## Phase 3: Self-Hosted Infrastructure (P1)

**Timeline:** 8-12 weeks  
**Priority:** HIGH  
**Dependencies:** Phase 2 complete, fundraising/budget approval

### 3.1 Reserved GPU Procurement

**Requirement:** Purchase GCP Reserved GPU instances

**Infrastructure:**

```bash
# Reserve 2x A100 40GB GPUs
gcloud compute commitments create igniteai-gpu-commitment \
  --resources=nvidia-tesla-a100=2 \
  --plan=12-month \
  --region=us-central1

# Estimated cost: $1,500-2,000/month
# Savings vs on-demand: 30-40%
```

**Auto-Scaling Configuration:**

```yaml
# Cloud Run GPU service config
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: video-generator-gpu
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "2"
        autoscaling.knative.dev/maxScale: "5"
    spec:
      containers:
      - image: gcr.io/igniteai/video-gen-gpu:latest
        resources:
          limits:
            nvidia.com/gpu: "1"
            memory: "40Gi"
            cpu: "8"
```

**Acceptance Criteria:**
- [ ] Reserved GPUs purchased and active
- [ ] Auto-scaling configured (2 min, 5 max)
- [ ] GPU utilization monitored
- [ ] Cost alerts set (<$2K/month)
- [ ] Fallback to on-demand if reserved exhausted

---

### 3.2 LivePortrait Deployment

**Requirement:** Deploy open-source LivePortrait model for face animation

**New Service:** `projects/gpu-services/liveportrait/`

```python
# app.py
from fastapi import FastAPI, UploadFile
import torch
from liveportrait import LivePortraitPipeline

app = FastAPI()

# Load model on startup
pipeline = LivePortraitPipeline.from_pretrained(
    "KwaiVGI/LivePortrait",
    torch_dtype=torch.float16
).to("cuda")

@app.post("/api/v1/animate")
async def animate_face(
    source_image: UploadFile,
    driving_video: UploadFile,
    duration_seconds: int
):
    """Animate face using LivePortrait."""
    
    # Load inputs
    source = load_image(source_image)
    driving = load_video(driving_video)
    
    # Run inference
    result = pipeline(
        source_image=source,
        driving_video=driving,
        num_frames=duration_seconds * 30  # 30 fps
    )
    
    # Save and return
    output_path = save_video(result)
    
    return {
        "video_url": output_path,
        "duration_seconds": duration_seconds,
        "cost_usd": 0.25  # Reserved GPU cost
    }
```

**Acceptance Criteria:**
- [ ] LivePortrait model deployed on GPU instances
- [ ] API endpoint responds <10s for 30s video
- [ ] Quality comparable to Runway ML (user testing)
- [ ] COGS reduced to <$0.30 per 30s video
- [ ] Automatic fallback to Runway if GPU service fails

---

## Phase 4: Agency Features (P2)

**Timeline:** 12-16 weeks  
**Priority:** MEDIUM  
**Dependencies:** Phase 2 complete, agency demand validated

### 4.1 White-Label Mode

**Requirement:** Agencies can remove IgniteAI branding

**Backend:**

```sql
-- Add white_label settings to subscriptions
ALTER TABLE subscriptions
ADD COLUMN white_label_enabled BOOLEAN DEFAULT FALSE;

CREATE TABLE white_label_settings (
    user_id VARCHAR(255) PRIMARY KEY,
    custom_logo_url TEXT,
    primary_color VARCHAR(7),  -- Hex color
    company_name VARCHAR(255),
    hide_igniteai_branding BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**Frontend:**

```typescript
// Dynamic branding
export class BrandingService {
  async getBranding(userId: string): Promise<BrandingConfig> {
    const settings = await this.apiService.get(`/api/white-label/${userId}`);
    
    if (settings.white_label_enabled) {
      return {
        logoUrl: settings.custom_logo_url,
        primaryColor: settings.primary_color,
        companyName: settings.company_name,
        hideIgniteAI: settings.hide_igniteai_branding
      };
    } else {
      return DEFAULT_IGNITEAI_BRANDING;
    }
  }
}
```

**Acceptance Criteria:**
- [ ] Agencies can upload custom logo
- [ ] Agencies can set primary color
- [ ] Video exports exclude IgniteAI branding
- [ ] UI reflects agency branding when logged in
- [ ] Embed code works with agency branding

---

### 4.2 API Access

**Requirement:** REST API for agency automation

**New Endpoint:** `POST /api/v1/campaigns/create`

```python
@router.post("/v1/campaigns/create")
async def create_campaign_api(
    data: CampaignCreateRequest,
    api_key: str = Depends(validate_api_key)
):
    """Create campaign via API (agency tier only)."""
    
    # Validate API key and plan
    user = get_user_from_api_key(api_key)
    if user.subscription_plan != 'agency':
        raise HTTPException(403, "API access requires Agency plan")
    
    # Create campaign
    campaign = await create_campaign(
        user_id=user.uid,
        **data.dict()
    )
    
    return {
        "campaign_id": campaign.id,
        "status": "processing",
        "webhook_url": data.webhook_url  # Notify on completion
    }
```

**Rate Limiting:**

```python
# Rate limit: 100 requests/minute for agency tier
@router.post("/v1/campaigns/create")
@rate_limit(limit=100, window=60)
async def create_campaign_api(...):
    ...
```

**Acceptance Criteria:**
- [ ] API keys generated for agency users
- [ ] All core endpoints accessible via API
- [ ] Webhook notifications on job completion
- [ ] Rate limiting enforced (100/min)
- [ ] API documentation published (OpenAPI/Swagger)
- [ ] SDKs generated (Python, JavaScript)

---

## Technical Architecture

### System Diagram

```
┌─────────────────┐
│   Next.js       │
│   Landing       │◄─── SEO, Marketing
│   (igniteai.com)│
└────────┬────────┘
         │
         │ Sign Up/Pricing
         ▼
┌─────────────────┐      ┌──────────────┐
│   Angular App   │◄────►│   Firebase   │
│ (app.igniteai.  │      │   Auth       │
│      com)       │      └──────────────┘
└────────┬────────┘
         │
         │ API Calls
         ▼
┌─────────────────┐      ┌──────────────┐      ┌──────────────┐
│   FastAPI       │────► │   Firestore  │      │   Stripe     │
│   Backend       │      │   Database   │      │   Payments   │
│ (Cloud Run)     │      └──────────────┘      └──────────────┘
└────────┬────────┘
         │
         ├─────► Runway ML API (Phase 1-2)
         │
         └─────► Self-Hosted GPU (Phase 3+)
                 ├─ LivePortrait (face animation)
                 ├─ Coqui TTS (voice)
                 └─ SDXL (backgrounds)
```

### Database Schema (Key Tables)

```sql
-- Users
CREATE TABLE users (
    uid VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    credits_remaining INTEGER DEFAULT 0,
    grandfathered BOOLEAN DEFAULT FALSE,
    subscription_plan VARCHAR(50),  -- NULL, 'starter', 'growth', 'agency'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(uid),
    stripe_subscription_id VARCHAR(255) UNIQUE,
    plan VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL,
    current_period_end TIMESTAMP
);

-- Campaigns
CREATE TABLE campaigns (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) REFERENCES users(uid),
    video_duration_seconds INTEGER DEFAULT 30,
    features_used JSONB DEFAULT '{}',
    credits_charged INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- COGS Logs
CREATE TABLE cogs_logs (
    id SERIAL PRIMARY KEY,
    campaign_id VARCHAR(255) REFERENCES campaigns(id),
    api_name VARCHAR(50) NOT NULL,
    cost_usd DECIMAL(10, 4) NOT NULL,
    metadata JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

---

## Testing Requirements

### Unit Tests

**Backend:**
- [ ] `test_calculate_duration_credits()` - All duration scenarios
- [ ] `test_calculate_weighted_credits()` - All feature combinations
- [ ] `test_grandfather_clause()` - Old vs new pricing logic
- [ ] `test_stripe_webhook_handling()` - All event types
- [ ] `test_api_rate_limiting()` - Agency API limits

**Frontend:**
- [ ] Credit estimation updates correctly
- [ ] Feature toggles update cost in real-time
- [ ] Insufficient credits shows upgrade modal
- [ ] Grandfathered badge displays correctly

### Integration Tests

- [ ] Full campaign generation flow (new pricing)
- [ ] Subscription purchase → credit award → renewal
- [ ] Grandfather clause: existing user vs new user
- [ ] Admin dashboard displays correct margins
- [ ] API key authentication and rate limiting

### Load Tests

- [ ] 100 concurrent campaign generations
- [ ] Stripe webhook burst (100 events/second)
- [ ] Admin dashboard with 10K campaigns
- [ ] GPU auto-scaling under load

---

## Deployment Strategy

### Phase 1 Deployment

**Pre-Launch Checklist:**
- [ ] All unit tests passing (100% coverage critical paths)
- [ ] Integration tests passing
- [ ] Database migration tested on staging
- [ ] Grandfather flag applied to all existing users
- [ ] Admin dashboard accessible
- [ ] Rollback plan documented

**Launch Steps:**

1. **Deploy Backend** (Week 1 Thursday, off-peak hours)
   ```bash
   # 1. Run database migration
   ./scripts/migrate-phase1.sh
   
   # 2. Deploy to Cloud Run
   ./scripts/deploy-backend.sh
   
   # 3. Verify health check
   curl https://backend-url/health
   ```

2. **Deploy Frontend** (Week 1 Friday, off-peak hours)
   ```bash
   # 1. Build with new pricing UI
   npm run build:app
   
   # 2. Deploy to Firebase
   firebase deploy --only hosting:app
   ```

3. **Monitor for 48 Hours**
   - Watch margin dashboard for negative margins
   - Monitor error logs for credit calculation issues
   - Track user support tickets
   - Verify grandfather clause working

4. **Communicate to Users** (Week 2 Monday)
   ```
   Subject: Introducing Fair Pricing Based on Video Length
   
   Hi [Name],
   
   Starting today, IgniteAI's credit system now reflects video length:
   - 15-30s videos: 1 credit
   - 45-60s videos: 2 credits
   - 90s videos: 3 credits
   
   ⭐ Your existing credits are grandfathered at the old rate (1 credit per video).
   
   Once you run out, new purchases will use the updated pricing.
   
   We also added premium features (generative backgrounds, 4K exports) that you can enable for additional credits.
   
   Questions? Reply to this email.
   
   Thanks,
   The IgniteAI Team
   ```

**Rollback Plan:**

If critical issues occur within 48 hours:

```bash
# 1. Revert backend deployment
gcloud run services update-traffic igniteai-backend \
  --to-revisions=PREVIOUS_REVISION=100

# 2. Revert database migration
./scripts/rollback-phase1.sh

# 3. Notify users of temporary rollback
```

### Phase 2 Deployment

**Pre-Launch:**
- [ ] Stripe account verified (business verification complete)
- [ ] Test payments processed successfully
- [ ] Webhook endpoint tested with Stripe CLI
- [ ] Subscription cancellation flow tested

**Launch:**
- Gradual rollout: 10% → 50% → 100% over 2 weeks
- A/B test: Show subscription option to 50% of users
- Monitor conversion rate, churn rate

---

## Risk Mitigation

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Credit calculation bugs | Medium | Critical | 100% unit test coverage, manual QA |
| Database migration failure | Low | Critical | Test on staging, rollback script ready |
| Stripe webhook failures | Low | High | Retry logic, manual reconciliation tool |
| GPU service downtime | Medium | High | Automatic fallback to Runway ML API |
| User data loss | Low | Critical | Daily backups, point-in-time recovery |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Existing user churn | Medium | Medium | Grandfather clause, clear communication |
| New pricing too high | Low | Medium | A/B test, customer surveys first |
| Subscription conversion <30% | Medium | High | Optimize pricing page, offer discounts |
| Negative PR | Low | High | Transparent communication, grandfather clause |

---

## Success Criteria

### Phase 1 Success Metrics

**Week 1:**
- ✅ Zero critical bugs reported
- ✅ <5% user support ticket increase
- ✅ Grandfather clause working (no complaints)

**Week 2:**
- ✅ Average margin >40% (vs <0% before)
- ✅ Zero negative margin campaigns
- ✅ Admin dashboard shows green across all metrics

### Phase 2 Success Metrics

**Month 1:**
- ✅ 50+ new subscribers
- ✅ MRR >$5K
- ✅ <10% monthly churn

**Month 2:**
- ✅ MRR >$10K
- ✅ 30% of existing users migrated
- ✅ Stripe integration stable (99.9% uptime)

---

## Appendix

### API Specifications

See [API Documentation](./api_specs.md) (to be created)

### Database Migration Scripts

See [Migration Guide](./migrations/) (to be created)

### Frontend Component Specs

See [Component Library](./components.md) (to be created)

---

**Next Steps:**

1. **CEO Approval:** Review and approve PRD
2. **CTO Assignment:** Assign engineering resources
3. **Sprint Planning:** Break down into 2-week sprints
4. **Kickoff Meeting:** Align team on priorities
5. **Phase 1 Development:** Begin immediately upon approval

**Questions?** Contact CFO or schedule PRD review meeting.

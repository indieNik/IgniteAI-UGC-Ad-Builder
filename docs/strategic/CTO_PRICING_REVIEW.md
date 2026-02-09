# CTO Review: Pricing Strategy Implementation

**Review Date:** January 23, 2026  
**Reviewer:** CTO  
**Status:** 🟡 PENDING APPROVAL  
**Reference:** [CEO Pricing Strategy Decision](./../../.gemini/antigravity/brain/b0e80b70-2174-4064-bf1f-d7af2f882423/pricing_strategy_decision.md)

---

## Executive Summary

**Technical Feasibility:** ✅ **APPROVED** (with minor infrastructure changes)

**Implementation Complexity:** 🟢 LOW (2-week sprint)

**Key Technical Changes:**
1. Payment gateway: Add Stripe USD support
2. Pricing config: Update `product-content.ts` with USD tiers
3. Backend: Update Razorpay/Stripe integration
4. Database: No schema changes needed (credits are already integers)
5. Frontend: Currency display changes (₹ → $)

**Estimated Engineering Time:** 40-60 hours

---

## 1. Technical Architecture Review

### Current Payment Flow

```
User selects tier → Frontend → Backend API → Razorpay (INR) → Webhook → Credit allocation
```

### Proposed Payment Flow

```
User selects tier → Frontend → Backend API → Stripe/Razorpay (USD) → Webhook → Credit allocation
```

**Changes Required:**
- Add Stripe payment gateway (USD)
- Keep Razorpay (for INR fallback if needed)
- Update webhook handlers for both gateways
- Currency conversion utilities (if supporting both)

---

## 2. System Components Affected

### 2.1 Shared Content (Single Source of Truth)

**File:** `shared-content/product-content.ts`

**Changes:**
```typescript
// OLD (INR)
{
  name: 'Starter Pack',
  price: '₹499',
  priceNumeric: 499,
  currency: 'INR',
  credits: 15
}

// NEW (USD)
{
  name: 'Starter Pack',
  price: '$99',
  priceNumeric: 99,
  currency: 'USD',
  credits: 50
}
```

**Impact:** LOW (config change only)  
**Testing:** Sync script verification  
**Rollback:** Git revert (< 1 minute)

---

### 2.2 Backend Payment Service

**File:** `projects/backend/routers/payment.py`

**Changes:**
```python
# OLD
PRICING_TIERS = {
    "starter": {"amount_paise": 49900, "credits": 15},
    "builder": {"amount_paise": 399900, "credits": 100},
    "scale": {"amount_paise": 1199900, "credits": 500}
}

# NEW
PRICING_TIERS = {
    "starter": {"amount_cents": 9900, "credits": 50},  # $99
    "creator": {"amount_cents": 23900, "credits": 150},  # $239
    "growth": {"amount_cents": 59900, "credits": 500},  # $599
    "scale": {"amount_cents": 299900, "credits": 2000}  # $2,999
}
```

**Impact:** MEDIUM (payment logic changes)  
**Testing:** Unit tests + Stripe test mode  
**Rollback:** Feature flag (15 minutes)

---

### 2.3 Payment Gateway Integration

**Current:** Razorpay (INR)  
**Proposed:** Stripe (USD primary), Razorpay (INR fallback)

**Why Stripe?**
- Better USD support
- Lower transaction fees for international (2.9% vs 3.5%)
- Better developer experience (webhooks, test mode)
- Supports 135+ currencies (future expansion)

**Implementation:**
```python
# Install Stripe SDK
pip install stripe

# Environment variables
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Payment creation
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_stripe_checkout(tier: str):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': PRICING_TIERS[tier]['name']},
                'unit_amount': PRICING_TIERS[tier]['amount_cents'],
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f"{FRONTEND_URL}/payment/success",
        cancel_url=f"{FRONTEND_URL}/pricing"
    )
    return session.url
```

**Testing Requirements:**
- [ ] Test mode payments (Stripe test cards)
- [ ] Webhook signature verification
- [ ] Duplicate payment prevention
- [ ] Failed payment handling
- [ ] Refund flow (if needed)

**Rollback Plan:**
- Keep Razorpay code active
- Feature flag to switch between gateways
- Database tracks payment_gateway field

---

### 2.4 Frontend Components

**Files Affected:**
- `projects/frontend/src/app/pricing/pricing.component.ts`
- `projects/frontend/src/app/account-settings/account-settings.component.ts`
- `projects/landing/app/page.tsx` (Next.js)

**Changes:**
1. Currency symbol display (₹ → $)
2. Payment gateway integration (Razorpay → Stripe Checkout)
3. Tier name updates (`builder` → `creator`)
4. Feature list updates

**Example:**
```typescript
// OLD
buyPlan(tier: string) {
  this.paymentService.createOrder(tier).subscribe(order => {
    this.razorpay.open(order);
  });
}

// NEW
buyPlan(tier: string) {
  this.paymentService.createStripeCheckout(tier).subscribe(sessionUrl => {
    window.location.href = sessionUrl;  // Redirect to Stripe Checkout
  });
}
```

**Impact:** MEDIUM (UI changes, payment flow changes)  
**Testing:** E2E tests with Stripe test mode

---

### 2.5 Database Schema

**Good News:** ✅ No schema changes required!

**Why:**
- Credits are stored as integers (currency-agnostic)
- Payment amounts stored in cents/paise (already integers)
- Just need to add `currency` field to payments table

**Optional Enhancement:**
```sql
ALTER TABLE payments 
ADD COLUMN currency VARCHAR(3) DEFAULT 'USD';

ALTER TABLE payments
ADD COLUMN payment_gateway VARCHAR(20) DEFAULT 'stripe';
```

**Impact:** LOW (optional, backward compatible)

---

## 3. Infrastructure Changes

### 3.1 Secret Manager (GCP)

**New Secrets to Add:**
```bash
# Stripe credentials
echo "sk_live_..." | gcloud secrets create STRIPE_SECRET_KEY --data-file=-
echo "pk_live_..." | gcloud secrets create STRIPE_PUBLISHABLE_KEY --data-file=-
echo "whsec_..." | gcloud secrets create STRIPE_WEBHOOK_SECRET --data-file=-
```

**Cloud Run Service Update:**
```bash
gcloud run services update igniteai-backend \
  --set-secrets="STRIPE_SECRET_KEY=STRIPE_SECRET_KEY:latest,STRIPE_PUBLISHABLE_KEY=STRIPE_PUBLISHABLE_KEY:latest,STRIPE_WEBHOOK_SECRET=STRIPE_WEBHOOK_SECRET:latest"
```

**Impact:** LOW (standard secret management)

---

### 3.2 Environment Variables

**New Variables:**
```env
# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Currency
DEFAULT_CURRENCY=USD

# Feature Flags
ENABLE_STRIPE=true
ENABLE_RAZORPAY_FALLBACK=true
```

---

### 3.3 Monitoring & Logging

**Add Logging for:**
- Payment gateway selection (Stripe vs Razorpay)
- Currency conversion (if supporting both)
- Failed payments (with reasons)
- Webhook failures

**Monitoring Alerts:**
- Payment success rate < 95%
- Webhook delivery failures
- Duplicate payment attempts
- Stripe API errors

---

## 4. Testing Strategy

### 4.1 Unit Tests

**Backend:**
```python
# test_payment.py
def test_starter_pack_usd_pricing():
    tier = PRICING_TIERS["starter"]
    assert tier["amount_cents"] == 9900  # $99
    assert tier["credits"] == 50

def test_stripe_checkout_creation():
    session_url = create_stripe_checkout("starter")
    assert "checkout.stripe.com" in session_url

def test_webhook_signature_verification():
    # Use Stripe test webhook signature
    ...
```

**Frontend:**
```typescript
// payment.service.spec.ts
it('should format USD currency correctly', () => {
  expect(service.formatPrice(99, 'USD')).toBe('$99');
  expect(service.formatPrice(239, 'USD')).toBe('$239');
});

it('should redirect to Stripe Checkout', () => {
  service.createStripeCheckout('starter').subscribe(url => {
    expect(url).toContain('checkout.stripe.com');
  });
});
```

---

### 4.2 Integration Tests

**Stripe Test Mode:**
```bash
# Test cards
4242 4242 4242 4242  # Success
4000 0000 0000 0002  # Declined
4000 0025 0000 3155  # Requires authentication
```

**Test Flow:**
1. Select Starter Pack → Redirects to Stripe Checkout
2. Enter test card → Payment succeeds
3. Webhook fired → Credits added
4. Verify database: 50 credits, $99 payment record

---

### 4.3 Load Testing

**Webhook Handling:**
- Simulate 100 concurrent webhook deliveries
- Verify idempotency (duplicate webhooks handled)
- Check database race conditions

**Payment Creation:**
- 50 concurrent users selecting different tiers
- Verify no order ID collisions
- Check Cloud Run autoscaling

---

## 5. Deployment Strategy

### 5.1 Phased Rollout

**Phase 1: Staging (Feb 1-7)**
- Deploy pricing changes to staging
- Test with Stripe test mode
- Run E2E tests
- Team QA

**Phase 2: Canary (Feb 8-10)**
- 10% of users see new pricing (feature flag)
- Monitor conversion rates
- Track errors/bugs

**Phase 3: Full Launch (Feb 18)**
- 100% of users on new pricing
- Remove feature flag
- Monitor for 48 hours

---

### 5.2 Feature Flags

```python
# Use LaunchDarkly or simple config
FEATURE_FLAGS = {
    "enable_usd_pricing": {
        "enabled": True,
        "rollout_percentage": 100  # Start at 10%, ramp to 100%
    }
}

def get_pricing_currency(user_id: str):
    if is_user_in_rollout(user_id, "enable_usd_pricing"):
        return "USD"
    return "INR"  # Fallback to old pricing
```

---

### 5.3 Rollback Plan

**If issues detected:**
1. Set feature flag `enable_usd_pricing` to 0%
2. All users revert to INR pricing
3. No database rollback needed
4. **Rollback time:** < 5 minutes

**Rollback Triggers:**
- Payment success rate < 80%
- Webhook failure rate > 5%
- Customer support tickets > 50/day
- Stripe API downtime

---

## 6. Security Considerations

### 6.1 Stripe Webhook Security

**Signature Verification:**
```python
import stripe

def verify_webhook(payload, sig_header):
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        return event
    except ValueError:
        return None  # Invalid payload
    except stripe.error.SignatureVerificationError:
        return None  # Invalid signature
```

**Why:** Prevents malicious POST requests faking payments

---

### 6.2 Idempotency

**Problem:** Stripe may send same webhook multiple times

**Solution:**
```python
@app.post("/webhooks/stripe")
def stripe_webhook(request: Request):
    event_id = event['id']
    
    # Check if already processed
    if redis.exists(f"webhook_{event_id}"):
        return {"status": "duplicate"}
    
    # Process payment
    add_credits(user_id, credits)
    
    # Mark as processed (expire after 24h)
    redis.setex(f"webhook_{event_id}", 86400, "1")
```

---

### 6.3 PCI Compliance

**Good News:** Using Stripe Checkout means we're PCI-DSS compliant by default
- Stripe hosts payment form (we never touch card data)
- No PCI audit needed
- Reduced liability

---

## 7. Cost Optimization (AI Models)

### 7.1 Negotiate Google Bulk Pricing

**Current Cost:** $0.15/sec (Veo 3.1)  
**Target Cost:** $0.10/sec (33% reduction)

**Approach:**
- Contact Google Cloud sales
- Commit to $50K/year spend
- Negotiate enterprise pricing

**Impact:**
- COGS: $1.03 → $0.73/credit
- Gross margin: 38% → 52%

**Timeline:** Q2 2026

---

### 7.2 Mixed Media Strategy

**Optimization:** Use Imagen ($0.04) for 50% of scenes

**Example:**
```
Scene 1: Imagen static image + voiceover
Scene 2: Veo video (action shot)
Scene 3: Imagen static image
Scene 4: Veo video (CTA)
```

**Savings:** ~$1.80/video (45% reduction)

**Implementation:**
- Add "scene_type" field: "static" | "video"
- Template engine chooses based on scene
- User can override in editor

---

## 8. Technical Debt & Future Considerations

### 8.1 Multi-Currency Support

**Future State (2027):**
- USD (primary)
- EUR (Europe)
- GBP (UK)
- INR (India)
- AUD (Australia)

**Architecture:**
```typescript
interface PricingTier {
  credits: number;
  prices: {
    USD: number;
    EUR: number;
    GBP: number;
    INR: number;
  };
}
```

**Implementation Effort:** 2 weeks

---

### 8. 2 Subscription Model (Future)

**Current:** One-time purchases (credits never expire)  
**Future:** Hybrid (credits + monthly subscription)

**Example:**
- $49/month for 50 credits/month (20% cheaper than one-time)
- Credits expire end of month
- Cancel anytime

**Why Later:** Need to validate credit-based model first

---

## 9. Technical Approval Checklist

**Pre-Launch:**
- [ ] Stripe account created (live mode)
- [ ] Webhook endpoint deployed and tested
- [ ] Payment success/failure flows tested
- [ ] Credits allocation verified
- [ ] Frontend UI updated (USD symbols)
- [ ] Content sync script tested
- [ ] Feature flag system ready
- [ ] Monitoring/alerts configured
- [ ] Rollback procedure documented

**Post-Launch:**
- [ ] Monitor payment success rate (target: >95%)
- [ ] Monitor webhook delivery (target: 100%)
- [ ] Track Stripe API errors
- [ ] Monitor customer support tickets

---

## 10. CTO Decision

**Status:** ✅ **APPROVED**

**Conditions:**
1. Complete Stripe integration testing by Feb 7
2. Deploy to staging by Feb 8
3. Feature flag rollout (10% → 50% → 100%)
4. Daily monitoring first week post-launch

**Implementation Timeline:**
- Feb 1-7: Development (40 hours)
- Feb 8-10: Staging testing
- Feb 11-14: Canary rollout (10%)
- Feb 15-17: Ramp to 100%
- Feb 18: Full launch

**Signature:** _________________________  
**Date:** January 23, 2026

**Next Review:** February 25, 2026 (post-launch review)

---

> [!NOTE]
> **CTO Comments:** This is a straightforward pricing config change. Stripe integration is well-documented and battle-tested. The biggest risk is payment gateway downtime, but we can fallback to Razorpay if needed. Feature flag rollout minimizes risk. Approve.

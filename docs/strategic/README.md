# Strategic Documents Index

**Last Updated:** January 23, 2026  
**Owner:** Executive Team

---

## Purpose

This directory contains all strategic documents that guide IgniteAI's direction, decisions, and execution. **All future work should reference these documents** to ensure alignment with company vision and approved strategies.

---

## Document Hierarchy

### 1. Foundation Documents (Read First)

#### [VISION.md](./VISION.md)
**What:** Company mission, 3-year roadmap, core values, success metrics  
**Who Should Read:** Everyone (required reading for all team members)  
**When to Reference:** Product decisions, hiring, partnerships, strategy pivots  
**Next Review:** July 2026 or upon hitting 1,000 paying customers

---

### 2. Pricing Strategy (January 2026)

#### [PRICING_STRATEGY.md](./PRICING_STRATEGY.md)
**What:** CEO-approved USD pricing structure ($99-$2,999 tiers)  
**Status:** ✅ Approved for Feb 18, 2026 launch  
**Key Decisions:**
- Free: $0 / 10 credits
- Starter: $99 / 50 credits (48% margin)
- Creator: $239 / 150 credits (35% margin)
- Growth: $599 / 500 credits (14% margin)
- Scale: $2,999 / 2,000 credits (31% margin)

**When to Reference:**
- Pricing page updates
- Marketing campaigns
- Customer support (grandfather clause questions)
- Financial reporting

---

#### [CFO_PRICING_REVIEW.md](./CFO_PRICING_REVIEW.md)
**What:** Financial analysis, unit economics, projections, approval conditions  
**Status:** ✅ Approved (with cash reserve requirement)  
**Key Metrics:**
- COGS per credit: $1.03
- Blended margin: 38%
- Breakeven: 35 paid customers/month
- Projected MRR: $18,540

**When to Reference:**
- Budget planning
- Investor pitches
- Cost optimization initiatives
- Performance reviews

---

#### [CTO_PRICING_REVIEW.md](./CTO_PRICING_REVIEW.md)
**What:** Technical implementation plan, Stripe integration, testing strategy  
**Status:** ✅ Approved (40-60 hours implementation)  
**Key Changes:**
- Add Stripe USD payment gateway
- Update `product-content.ts` pricing
- Feature flag rollout (10% → 100%)
- Monitoring/alerts setup

**When to Reference:**
- Payment gateway issues
- Pricing config changes
- Feature flag management
- Deployment planning

---

#### [LEGAL_PRICING_REVIEW.md](./LEGAL_PRICING_REVIEW.md)
**What:** Terms of Service updates, compliance requirements, risk assessment  
**Status:** ✅ Approved (with TOS update requirement)  
**Key Requirements:**
- 14-day advance notice (email Feb 8)
- Grandfather clause (60 days old pricing)
- No-refund policy (with exception for tech issues)
- Tax consultation (GST on USD pricing)

**When to Reference:**
- Customer disputes
- Refund requests
- TOS updates
- Legal compliance questions

---

#### [MARKETING_PRICING_REVIEW.md](./MARKETING_PRICING_REVIEW.md)
**What:** Communication strategy, email campaigns, objection handling  
**Status:** ✅ Approved (with campaign execution requirement)  
**Key Deliverables:**
- 3-part email series (Feb 8, 12, 17)
- Blog post: "Why We're Changing Pricing"
- FAQ page: `/pricing-faq`
- Support training: Objection handling guide

**When to Reference:**
- Customer communications
- Support ticket responses
- Content marketing
- Social media posts

---

## How to Use These Documents

### For Product Decisions
1. Read [VISION.md](./VISION.md) for strategic alignment
2. Check if decision impacts pricing → Reference [PRICING_STRATEGY.md](./PRICING_STRATEGY.md)
3. Estimate cost impact → Reference [CFO_PRICING_REVIEW.md](./CFO_PRICING_REVIEW.md)
4. Plan technical implementation → Reference [CTO_PRICING_REVIEW.md](./CTO_PRICING_REVIEW.md)

### For Customer Support
1. Pricing questions → [MARKETING_PRICING_REVIEW.md](./MARKETING_PRICING_REVIEW.md) (objection handling)
2. Refund requests → [LEGAL_PRICING_REVIEW.md](./LEGAL_PRICING_REVIEW.md) (TOS policy)
3. Grandfather clause → [PRICING_STRATEGY.md](./PRICING_STRATEGY.md) (dates and eligibility)

### For Marketing Campaigns
1. Messaging → [VISION.md](./VISION.md) (value propositions)
2. Pricing communication → [MARKETING_PRICING_REVIEW.md](./MARKETING_PRICING_REVIEW.md) (templates)
3. Competitive positioning → [PRICING_STRATEGY.md](./PRICING_STRATEGY.md) (benchmarking)

### For Engineering
1. Payment integration → [CTO_PRICING_REVIEW.md](./CTO_PRICING_REVIEW.md)
2. Feature priorities → [VISION.md](./VISION.md) (roadmap)
3. Cost optimization → [CFO_PRICING_REVIEW.md](./CFO_PRICING_REVIEW.md) (COGS reduction)

---

## Document Update Policy

### Who Can Update?
- **VISION.md:** CEO only (quarterly review)
- **Pricing Docs:** Requires cross-functional approval (CEO, CFO, CTO, Legal, Marketing)
- **Review Docs:** Respective department heads

### When to Update?
- Major strategy pivots
- Quarterly reviews
- Post-launch retrospectives
- When metrics significantly deviate from projections

### How to Update?
1. Create new version with date suffix (e.g., `VISION_2026_Q2.md`)
2. Update this README with change log
3. Archive old version in `docs/strategic/archive/`
4. Communicate changes to team via Slack/email

---

## Quick Reference

| Need | Document | Section |
|------|----------|---------|
| Company mission | VISION.md | "Our Mission" |
| Pricing tiers | PRICING_STRATEGY.md | Section 3 |
| Unit economics | CFO_PRICING_REVIEW.md | Section 1 |
| Customer email templates | MARKETING_PRICING_REVIEW.md | Section 2 |
| Payment integration guide | CTO_PRICING_REVIEW.md | Section 2.3 |
| Refund policy | LEGAL_PRICING_REVIEW.md | TOS Updates |
| Objection handling | MARKETING_PRICING_REVIEW.md | Section 4 |
| Cost optimization roadmap | CFO_PRICING_REVIEW.md | Section 5 |

---

## Approval Status Summary

| Document | CEO | CFO | CTO | Legal | Marketing |
|----------|-----|-----|-----|-------|-----------|
| VISION.md | ✅ | - | - | - | - |
| PRICING_STRATEGY.md | ✅ | ⏳ | ⏳ | ⏳ | ⏳ |
| CFO_PRICING_REVIEW.md | - | ✅ | - | - | - |
| CTO_PRICING_REVIEW.md | - | - | ✅ | - | - |
| LEGAL_PRICING_REVIEW.md | - | - | - | ✅ | - |
| MARKETING_PRICING_REVIEW.md | - | - | - | - | ✅ |

**Legend:** ✅ Approved | ⏳ Pending | ❌ Rejected

---

## Next Steps

1. Complete remaining approvals (CFO, CTO, Legal, Marketing on pricing strategy)
2. Execute marketing campaign (Feb 1-18)
3. Deploy pricing changes (Feb 18)
4. Monitor metrics (churn, conversion, MRR)
5. Post-launch retrospective (Mar 15)
6. Update VISION.md based on learnings (Q2 review)

---

**Questions?** Contact the document owner or bring to weekly leadership meeting.

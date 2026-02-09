# CEO → CTO Handover: Pricing System Improvements

**From:** CEO/CFO  
**To:** CTO  
**Date:** January 23, 2026  
**Priority:** P0 CRITICAL  
**Subject:** Implementation of Emergency Pricing Fixes & Subscription System

---

## Executive Summary

Following comprehensive CFO analysis of our pricing model, we've identified **critical margin vulnerabilities** requiring immediate technical implementation. Current system creates negative unit economics on videos >45 seconds.

**Bottom Line:** We're losing money on every video longer than 45 seconds. Phase 1 must ship within 2 weeks to stop the bleeding.

---

## Your Mission

Implement 4-phase pricing improvements:

1. **Phase 1 (P0 - 2 weeks):** Emergency COGS protection
2. **Phase 2 (P1 - 6 weeks):** USD subscription system  
3. **Phase 3 (P1 - 12 weeks):** Self-hosted GPU infrastructure
4. **Phase 4 (P2 - 16 weeks):** Agency white-label features

**Complete documentation:**
📄 [Product Requirements Document](./pricing_improvements_prd.md) - **READ THIS FIRST**

---

## Phase 1: Immediate Action Required (P0)

**Timeline:** 2 weeks from approval  
**Impact:** Stops negative margins immediately

### What You're Building

1. **Duration-Based Pricing**
   - Charge 1 credit per 30 seconds of video
   - Backend: Update `pricing_service.py`
   - Frontend: Add duration selector in editor
   - Database: Add `video_duration_seconds`, `credits_charged` columns

2. **Weighted Credits System**
   - Generative background: +2 credits
   - Premium TTS: +1 credit
   - 4K resolution: +1 credit
   - Frontend: Feature toggles with real-time cost display

3. **Admin Margin Dashboard**
   - Track COGS vs revenue per campaign
   - Alert on negative margins
   - New endpoint: `GET /api/admin/margins`
   - Requires COGS logging on all API calls

4. **Grandfather Clause**
   - Existing users keep 1 credit/video rate
   - Once their credits run out, new pricing applies
   - Database: Add `grandfathered` boolean flag

### Technical Specs

All detailed specs, code samples, API endpoints, database schemas, and acceptance criteria are in the **[PRD document](./pricing_improvements_prd.md)**.

**Key files to modify:**
- `projects/backend/services/pricing_service.py`
- `projects/backend/routers/campaigns.py`
- `projects/frontend/src/app/campaigns/editor.component.ts`
- `projects/frontend/src/app/admin/margin-dashboard.component.ts` (new)
- Database migrations for `campaigns`, `users` tables

---

## Phase 2: USD Subscription System (P1)

**Timeline:** 4-6 weeks after Phase 1  
**Impact:** Enables $1.2M+ ARR potential

### What You're Building

1. **Stripe Integration**
   - Backend: `stripe_service.py` (new)
   - Webhook handling for subscription events
   - Monthly credit renewal automation

2. **Subscription Management**
   - New database table: `subscriptions`
   - Endpoints: Create session, manage subscription, cancel
   - Frontend: New pricing page with monthly/annual toggle

3. **Recommended Pricing Tiers**
   - Starter: $49/month (40 credits)
   - Growth: $149/month (150 credits)
   - Agency: $497/month (600 credits)

**Stripe setup required:**
- Business verification
- Webhook endpoint configuration
- Test mode → production migration plan

---

## Phase 3: Self-Hosted Infrastructure (P1)

**Timeline:** 8-12 weeks after Phase 2  
**Requires:** Budget approval ($1-2K/month GPU + engineer)  
**Impact:** 94% COGS reduction ($5.61 → $0.32 per video)

### What You're Building

1. **Reserved GPU Procurement**
   - 2x A100 40GB instances (GCP)
   - Auto-scaling to 5x during peak

2. **LivePortrait Deployment**
   - Open-source face animation model
   - Replace Runway ML API
   - Fallback to API if GPU unavailable

3. **Open-Source TTS**
   - Replace ElevenLabs with Coqui/Bark
   - Deploy on same GPU instances

**Warning:** This is a full infrastructure project. Consider hiring ML Ops contractor ($3K/mo) if internal capacity limited.

---

## Phase 4: Agency Features (P2)

**Timeline:** 12-16 weeks  
**Impact:** Unlock $5-10K MRR from agency tier

1. **White-Label Mode**
   - Custom branding (logo, colors)
   - Remove IgniteAI branding from exports

2. **REST API**
   - All endpoints accessible via API key
   - Rate limiting (100 req/min)
   - Webhook notifications
   - OpenAPI docs + SDKs

3. **Multi-Tenant**
   - Sub-account management
   - Usage reporting per seat

---

## Resources Provided

### Documentation
1. **[Product Requirements Document](./pricing_improvements_prd.md)** (92 pages)
   - Complete technical specs
   - Database schemas
   - API endpoint definitions
   - Frontend component requirements
   - Testing requirements
   - Deployment strategy

2. **[CFO Report to CEO](../../.gemini/antigravity/brain/2d61d8ef-536d-4375-99b4-44a908603a2e/cfo_report_to_ceo.md)**
   - Strategic rationale
   - Financial projections
   - Risk assessment

3. **[Pricing Strategy 2026](../reports/pricing_strategy_2026.md)**
   - Market analysis
   - Competitive positioning
   - Success metrics

### Code Documentation
- `shared-content/product-content.ts` - Updated with strategic context
- `CHANGELOG.md` - v1.6.0 entry documenting analysis
- `GEMINI.md` - Full pricing evolution learnings

---

## Success Metrics

### Phase 1 (Week 2 after launch)
- ✅ Zero campaigns with negative margins
- ✅ Average margin >40% (vs <0% before)
- ✅ Admin dashboard operational
- ✅ <5% increase in support tickets

### Phase 2 (Month 2)
- ✅ 50+ new subscribers
- ✅ MRR >$10K
- ✅ <10% monthly churn
- ✅ 30% of existing users migrated

### Phase 3 (Month 4)
- ✅ COGS <$0.50 per 30s video
- ✅ Gross margin >80%
- ✅ Video quality maintained

### Phase 4 (Month 6)
- ✅ 10+ agency customers
- ✅ Agency MRR >$5K
- ✅ API uptime >99.9%

---

## Team & Budget

### Phase 1 Team (Immediate)
- **Backend Engineer:** 1 FTE (2 weeks)
- **Frontend Engineer:** 0.5 FTE (1 week)
- **QA:** 0.5 FTE (1 week)

### Phase 2 Team
- **Backend Engineer:** 1 FTE (4 weeks)
- **Frontend Engineer:** 1 FTE (3 weeks)
- **QA:** 0.5 FTE (2 weeks)

### Phase 3 Team (Budget Approval Required)
- **MLOps Engineer:** 1 FTE or contractor ($3-12K/month)
- **Infrastructure:** $1-2K/month Reserved GPUs
- **One-Time:** $5K model optimization

### Phase 4 Team
- **Backend Engineer:** 1 FTE (6 weeks)
- **Frontend Engineer:** 0.5 FTE (4 weeks)
- **DevOps:** 0.5 FTE (2 weeks)

---

## Risks & Mitigation

### Technical Risks

**Risk:** Credit calculation bugs create customer complaints  
**Mitigation:** 100% unit test coverage, manual QA, gradual rollout

**Risk:** Database migration fails  
**Mitigation:** Test on staging, rollback script ready, deploy off-peak

**Risk:** Stripe integration issues  
**Mitigation:** Test thoroughly in Stripe test mode, webhook retry logic

**Risk:** GPU service downtime  
**Mitigation:** Automatic fallback to Runway ML API

### Business Risks

**Risk:** Existing user churn due to pricing changes  
**Mitigation:** Grandfather clause, clear communication, 40% migration discount

**Risk:** Subscription conversion <30%  
**Mitigation:** A/B test pricing page, customer surveys, optimize messaging

---

## Next Steps

### Immediate (This Week)
1. **CTO:** Review complete PRD document
2. **CTO:** Confirm Phase 1 team availability
3. **CTO:** Raise any technical concerns/blockers
4. **CEO/CTO:** Align on Phase 1 timeline (2 weeks feasible?)

### Week 1
1. **Kickoff Meeting:** Engineering team alignment
2. **Sprint Planning:** Break Phase 1 into tasks
3. **Database Migration:** Design and test on staging
4. **Begin Development:** Backend pricing logic

### Week 2
1. **Backend Complete:** Duration + weighted credits
2. **Frontend Development:** Editor UI updates
3. **Admin Dashboard:** Margin monitoring
4. **QA Testing:** All acceptance criteria

### Week 3
1. **Deploy to Production:** Off-peak hours
2. **Monitor Margins:** 48-hour intensive monitoring
3. **User Communication:** Email explaining changes
4. **Support Readiness:** FAQs prepared

---

## Key Deliverables Expected

### Phase 1 Deliverables (Due: 2 weeks from start)

1. **Backend:**
   - `pricing_service.py` with duration + weighted credit logic
   - `/api/admin/margins` endpoint
   - COGS tracking on all API calls
   - Database migrations applied

2. **Frontend:**
   - Duration selector in editor
   - Premium feature toggles with cost display
   - Admin margin dashboard
   - Grandfathered user badge

3. **Testing:**
   - Unit tests (100% coverage on pricing logic)
   - Integration tests (full campaign flow)
   - Manual QA sign-off

4. **Documentation:**
   - API documentation updated
   - Internal technical docs
   - Runbook for deployment

---

## Communication

### Meetings

**Daily Standups:** 15 min, 9 AM (during Phase 1 development)  
**Weekly Check-In:** CEO/CTO alignment (Fridays, 30 min)  
**PRD Review Meeting:** Schedule before starting (1 hour)

### Reporting

**Weekly Status Report:** Email to CEO with:
- Progress against timeline
- Blockers identified
- Resource needs
- Risk updates

**Launch Readiness:** 48 hours before deployment:
- Go/No-Go decision
- Rollback plan confirmed
- Support team briefed

---

## Questions or Concerns?

**Technical Questions:** Review PRD first, then schedule 30-min deep dive  
**Resource Needs:** Escalate immediately if team unavailable  
**Timeline Concerns:** Discuss ASAP - Phase 1 is critical path  
**Budget Approval:** Required for Phase 3 (Reserved GPUs)

---

## Final Notes

**This is our highest priority technical work.** Current pricing model creates existential risk (negative margins). Phase 1 must ship to stop bleeding money.

**The PRD is comprehensive.** Every technical detail, code sample, database schema, and acceptance criterion is documented. Read it thoroughly before starting.

**We're here to support.** CEO/CFO available for clarifications, business context, or helping remove blockers.

**Let's ship this.** 🚀

---

**Approval Status:**
- [ ] CEO Approved
- [ ] CTO Reviewed PRD
- [ ] Team Assigned
- [ ] Timeline Confirmed
- [ ] Phase 1 Kickoff Scheduled

**Once approved, update this doc with team assignments and kickoff date.**

---

**Document Version:** 1.0  
**Last Updated:** January 23, 2026  
**Next Review:** After Phase 1 completion

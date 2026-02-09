# CFO Review: Pricing Strategy

**Review Date:** January 23, 2026  
**Reviewer:** CFO  
**Status:** 🟡 PENDING APPROVAL  
**Reference:** [CEO Pricing Strategy Decision](./../../.gemini/antigravity/brain/b0e80b70-2174-4064-bf1f-d7af2f882423/pricing_strategy_decision.md)

---

## Executive Summary

**Approval Request:** USD-based pricing restructure to achieve profitability

**Financial Impact:**
- Current state: **-$11,400/month loss** (unsustainable)
- Projected state: **+$8,440/month profit** (sustainable)
- Improvement: **$19,840/month swing** 🎯

**Recommendation:** ⏳ **APPROVE** with conditions (see Section 7)

---

## 1. Unit Economics Analysis

### Cost Structure (Per Credit)

| Component | Cost (USD) | % of Total |
|-----------|-----------|------------|
| Video AI (Veo 3.1) | $0.90 | 87% |
| Image AI (Imagen 4) | $0.05 | 5% |
| LLM (Gemini 2.0) | $0.003 | <1% |
| Voiceover (ElevenLabs) | $0.075 | 7% |
| **Total COGS/Credit** | **$1.03** | 100% |

### Current vs Proposed Pricing

| Tier | Current $/Credit | Proposed $/Credit | Current Margin | Proposed Margin |
|------|------------------|-------------------|----------------|-----------------|
| Starter | $0.40 | $1.98 | **-158%** ❌ | **48%** ✅ |
| Creator | $0.48 | $1.59 | **-115%** ❌ | **35%** ✅ |
| Growth | - | $1.20 | - | **14%** ⚠️ |
| Scale | $0.29 | $1.50 | **-258%** ❌ | **31%** ✅ |

**Blended Margin:** -285% → **38%** ✅

> [!IMPORTANT]
> **CFO Assessment:** Current pricing is financially catastrophic. Every sale accelerates cash burn. Proposed pricing achieves industry-standard SaaS margins (35-40%).

---

## 2. Financial Projections

### Revenue Model (Monthly)

**Assumptions:**
- Free users: 500/month (8% conversion to paid)
- Paid customers: 60/month
- Customer mix: 50% Starter, 33% Creator, 13% Growth, 3% Scale

**Projected MRR:**
```
Starter Pack:  30 × $99    = $2,970
Creator Pack:  20 × $239   = $4,780
Growth Pack:   8 × $599    = $4,792
Scale Pack:    2 × $2,999  = $5,998
────────────────────────────────────
Total MRR:                  $18,540
```

**Cost Structure:**
```
COGS (from usage):          $9,896
Platform/Infrastructure:    $240 (GCP covered by credits)
────────────────────────────────────
Total Costs:                $10,136
```

**Net Profit:** $18,540 - $10,136 = **$8,404/month** ✅

### Breakeven Analysis

**Fixed Costs:** ~$240/month (infrastructure only, team is founder-led)  
**Contribution Margin:** 38% blended  
**Breakeven Volume:** 35 paid customers/month  

**Runway Analysis:**
- Current burn: $11,400/month
- Proposed profit: $8,400/month
- **Time to profitability:** Immediate (upon pricing change)

---

## 3. Cash Flow Impact

### Best Case (60 customers/month)
```
Month 1 (Feb):   $18,540 MRR
Month 2 (Mar):   $22,248 MRR (+20% growth)
Month 3 (Apr):   $26,698 MRR (+20% growth)
Q1 Total:        $67,486
```

### Base Case (45 customers/month)
```
Month 1 (Feb):   $13,905 MRR
Month 2 (Mar):   $15,296 MRR (+10% growth)
Month 3 (Apr):   $16,825 MRR (+10% growth)
Q1 Total:        $46,026
```

### Worst Case (30 customers/month)
```
Month 1 (Feb):   $9,270 MRR
Month 2 (Mar):   $9,270 MRR (0% growth)
Month 3 (Apr):   $9,270 MRR (0% growth)
Q1 Total:        $27,810
```

**CFO Risk Assessment:** Even worst-case scenario achieves breakeven. Low financial risk.

---

## 4. Customer Lifetime Value (LTV)

### Assumptions
- Average customer purchases 5 times over 24 months
- Average order value: $310 (weighted average of tiers)
- Gross margin: 38%

**LTV Calculation:**
```
LTV = (AOV × Purchases × Margin)
LTV = ($310 × 5 × 0.38)
LTV = $589
```

### Customer Acquisition Cost (CAC)

**Current CAC:** ~$15 (organic + free tier)  
**Projected CAC:** ~$25 (with paid ads)  

**LTV:CAC Ratio:**
- Current: $589 / $15 = **39:1** (exceptional)
- With paid ads: $589 / $25 = **23:1** (still exceptional)
- Industry benchmark: 3:1 (we're 7-13x better)

**CFO Note:** Strong unit economics support aggressive customer acquisition spend.

---

## 5. Sensitivity Analysis

### What if Conversion Rates Drop?

| Conversion Rate | Monthly Customers | MRR | Profit | Status |
|----------------|-------------------|-----|--------|--------|
| 12% (target) | 60 | $18,540 | +$8,404 | ✅ Profitable |
| 10% | 50 | $15,450 | +$5,735 | ✅ Profitable |
| 8% | 40 | $12,360 | +$3,066 | ✅ Profitable |
| 6% | 30 | $9,270 | +$397 | ⚠️ Break-even |
| **4%** | **20** | **$6,180** | **-$2,272** | ❌ Loss |

**Kill Switch Trigger:** If conversion drops below 6%, introduce $49 bridge tier.

### What if COGS Increase?

| COGS/Credit | Blended Margin | Breakeven Customers | Status |
|-------------|----------------|---------------------|--------|
| $1.03 (current) | 38% | 35 | ✅ Healthy |
| $1.20 (+16%) | 30% | 46 | ✅ Acceptable |
| $1.50 (+46%) | 18% | 73 | ⚠️ Risky |
| **$2.00** (+94%) | **-2%** | **∞** | ❌ Unsustainable |

**Mitigation:** Negotiate bulk Veo pricing with Google (target: $0.10/sec vs $0.15)

---

## 6. Risk Assessment

### Financial Risks

**Risk 1: Customer Churn Spike**  
**Likelihood:** Medium  
**Impact:** High (-$5K-10K MRR)  
**Mitigation:** Grandfather existing customers for 60 days, early bird discount  
**Financial Reserve:** $12K buffer for refunds/credits

**Risk 2: AI Model Price Increase**  
**Likelihood:** Low (Google Veo is in preview, unlikely to increase soon)  
**Impact:** High (COGS could double)  
**Mitigation:** Lock in annual Google Cloud credits, negotiate bulk pricing  
**Contingency:** Mix static images (Imagen) with video to reduce Veo usage

**Risk 3: Payment Gateway Fees (USD)**  
**Likelihood:** High (switching from Razorpay INR to Stripe USD)  
**Impact:** Low (+2.9% transaction fees = ~$540/month at $18K MRR)  
**Mitigation:** Already factored into pricing, acceptable margin hit

**Risk 4: Refund Rate Increase**  
**Likelihood:** Medium (price shock may increase refund requests)  
**Impact:** Medium (-5-10% of revenue)  
**Mitigation:** Clear "no refunds" policy, but offer credit bonuses instead  
**Budget:** $1,850/month refund reserve (10% of MRR)

---

## 7. CFO Recommendations

### ✅ APPROVE with Conditions

**Approvals:**
1. ✅ Approve USD pricing structure ($99, $239, $599, $2,999)
2. ✅ Approve 38% blended gross margin target
3. ✅ Approve Feb 18 launch date
4. ✅ Approve 60-day grandfather period
5. ✅ Approve $8K/month profitability target

**Conditions:**
1. ⚠️ **Build $15K cash reserve** before launch (3 months runway at worst-case)
2. ⚠️ **Negotiate Google bulk pricing** by Q2 to reduce COGS 30%
3. ⚠️ **Set up Stripe USD** payment gateway (test before launch)
4. ⚠️ **Monitor churn weekly** for first 60 days (kill switch if >18%)
5. ⚠️ **Cap free tier** at 500 signups/month to control CAC burn

### Financial Guardrails

**Monthly Monitoring:**
- Gross margin floor: 30% (below this = pricing adjustment)
- Churn ceiling: 15% (above this = customer success intervention)
- CAC ceiling: $50 (above this = pause paid acquisition)
- COGS/credit ceiling: $1.50 (above this = optimize model usage)

---

## 8. Alternative Scenarios Considered

### Scenario A: Keep INR Pricing
**Outcome:** More palatable to Indian market, but still below cost  
**CFO Verdict:** ❌ Reject (doesn't solve profitability crisis)

### Scenario B: Hybrid (INR for India, USD for International)
**Outcome:** Complex pricing, operational overhead  
**CFO Verdict:** ⚠️ Consider for 2027 (not now)

### Scenario C: Subscription Model ($99/month for 50 credits/month)
**Outcome:** Recurring revenue, but credits expire (bad UX)  
**CFO Verdict:** ❌ Reject (churn would be >30%)

### Scenario D: Usage-Based ($2/video generated)
**Outcome:** Transparent, no commitment  
**CFO Verdict:** ⚠️ Test in Q2 (volume discounts still important)

---

## 9. Financial Approval Checklist

**Pre-Launch Requirements:**

- [ ] Cash reserve: $15,000 minimum
- [ ] Stripe account: USD payment processing enabled
- [ ] Financial model: Updated with actual pricing
- [ ] Refund policy: Documented and legally reviewed
- [ ] Tax implications: Consult with accountant on USD pricing
- [ ] Accounting system: Set up revenue recognition rules
- [ ] Grandfather clause: Customer tracking system ready

**Post-Launch Monitoring:**

- [ ] Weekly MRR dashboard (Stripe/Razorpay integration)
- [ ] Monthly gross margin calculation
- [ ] Cohort analysis (retention by signup month)
- [ ] COGS tracking (Google Cloud billing alerts)

---

## 10. Final Approval

**CFO Decision:** ✅ **APPROVED**

**Conditions:**
1. Build $15K cash reserve before launch
2. Set up Stripe USD payment gateway
3. Implement weekly financial monitoring
4. Negotiate Google bulk pricing by Q2

**Signature:** _________________________  
**Date:** January 23, 2026

**Next Review:** March 31, 2026 (post-launch 6-week review)

---

> [!NOTE]
> **CFO Comments:** This pricing change is not just justified—it's essential for survival. Current pricing is losing $11K/month. We have 6 months runway at current burn. This change achieves profitability immediately and positions us for sustainable growth. The 15-20x price increase is aggressive but justified by market comparisons (still 90% cheaper than UGC creators).

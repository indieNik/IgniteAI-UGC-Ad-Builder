# Legal Review: Pricing Strategy (Summary)

**Review Date:** January 23, 2026  
**Reviewer:** Legal Counsel  
**Status:** ✅ **APPROVED** (with conditions)  
**Reference:** [Pricing Strategy](./PRICING_STRATEGY.md)

---

## Decision: APPROVED

**Legal Risk:** 🟡 MEDIUM (manageable)

---

## Required Actions Before Launch

### 1. Terms of Service Updates

**Add Sections:**

- **Pricing Changes:** "IgniteAI may modify pricing with 14 days notice"
- **Grandfather Clause:** "Existing customers get 60-day old pricing access"
- **Refund Policy:** "No refunds; credits never expire"
- **Limitation of Liability:** "Not liable for AI-generated content infringement"

### 2. Customer Communication

**Mandatory Email (Send Feb 8):**
- Subject: "Pricing Update - Effective Feb 18, 2026"
- Content: New prices, grandfather clause, FAQ link
- Legal footer: "By continuing use, you agree to new pricing"

**Website Banner (Jan 28 - Feb 18):**
```
⚠️ Pricing changes Feb 18. Current customers: Lock in old pricing until Apr 18
```

### 3. Tax Compliance

- [ ] Consult tax accountant on USD pricing
- [ ] Clarify GST treatment (18% on USD sales in India?)
- [ ] Update invoices with tax breakdown

### 4. Grandfather Clause Implementation

**Database:**
```sql
UPDATE users 
SET grandfathered_until = '2026-04-18' 
WHERE created_at < '2026-02-18';
```

**Enforcement:** Frontend + backend check `grandfathered_until` date

---

## Key Legal Protections

### Updated Terms Clauses

**6.1 Pricing Changes**
```
IgniteAI reserves the right to modify pricing with 14 days advance 
email notice. Existing credits remain valid indefinitely.
```

**7.1 No Refunds**
```
All purchases are final. Credits never expire. Technical issues may 
warrant replacement credits at our discretion.
```

**9.1 AI Content Disclaimer**
```
IgniteAI does not guarantee generated videos are unique or 
non-infringing. User responsible for reviewing before commercial use.
```

**11.1 Governing Law**
```
Disputes resolved via arbitration in Bangalore, India under 
Arbitration and Conciliation Act, 1996.
```

---

## Risk Assessment

| Risk | Level | Mitigation |
|------|-------|------------|
| Customer lawsuits | LOW | 14-day notice, clear TOS |
| Refund disputes | MEDIUM | Offer bonus credits |
| Tax non-compliance | MEDIUM | Consult accountant |
| Consumer protection | LOW | Comply with notice period |

---

## Approval Conditions

1. ✅ Update Terms of Service (4 new sections)
2. ✅ Email notification sent Feb 8 (10 days advance)
3. ✅ Tax consultation with accountant
4. ✅ FAQ page created at `/pricing-faq`
5. ✅ Grandfather clause implemented in code

**Signature:** Legal Counsel  
**Date:** January 23, 2026

---

**Full Legal Analysis:** See complete review for trademark, IP ownership, consumer protection details.

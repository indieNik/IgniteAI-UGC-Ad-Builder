# Cloud Run Public Access - Organization Policy Change Request

**Date:** January 18, 2026  
**Requester:** IgniteAI Development Team  
**Project:** sacred-temple-484011-h0  
**Service:** igniteai-backend (Cloud Run)

---

## Request Summary

We need to enable public access to our Cloud Run service `igniteai-backend` for our production web application hosted on Firebase Hosting.

---

## Current Issue

**Error Message:**
```
FAILED_PRECONDITION: One or more users named in the policy do not belong to a permitted customer
```

**Impact:**  
- Frontend (Firebase Hosting) cannot call backend API
- CORS errors blocking all functionality
- Application is non-functional in production

---

## Required Policy Change

### Organization Constraint to Modify

```
constraints/iam.allowedPolicyMemberDomains
```

### Current Restriction
The organization policy currently prevents external members (including `allUsers`) from being granted IAM roles.

### Requested Change

**Option 1: Allow Public Access (Recommended)**
Add `allUsers` to the allowed policy members for our specific project:

```bash
gcloud resource-manager org-policies allow \
  iam.allowedPolicyMemberDomains \
  allUsers \
  --project=sacred-temple-484011-h0
```

**Option 2: Allow Specific Domains**
If organization policy requires domain restriction, allow these specific origins:
- `ignite-ai-01.web.app` (Firebase Hosting)
- `ignite-ai-01.firebaseapp.com` (Firebase Hosting alternative)
- `igniteai.in` (custom domain - pending DNS setup)
- `app.igniteai.in` (custom subdomain - pending DNS setup)

---

## Security Considerations

**Why This Is Safe:**

1. **Application-Level Security**
   - Backend has Firebase Authentication (JWT tokens)
   - API endpoints validate user permissions
   - Rate limiting implemented (2-minute cooldown per user)
   - Admin endpoints require admin role verification

2. **CORS Protection**
   - Backend only accepts requests from whitelisted origins:
     ```python
     allow_origins=[
         "https://igniteai.in",
         "https://app.igniteai.in",
         "https://ignite-ai-01.web.app",
         "https://ignite-ai-01.firebaseapp.com",
         "http://localhost:4200"  # dev only
     ]
     ```

3. **Cloud Run Security**
   - HTTPS only
   - Auto-scaling with cost limits
   - Secret Manager for API keys
   - No sensitive data exposed publicly

4. **Industry Standard**
   - This is standard for serverless APIs
   - Google's recommended architecture for Firebase + Cloud Run
   - Similar to any public REST API (Stripe, Twilio, etc.)

---

## Alternative Solutions (If Policy Cannot Be Changed)

If organizational policy absolutely cannot allow public Cloud Run access, we have these alternatives:

### Alternative 1: API Gateway (Workaround)
- Deploy Google Cloud Endpoints as public proxy
- Cloud Run remains private
- Adds complexity & latency (~50-100ms)
- Additional cost (~$2-5/month)

### Alternative 2: Move to New Project
- Create new GCP project without restrictions
- Re-deploy entire stack
- Lose free credits (₹25,110 remaining)
- Requires DNS re-configuration

### Alternative 3: Revert to Hugging Face
- Move backend back to HF Spaces
- Slower performance (~10-30s cold starts vs <1s)
- Less reliable infrastructure
- Defeats purpose of GCP migration

---

## Impact of Delay

**Each day without fix:**
- Frontend completely non-functional
- Cannot onboard new users
- Lost revenue opportunity
- Development blocked

**Estimated time to implement fix:**
- Policy change: <5 minutes
- Validation: <2 minutes
- **Total: ~7 minutes**

---

## Implementation Steps (For Admin)

1. **Review Organization Policies:**
   ```bash
   gcloud resource-manager org-policies describe \
     iam.allowedPolicyMemberDomains \
     --organization=YOUR_ORG_ID
   ```

2. **Modify Policy for Our Project:**
   ```bash
   # See current policy
   gcloud resource-manager org-policies describe \
     iam.allowedPolicyMemberDomains \
     --project=sacred-temple-484011-h0
   
   # Allow all users for this project
   gcloud resource-manager org-policies allow \
     iam.allowedPolicyMemberDomains \
     allUsers \
     --project=sacred-temple-484011-h0
   ```

3. **Grant Cloud Run Invoker Role:**
   ```bash
   gcloud run services add-iam-policy-binding igniteai-backend \
     --region=us-central1 \
     --member="allUsers" \
     --role="roles/run.invoker" \
     --project=sacred-temple-484011-h0
   ```

4. **Verify Policy Change:**
   ```bash
   gcloud run services get-iam-policy igniteai-backend \
     --region=us-central1 \
     --project=sacred-temple-484011-h0
   ```

   Expected output should include:
   ```yaml
   bindings:
   - members:
     - allUsers
     role: roles/run.invoker
   ```

5. **Test Public Access:**
   ```bash
   curl https://igniteai-backend-254654034407.us-central1.run.app/health
   ```

   Expected response:
   ```json
   {"status":"ok","message":"AI Video Builder Backend is running"}
   ```

---

## Documentation & References

**Google Cloud Documentation:**
- [Cloud Run Authentication](https://cloud.google.com/run/docs/authenticating/public)
- [Organization Policy Constraints](https://cloud.google.com/resource-manager/docs/organization-policy/org-policy-constraints)
- [IAM Policy for Cloud Run](https://cloud.google.com/run/docs/securing/managing-access)

**Firebase + Cloud Run Architecture:**
- [Firebase Hosting with Cloud Run](https://firebase.google.com/docs/hosting/cloud-run)
- [Recommended pattern](https://cloud.google.com/blog/products/serverless/use-firebase-and-cloud-run-to-build-serverless-apps)

---

## Contact Information

**Technical Lead:** [Your Name]  
**Email:** hello@thejaggerypoint.com  
**Project:** IgniteAI (AI Video Generation Platform)  
**Cloud Run Service:** igniteai-backend  
**Region:** us-central1  
**Project ID:** sacred-temple-484011-h0

---

## Approval Status

- [ ] Request reviewed by organization admin
- [ ] Policy change approved
- [ ] Policy change implemented
- [ ] Public access verified
- [ ] Frontend functionality confirmed

---

**Urgency:** High - Application non-functional  
**Estimated Fix Time:** 7 minutes  
**Business Impact:** Production outage

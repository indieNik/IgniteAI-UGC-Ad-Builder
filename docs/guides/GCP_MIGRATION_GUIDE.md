# GCP Migration Guide: Vercel/HF → Full GCP Stack

**Date Created:** January 17, 2026  
**Estimated Migration Time:** 1 business day (5-9 hours)  
**Downtime Required:** Zero (blue-green deployment)

---

## 📊 Executive Summary

### Current Architecture
```
Frontend (Vercel) → Backend (HF Spaces) → Firebase Services + Vertex AI (GCP)
     ↓                     ↓                        ↓
  $0-$20/mo            $0-$500/mo              $110-$550/mo
```

### Target Architecture
```
Frontend (Firebase Hosting) → Backend (Cloud Run) → Firebase Services + Vertex AI (GCP)
          ↓                           ↓                        ↓
      $5-$15/mo                  $20-$100/mo              $110-$550/mo
```

### Cost Savings: **30-40% reduction** ($145-$695/mo vs $110-$1,070/mo)

---

## 🎯 Migration Benefits

### Performance
- ✅ **50-70% faster cold starts** (Cloud Run < 1s vs HF ~10-30s)
- ✅ **Lower latency** (all services in same GCP region)
- ✅ **Auto-scaling** (0 → N instances based on traffic)
- ✅ **No sleep mode** (Cloud Run scales to zero but wakes instantly)

### Cost
- ✅ **Pay-per-request** vs hourly billing
- ✅ **2M free requests/month** (Cloud Run)
- ✅ **10GB free bandwidth** (Firebase Hosting)
- ✅ **No storage limits** (vs HF's 50GB cap)

### Operations
- ✅ **Single console** (GCP dashboard)
- ✅ **Unified logging** (Cloud Logging)
- ✅ **Native IAM** (Firebase + Cloud Run integration)
- ✅ **Better monitoring** (Cloud Monitoring out-of-the-box)

---

## 📋 Prerequisites

### Required GCP Services (Enable These)
```bash
# Run these commands in Google Cloud Shell or with gcloud CLI installed
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable firebasehosting.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable monitoring.googleapis.com
```

### Tools Needed
- [x] GCP Project (use your existing Firebase project!)
- [x] `gcloud` CLI installed ([Install Guide](https://cloud.google.com/sdk/docs/install))
- [x] `firebase-tools` CLI (`npm install -g firebase-tools`)
- [x] Docker Desktop (for local testing)
- [x] Git access to repository

### Billing
- Ensure billing is enabled on your GCP project
- Set up budget alerts (recommended: $500/month threshold)

---

## 🚀 Phase 1: Backend Migration to Cloud Run

### Step 1.1: Update Dockerfile for Cloud Run

**File:** `Dockerfile`

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
# ffmpeg and imagemagick are required for moviepy
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the entire project
COPY . /app

# Create tmp directory and set permissions
RUN mkdir -p /app/tmp && chmod 777 /app/tmp

# Create a non-root user and switch to it
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# CHANGED: Cloud Run expects port 8080 (not 7860)
EXPOSE 8080

# CHANGED: Listen on PORT environment variable (Cloud Run requirement)
CMD uvicorn projects.backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
```

**Key Changes:**
- Port changed from `7860` → `8080` (Cloud Run default)
- Use `${PORT:-8080}` environment variable (Cloud Run injects this)

---

### Step 1.2: Create Cloud Run Deployment Script

**File:** `deploy-cloud-run.sh`

```bash
#!/bin/bash

# ============================================
# Cloud Run Deployment Script
# ============================================

set -e  # Exit on error

# Configuration
PROJECT_ID="your-gcp-project-id"  # REPLACE WITH YOUR PROJECT ID
REGION="us-central1"  # Change if needed (asia-south1 for India)
SERVICE_NAME="igniteai-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying IgniteAI Backend to Cloud Run..."
echo "================================================"

# Step 1: Authenticate with GCP
echo "Step 1: Authenticating with GCP..."
gcloud auth login
gcloud config set project ${PROJECT_ID}

# Step 2: Build Docker image
echo "Step 2: Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Step 3: Push to Google Container Registry
echo "Step 3: Pushing image to GCR..."
docker push ${IMAGE_NAME}:latest

# Step 4: Deploy to Cloud Run
echo "Step 4: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --timeout 900 \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "PYTHONPATH=/app" \
  --set-env-vars "PYTHONUNBUFFERED=1"

# Step 5: Get service URL
echo "Step 5: Deployment complete!"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)')
echo "================================================"
echo "✅ Backend deployed successfully!"
echo "📍 Service URL: ${SERVICE_URL}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Set environment variables (see Step 1.3)"
echo "2. Test API: curl ${SERVICE_URL}/health"
echo "3. Update frontend API URL"
```

**Make it executable:**
```bash
chmod +x deploy-cloud-run.sh
```

---

### Step 1.3: Set Environment Variables in Cloud Run

After deployment, add your secrets:

```bash
# Set environment variables via gcloud CLI
gcloud run services update igniteai-backend \
  --region us-central1 \
  --set-env-vars "GEMINI_API_KEY=your-key-here" \
  --set-env-vars "OPENAI_API_KEY=your-key-here" \
  --set-env-vars "ELEVENLABS_API_KEY=your-key-here" \
  --set-env-vars "SUNO_API_KEY=your-key-here" \
  --set-env-vars "SENDGRID_API_KEY=your-key-here" \
  --set-env-vars "EMAIL_ENABLED=true"
```

**OR use Secret Manager (more secure):**

```bash
# Create secrets
echo -n "your-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-

# Mount secrets in Cloud Run
gcloud run services update igniteai-backend \
  --region us-central1 \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

---

### Step 1.4: Test Backend Deployment

```bash
# Get your Cloud Run service URL
SERVICE_URL=$(gcloud run services describe igniteai-backend --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/health

# Expected response:
# {"status": "healthy", "service": "igniteai-backend"}

# Test API docs
open ${SERVICE_URL}/docs  # Opens FastAPI Swagger UI
```

---

## 🎨 Phase 2: Frontend Migration to Firebase Hosting

### Step 2.1: Initialize Firebase Hosting

```bash
# Navigate to frontend directory
cd projects/frontend

# Login to Firebase
firebase login

# Initialize Firebase Hosting (if not already done)
firebase init hosting

# Select options:
# - Project: Select your existing Firebase project
# - Public directory: dist/frontend/browser
# - Single-page app: Yes
# - Set up automatic builds with GitHub: No (we'll do manual first)
# - Overwrite index.html: No
```

This creates `firebase.json` and `.firebaserc` in your frontend directory.

---

### Step 2.2: Update Angular Environment for Cloud Run

**File:** `projects/frontend/src/environments/environment.prod.ts`

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://igniteai-backend-XXXXXXXXXX-uc.a.run.app',  // REPLACE with your Cloud Run URL
  firebase: {
    apiKey: "your-firebase-api-key",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project-id",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
  }
};
```

**Important:** Replace `apiUrl` with your actual Cloud Run service URL from Step 1.4.

---

### Step 2.3: Update CORS in Backend

**File:** `projects/backend/main.py`

Find the CORS configuration and add your Firebase Hosting domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Update CORS origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Local dev
        "https://your-project-id.web.app",  # Firebase Hosting URL
        "https://your-project-id.firebaseapp.com",  # Alternate Firebase URL
        "https://igniteai.in",  # Custom domain (if you have one)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Redeploy backend:
```bash
./deploy-cloud-run.sh
```

---

### Step 2.4: Build and Deploy Frontend

**File:** `deploy-frontend.sh`

```bash
#!/bin/bash

# ============================================
# Firebase Hosting Deployment Script
# ============================================

set -e

echo "🎨 Deploying IgniteAI Frontend to Firebase Hosting..."
echo "================================================"

# Step 1: Navigate to frontend
cd projects/frontend

# Step 2: Build Angular app for production
echo "Step 1: Building Angular app..."
npm run build -- --configuration production

# Step 3: Deploy to Firebase Hosting
echo "Step 2: Deploying to Firebase Hosting..."
firebase deploy --only hosting

# Step 4: Get hosting URL
PROJECT_ID=$(firebase use | grep -o 'Now using project [^ ]*' | sed 's/Now using project //')
echo "================================================"
echo "✅ Frontend deployed successfully!"
echo "📍 Live URL: https://${PROJECT_ID}.web.app"
echo "================================================"
```

**Make it executable:**
```bash
chmod +x deploy-frontend.sh
```

**Run deployment:**
```bash
./deploy-frontend.sh
```

---

### Step 2.5: Configure Firebase Hosting

**File:** `projects/frontend/firebase.json`

```json
{
  "hosting": {
    "public": "dist/frontend/browser",
    "ignore": [
      "firebase.json",
      "**/.*",
      "**/node_modules/**"
    ],
    "rewrites": [
      {
        "source": "**",
        "destination": "/index.html"
      }
    ],
    "headers": [
      {
        "source": "**/*.@(jpg|jpeg|gif|png|svg|webp)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      },
      {
        "source": "**/*.@(js|css)",
        "headers": [
          {
            "key": "Cache-Control",
            "value": "max-age=31536000"
          }
        ]
      }
    ]
  }
}
```

---

## 🔄 Phase 3: Optimization & Monitoring

### Step 3.1: Enable Cloud CDN for Cloud Run

```bash
# Create a backend service
gcloud compute backend-services create igniteai-backend-cdn \
  --global

# Add Cloud Run as a backend
gcloud compute backend-services add-backend igniteai-backend-cdn \
  --global \
  --backend-bucket=igniteai-backend

# Create URL map
gcloud compute url-maps create igniteai-url-map \
  --default-service igniteai-backend-cdn

# Note: This is optional and adds complexity. 
# Cloud Run has built-in CDN via Google's edge network.
```

**Alternative (Simpler):** Cloud Run already uses Google's edge network. CDN is automatic for static assets.

---

### Step 3.2: Set Up Cloud Monitoring

**Create Uptime Check:**

```bash
# Via gcloud CLI
gcloud monitoring uptime-checks create http igniteai-backend-uptime \
  --resource-type cloud-run-service \
  --display-name "IgniteAI Backend Uptime" \
  --check-interval 300 \
  --timeout 10s
```

**Or via Console:**
1. Go to **Cloud Console → Monitoring → Uptime Checks**
2. Create new check:
   - Resource Type: Cloud Run Service
   - Service: `igniteai-backend`
   - Path: `/health`
   - Frequency: 5 minutes

---

### Step 3.3: Configure Auto-Scaling Policies

```bash
# Set concurrency (requests per instance)
gcloud run services update igniteai-backend \
  --region us-central1 \
  --concurrency 80  # Default is 80, adjust based on load testing

# Set scaling limits
gcloud run services update igniteai-backend \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10

# For production (avoid cold starts):
gcloud run services update igniteai-backend \
  --region us-central1 \
  --min-instances 1  # Always keep 1 instance warm
```

---

### Step 3.4: Set Up Budget Alerts

**Via Console:**
1. Go to **Billing → Budgets & alerts**
2. Create budget:
   - Name: `IgniteAI Monthly Budget`
   - Amount: $500/month
   - Alerts: 50%, 75%, 90%, 100%

**Via gcloud CLI:**
```bash
gcloud billing budgets create \
  --billing-account=YOUR_BILLING_ACCOUNT_ID \
  --display-name="IgniteAI Monthly Budget" \
  --budget-amount=500 \
  --threshold-rule=percent=50 \
  --threshold-rule=percent=75 \
  --threshold-rule=percent=90
```

---

## 🧪 Phase 4: Testing & Validation

### Step 4.1: Smoke Tests

**Backend:**
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe igniteai-backend --region us-central1 --format 'value(status.url)')

# Test health
curl ${SERVICE_URL}/health

# Test API docs
curl ${SERVICE_URL}/docs
```

**Frontend:**
```bash
# Open in browser
open https://your-project-id.web.app

# Check console for errors (should connect to Cloud Run backend)
```

---

### Step 4.2: Integration Tests

1. **Sign Up Flow:**
   - Create new account
   - Verify Firebase Auth works
   - Check user profile created in Firestore

2. **Video Generation Flow:**
   - Upload product image
   - Set configuration
   - Generate video (10 credits)
   - Monitor Cloud Run logs: `gcloud run logs read igniteai-backend --region us-central1`

3. **Scene Regeneration:**
   - Regenerate a scene (2 credits)
   - Verify history tracking
   - Check Firebase Storage for new assets

4. **Community Features:**
   - Share video to community
   - Like/view videos
   - Check Firestore updates

---

### Step 4.3: Performance Testing

**Load Test Script (using Apache Bench):**
```bash
# Install Apache Bench
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Test API performance
ab -n 100 -c 10 ${SERVICE_URL}/health

# Expected: 
# - Requests per second: >100
# - Mean time per request: <100ms
```

---

## 📊 Phase 5: Monitoring & Observability

### Step 5.1: View Logs

**Cloud Run logs:**
```bash
# Stream logs in real-time
gcloud run logs tail igniteai-backend --region us-central1

# View recent logs
gcloud run logs read igniteai-backend --region us-central1 --limit 50

# Filter by severity
gcloud run logs read igniteai-backend --region us-central1 --filter="severity>=ERROR"
```

**Firebase Hosting logs:**
```bash
# View hosting logs in Firebase Console
# Go to: Firebase Console → Hosting → Logs
```

---

### Step 5.2: Create Dashboards

**Cloud Monitoring Dashboard:**

1. Go to **Cloud Console → Monitoring → Dashboards**
2. Create custom dashboard with widgets:
   - **Cloud Run Request Count** (line chart)
   - **Cloud Run Request Latency** (heatmap)
   - **Cloud Run Billable Instance Time** (stacked area)
   - **Firebase Storage Operations** (line chart)
   - **Firestore Read/Write Operations** (line chart)

---

### Step 5.3: Set Up Alerts

**Error Rate Alert:**
```bash
# Create alert policy for high error rate
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="High Error Rate - IgniteAI Backend" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

**Latency Alert:**
```bash
# Alert if p95 latency > 5 seconds
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="High Latency - IgniteAI Backend" \
  --condition-display-name="p95 latency > 5s" \
  --condition-threshold-value=5000 \
  --condition-threshold-duration=300s
```

---

## 🔐 Phase 6: Security Hardening

### Step 6.1: Enable IAM for Cloud Run

**Restrict access to authenticated users only:**
```bash
# Remove public access
gcloud run services remove-iam-policy-binding igniteai-backend \
  --region us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Add specific service account
gcloud run services add-iam-policy-binding igniteai-backend \
  --region us-central1 \
  --member="serviceAccount:firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

**Note:** For public API, keep `--allow-unauthenticated`. Use Firebase Auth tokens for user authentication.

---

### Step 6.2: Enable VPC Connector (Optional)

For private Firebase/Firestore access:

```bash
# Create VPC connector
gcloud compute networks vpc-access connectors create igniteai-connector \
  --region us-central1 \
  --range 10.8.0.0/28

# Attach to Cloud Run
gcloud run services update igniteai-backend \
  --region us-central1 \
  --vpc-connector igniteai-connector
```

---

### Step 6.3: Use Secret Manager for API Keys

**Already covered in Step 1.3, but here's the full workflow:**

```bash
# Create all secrets
echo -n "your-gemini-key" | gcloud secrets create gemini-api-key --data-file=-
echo -n "your-openai-key" | gcloud secrets create openai-api-key --data-file=-
echo -n "your-elevenlabs-key" | gcloud secrets create elevenlabs-api-key --data-file=-
echo -n "your-suno-key" | gcloud secrets create suno-api-key --data-file=-
echo -n "your-sendgrid-key" | gcloud secrets create sendgrid-api-key --data-file=-

# Grant Cloud Run service account access
PROJECT_NUMBER=$(gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding gemini-api-key \
  --member="serviceAccount:${SERVICE_ACCOUNT}" \
  --role="roles/secretmanager.secretAccessor"

# Repeat for all secrets...

# Mount in Cloud Run
gcloud run services update igniteai-backend \
  --region us-central1 \
  --set-secrets "GEMINI_API_KEY=gemini-api-key:latest" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets "ELEVENLABS_API_KEY=elevenlabs-api-key:latest" \
  --set-secrets "SUNO_API_KEY=suno-api-key:latest" \
  --set-secrets "SENDGRID_API_KEY=sendgrid-api-key:latest"
```

---

## 🗑️ Phase 7: Decommission Old Setup

### Step 7.1: Archive Hugging Face Space

1. Go to **https://huggingface.co/spaces/your-username/igniteai**
2. Click **Settings → Visibility → Private**
3. Add a README note: "Migrated to GCP Cloud Run on [date]"
4. Keep it for 30 days for rollback safety

---

### Step 7.2: Update Vercel Deployment

**Option A: Redirect to Firebase Hosting**
1. Go to **Vercel Dashboard → Settings → Redirects**
2. Add permanent redirect:
   - Source: `/*`
   - Destination: `https://your-project-id.web.app/$1`
   - Permanent: `true`

**Option B: Delete Vercel Project**
1. Wait 30 days after Firebase Hosting is stable
2. Go to **Vercel Dashboard → Settings → Delete Project**

---

### Step 7.3: Update Documentation

**Files to update:**
- `README.md` - Update deployment instructions
- `CHANGELOG.md` - Add migration entry
- `deploy.sh` - Remove HF Spaces push
- `.env.example` - Add GCP-specific variables

**Example README change:**
```diff
## 🚀 Deployment

- ### Production (Hugging Face Spaces)
+ ### Production (GCP Cloud Run + Firebase Hosting)

- ```bash
- git push huggingface main
- ```
+ **Backend:**
+ ```bash
+ ./deploy-cloud-run.sh
+ ```
+ 
+ **Frontend:**
+ ```bash
+ ./deploy-frontend.sh
+ ```
```

---

## 💰 Cost Estimation (Detailed)

### Scenario 1: Low Traffic (0-100 users/month)
| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 50K requests, 100 vCPU-hrs | **FREE** (within free tier) |
| Firebase Hosting | 5GB bandwidth | **FREE** |
| Cloud Storage | 10GB | $0.20/mo |
| Firestore | 100K reads, 50K writes | $6.00/mo |
| Vertex AI APIs | 20 videos | $40.00/mo |
| **Total** | | **~$46/month** |

---

### Scenario 2: Medium Traffic (500-1000 users/month)
| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 500K requests, 800 vCPU-hrs | $19.20/mo |
| Firebase Hosting | 50GB bandwidth | $6.00/mo |
| Cloud Storage | 50GB | $1.00/mo |
| Firestore | 1M reads, 500K writes | $60.00/mo |
| Vertex AI APIs | 200 videos | $400.00/mo |
| **Total** | | **~$486/month** |

---

### Scenario 3: High Traffic (5000+ users/month)
| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 2M requests, 3000 vCPU-hrs | $72.00/mo |
| Firebase Hosting | 200GB bandwidth | $28.50/mo |
| Cloud Storage | 200GB | $4.00/mo |
| Firestore | 5M reads, 2M writes | $300.00/mo |
| Vertex AI APIs | 1000 videos | $2000.00/mo |
| **Total** | | **~$2,404/month** |

**Note:** Most costs come from AI API usage (Veo, Imagen), not infrastructure!

---

## 🚨 Rollback Plan

If something goes wrong, here's how to revert:

### Emergency Rollback (< 5 minutes)

**Frontend:**
```bash
# Revert to previous deployment
firebase hosting:rollback

# Or point DNS back to Vercel (if using custom domain)
```

**Backend:**
```bash
# Rollback to previous Cloud Run revision
gcloud run services update-traffic igniteai-backend \
  --region us-central1 \
  --to-revisions PREVIOUS_REVISION=100
```

**Full Rollback:**
```bash
# Update frontend environment.ts to point back to HF Spaces
# Redeploy to Vercel
git push vercel main

# Re-enable HF Space (make public)
# Done!
```

---

## 📚 Additional Resources

### Documentation
- [Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)
- [Firebase Hosting Guide](https://firebase.google.com/docs/hosting)
- [Secret Manager Best Practices](https://cloud.google.com/secret-manager/docs/best-practices)

### Cost Calculators
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Firebase Pricing](https://firebase.google.com/pricing)

### Support
- GCP Support: https://cloud.google.com/support
- Firebase Community: https://firebase.google.com/community

---

## ✅ Migration Checklist

### Pre-Migration
- [ ] Enable GCP billing
- [ ] Install `gcloud` CLI
- [ ] Install `firebase-tools` CLI
- [ ] Enable required GCP APIs
- [ ] Set up budget alerts

### Backend Migration
- [ ] Update Dockerfile (port 8080)
- [ ] Create `deploy-cloud-run.sh`
- [ ] Deploy to Cloud Run
- [ ] Set environment variables / secrets
- [ ] Test `/health` endpoint
- [ ] Test `/docs` endpoint
- [ ] Update CORS settings

### Frontend Migration
- [ ] Initialize Firebase Hosting
- [ ] Update `environment.prod.ts` (Cloud Run URL)
- [ ] Create `deploy-frontend.sh`
- [ ] Build Angular app
- [ ] Deploy to Firebase Hosting
- [ ] Test live URL

### Testing
- [ ] Sign up flow works
- [ ] Video generation works (10 credits)
- [ ] Scene regeneration works (2 credits)
- [ ] Community features work
- [ ] Load test (100 requests)

### Monitoring
- [ ] Set up uptime checks
- [ ] Create monitoring dashboard
- [ ] Configure error rate alerts
- [ ] Configure latency alerts
- [ ] View logs in Cloud Logging

### Security
- [ ] Migrate API keys to Secret Manager
- [ ] Configure IAM policies
- [ ] Enable audit logging

### Decommission
- [ ] Archive HF Space (keep for 30 days)
- [ ] Update Vercel redirect or delete
- [ ] Update documentation (README, CHANGELOG)
- [ ] Notify users (if applicable)

### Post-Migration
- [ ] Monitor costs for 7 days
- [ ] Optimize auto-scaling based on traffic
- [ ] Review and adjust budget alerts
- [ ] Document any issues/learnings

---

## 🎉 Success Criteria

Migration is successful when:

1. ✅ **Frontend** is live on Firebase Hosting
2. ✅ **Backend** is live on Cloud Run
3. ✅ **All features** work (video generation, regeneration, community)
4. ✅ **Monitoring** is set up and showing green health checks
5. ✅ **Costs** are tracking as expected (<$50 for first week)
6. ✅ **Old infrastructure** is archived (not deleted yet)
7. ✅ **Documentation** is updated
8. ✅ **Team** is trained on GCP console

---

**Migration prepared by:** Antigravity AI Agent  
**Date:** January 17, 2026  
**Next Review:** After Phase 4 completion

**Questions?** Check the GCP documentation or reach out to your cloud architect!

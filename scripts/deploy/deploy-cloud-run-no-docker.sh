#!/bin/bash

# ============================================
# Cloud Run Deployment WITHOUT Docker
# Uses Cloud Build to build image remotely
# ============================================

set -e  # Exit on error

# Check gcloud authentication
echo "🔐 Verifying gcloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  You are not logged in to gcloud."
    echo "🔐 Initiating login..."
    gcloud auth login
    if [ $? -ne 0 ]; then
        echo "❌ Login failed. Aborting deployment."
        exit 1
    fi
fi
echo "✅ Authenticated with gcloud"
echo ""

# Configuration
PROJECT_ID="sacred-temple-484011-h0"
REGION="us-central1"
SERVICE_NAME="igniteai-backend"

echo "🚀 Deploying IgniteAI Backend to Cloud Run (Cloud Build)"
echo "================================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "================================================"
echo ""
echo "✨ No Docker required - building in the cloud!"
echo ""

# Step 1: Deploy using gcloud (builds remotely)
echo "Step 1: Building and deploying to Cloud Run..."
echo "This will build the image in Google Cloud Build"
echo "Estimated time: 3-5 minutes"
echo ""

gcloud run deploy ${SERVICE_NAME} \
  --source . \
  --platform managed \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --timeout 900 \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "PYTHONPATH=/app" \
  --set-env-vars "PYTHONUNBUFFERED=1"

# Step 2: Get service URL
echo ""
echo "================================================"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --format 'value(status.url)')
echo "✅ Backend deployed successfully!"
echo "📍 Service URL: ${SERVICE_URL}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Environment variables already set from previous deployment"
echo "2. Test API: curl ${SERVICE_URL}/health"
echo ""

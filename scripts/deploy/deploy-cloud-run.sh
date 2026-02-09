#!/bin/bash

# ============================================
# Cloud Run Deployment Script
# ============================================

set -e  # Exit on error

# Configuration - UPDATE THIS
PROJECT_ID="sacred-temple-484011-h0"  # Your GCP project
REGION="us-central1"  # US Central
SERVICE_NAME="igniteai-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🚀 Deploying IgniteAI Backend to Cloud Run..."
echo "================================================"
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "================================================"
echo ""

# Step 0: Check gcloud authentication
echo "Step 0: Verifying gcloud authentication..."
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

# Step 1: Enable APIs if not done already
echo "Step 1: Ensuring required APIs are enabled..."
gcloud services enable run.googleapis.com \
    cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    artifactregistry.googleapis.com \
    --project=${PROJECT_ID}

echo "✅ APIs enabled"
echo ""

# Step 2: Build Docker image
echo "Step 2: Building Docker image..."
echo "This may take 5-10 minutes..."
docker build -t ${IMAGE_NAME}:latest .

echo "✅ Image built successfully"
echo ""

# Step 3: Configure Docker to use gcloud as a credential helper
echo "Step 3: Configuring Docker authentication..."
gcloud auth configure-docker --quiet

# Step 4: Push to Google Container Registry
echo "Step 4: Pushing image to GCR..."
echo "This may take a few minutes..."
docker push ${IMAGE_NAME}:latest

echo "✅ Image pushed successfully"
echo ""

# Step 5: Deploy to Cloud Run
echo "Step 5: Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --allow-unauthenticated \
  --timeout 900 \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars "PYTHONPATH=/app" \
  --set-env-vars "PYTHONUNBUFFERED=1"

# Step 6: Get service URL
echo ""
echo "Step 6: Deployment complete!"
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region ${REGION} --project ${PROJECT_ID} --format 'value(status.url)')
echo "================================================"
echo "✅ Backend deployed successfully!"
echo "📍 Service URL: ${SERVICE_URL}"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Set environment variables (API keys) - see next script"
echo "2. Test API: curl ${SERVICE_URL}/health"
echo "3. Update frontend API URL"
echo ""
echo "To set environment variables with your API keys, run:"
echo "./set-cloud-run-env.sh"

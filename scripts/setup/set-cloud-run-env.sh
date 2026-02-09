#!/bin/bash

# ============================================
# Set Cloud Run Environment Variables Script
# ============================================

set -e

# Check gcloud authentication
echo "🔐 Verifying gcloud authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  You are not logged in to gcloud."
    echo "🔐 Initiating login..."
    gcloud auth login
    if [ $? -ne 0 ]; then
        echo "❌ Login failed. Aborting setup."
        exit 1
    fi
fi
echo "✅ Authenticated with gcloud"
echo ""

PROJECT_ID="sacred-temple-484011-h0"
REGION="us-central1"
SERVICE_NAME="igniteai-backend"

echo "🔐 Configuring Environment Variables for Cloud Run..."
echo "================================================"
echo ""

# Read API keys from .env file (only for secrets, not env vars)
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    exit 1
fi

# Check for cloud-run-env.yaml
if [ ! -f ".config/cloud-run-env.yaml" ]; then
    echo "❌ .config/cloud-run-env.yaml not found!"
    echo "This file should contain all environment variables for Cloud Run."
    exit 1
fi

# Read ONLY secret values from .env (these go to Secret Manager)
export GEMINI_API_KEY=$(grep "^GEMINI_API_KEY=" .env | cut -d '=' -f2)
export OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" .env | cut -d '=' -f2)
export ELEVENLABS_API_KEY=$(grep "^ELEVENLABS_API_KEY=" .env | cut -d '=' -f2)
export SENDGRID_API_KEY=$(grep "^SENDGRID_API_KEY=" .env | cut -d '=' -f2)

echo "Step 1: Creating secrets in Secret Manager..."

# Create secrets (suppress errors if they already exist)
echo -n "${GEMINI_API_KEY}" | gcloud secrets create gemini-api-key --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo -n "${GEMINI_API_KEY}" | gcloud secrets versions add gemini-api-key --data-file=- --project=${PROJECT_ID}

echo -n "${OPENAI_API_KEY}" | gcloud secrets create openai-api-key --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo -n "${OPENAI_API_KEY}" | gcloud secrets versions add openai-api-key --data-file=- --project=${PROJECT_ID}

echo -n "${ELEVENLABS_API_KEY}" | gcloud secrets create elevenlabs-api-key --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo -n "${ELEVENLABS_API_KEY}" | gcloud secrets versions add elevenlabs-api-key --data-file=- --project=${PROJECT_ID}

echo -n "${SENDGRID_API_KEY}" | gcloud secrets create sendgrid-api-key --data-file=- --project=${PROJECT_ID} 2>/dev/null || \
    echo -n "${SENDGRID_API_KEY}" | gcloud secrets versions add sendgrid-api-key --data-file=- --project=${PROJECT_ID}

echo "✅ Secrets created/updated in Secret Manager"
echo ""

# Upload Service Account JSON to Secret Manager
if [ -f "projects/backend/service-account.json" ]; then
    echo "Step 1.1: Uploading service account JSON to Secret Manager..."
    gcloud secrets create firebase-service-account-json --data-file="projects/backend/service-account.json" --project=${PROJECT_ID} 2>/dev/null || \
    gcloud secrets versions add firebase-service-account-json --data-file="projects/backend/service-account.json" --project=${PROJECT_ID}
else
    echo "⚠️ Warning: projects/backend/service-account.json not found. Skipping secret upload."
fi

echo "Step 2: Deploying environment variables from .config/cloud-run-env.yaml..."
echo "This file contains all non-secret environment variables (API keys, plan IDs, config)."
echo ""

# Deploy using YAML file - automatically includes ALL variables
gcloud run services update ${SERVICE_NAME} \
  --region ${REGION} \
  --project ${PROJECT_ID} \
  --set-secrets="GEMINI_API_KEY=gemini-api-key:latest,OPENAI_API_KEY=openai-api-key:latest,ELEVENLABS_API_KEY=elevenlabs-api-key:latest,SENDGRID_API_KEY=sendgrid-api-key:latest,FIREBASE_SERVICE_ACCOUNT_JSON=firebase-service-account-json:latest" \
  --env-vars-file=.config/cloud-run-env.yaml

echo ""
echo "================================================"
echo "✅ Environment variables configured successfully!"
echo "================================================"
echo ""
echo "📝 Deployed variables from .config/cloud-run-env.yaml:"
cat .config/cloud-run-env.yaml | grep -v "^#" | grep -v "^$"
echo ""
echo "Next steps:"
echo "1. Wait 30-60 seconds for Cloud Run to restart"
echo "2. Test API endpoints"
echo "3. Deploy frontend to Firebase Hosting"

# Backend Deployment Guide (GCP Cloud Run)

> [!NOTE]
> **This project uses Google Cloud Platform (GCP), not AWS.**
> The backend is deployed on **Cloud Run** (Serverless Containers) for optimal scaling and cost efficiency.

## 📋 Prerequisites

Before deploying, ensure you have the following:

1.  **GCP Project**: You need a Google Cloud Project ID (e.g., `sacred-temple-484011-h0`).
2.  **Google Cloud CLI**: Install `gcloud` SDK.
    ```bash
    brew install --cask google-cloud-sdk
    ```
3.  **Docker**: Required for building the container image locally.

## 🚀 Deployment Steps

### 1. Authenticate
Login to your Google Cloud account:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### 2. Deploy Backend
We use a scripted deployment process. Run the following command from the project root:

```bash
./scripts/deploy/deploy-cloud-run.sh
```

**What this script does:**
1.  Enables required APIs (`run.googleapis.com`, `cloudbuild.googleapis.com`, etc.).
2.  Builds the Docker image from `Dockerfile`.
3.  Pushes the image to Google Container Registry (GCR).
4.  Deploys the service to Cloud Run (Region: `us-central1`).

### 3. Configure Environment & Secrets
After deployment, you must configure environment variables and sensitive keys (API Keys).

**Option A: Automated Setup (Recommended)**
Run the configuration script:
```bash
./scripts/setup/set-cloud-run-env.sh
```
*This script will interactively ask for your API keys (OpenAI, Gemini, ElevenLabs) and securely store them in **GCP Secret Manager**, then mount them to your Cloud Run service.*

**Option B: Manual Setup**
You can also set variables via the command line:
```bash
gcloud run services update igniteai-backend \
  --set-env-vars "EMAIL_ENABLED=true" \
  --set-secrets "OPENAI_API_KEY=openai-api-key:latest"
```

## 🔐 Access & Security

### Service Accounts
The backend uses a specific **Service Account** to access other GCP resources (like Vertex AI and Firestore).
*   **Default:** `PROJECT_NUMBER-compute@developer.gserviceaccount.com`
*   **Permissions Required:**
    *   `roles/secretmanager.secretAccessor` (To read API keys)
    *   `roles/aiplatform.user` (For Vertex AI)
    *   `roles/datastore.user` (For Firestore)

### IAM (Identity and Access Management)
By default, the deployment script allows **unauthenticated access** (`--allow-unauthenticated`) to the public API endpoints.
*   **Public Access:** Required for the frontend to call the API.
*   **Authentication:** The backend validates Firebase Auth tokens in the `Authorization` header for protected endpoints.

## 🔍 Verification

Check the service health after deployment:
```bash
SERVICE_URL=$(gcloud run services describe igniteai-backend --format 'value(status.url)')
curl "${SERVICE_URL}/health"
```
Output should be: `{"status": "healthy", "service": "igniteai-backend"}`

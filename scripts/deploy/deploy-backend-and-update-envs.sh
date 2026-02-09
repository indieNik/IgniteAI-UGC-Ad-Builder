#!/bin/bash

# Deploy backend and update environment variables
# This combines both deployment steps for convenience

echo "🚀 Deploying backend without Docker..."
./scripts/deploy/deploy-cloud-run-no-docker.sh

echo ""
echo "⚙️  Updating Cloud Run environment variables..."
./scripts/setup/set-cloud-run-env.sh

echo ""
echo "✅ Backend deployed and environment variables updated!"
#!/bin/bash
set -e

echo "🚀 Deploying App to Firebase..."
echo ""

# Step 1: Sync content
echo "📋 Step 1/3: Syncing product content..."
npm run sync-content
echo ""

# Step 2: Build Angular app
echo "🏗️  Step 2/3: Building Angular app..."
cd projects/frontend
npm run build
cd ../..
echo "✅ Build complete!"
echo ""

# Step 3: Deploy to Firebase
echo "☁️  Step 3/3: Deploying to Firebase (app target)..."
firebase deploy --only hosting:app

echo ""
echo "✨ App deployed successfully!"
echo "🌐 URL: https://app.igniteai.com (after DNS setup)"

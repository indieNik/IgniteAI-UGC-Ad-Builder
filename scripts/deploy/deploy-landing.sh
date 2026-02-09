#!/bin/bash
set -e

echo "🚀 Deploying Landing Site to Firebase..."
echo ""

# Step 1: Sync content
echo "📋 Step 1/3: Syncing product content..."
npm run sync-content
echo ""

# Step 2: Build landing site
echo "🏗️  Step 2/3: Building Next.js landing site..."
cd projects/landing
npm run build
cd ../..
echo "✅ Build complete!"
echo ""

# Step 3: Deploy to Firebase
echo "☁️  Step 3/3: Deploying to Firebase (landing target)..."
firebase deploy --only hosting:landing

echo ""
echo "✨ Landing site deployed successfully!"
echo "🌐 URL: https://igniteai.com (after DNS setup)"

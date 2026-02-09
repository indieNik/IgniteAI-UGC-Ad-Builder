#!/bin/bash
set -e

echo "🚀 Deploying BOTH Landing & App to Firebase..."
echo ""

# Sync content first
echo "📋 Syncing product content..."
npm run sync-content
echo ""

# Build both projects
echo "🏗️  Building landing site..."
cd projects/landing
npm run build
cd ../..
echo "✅ Landing build complete!"
echo ""

echo "🏗️  Building Angular app..."
cd projects/frontend
npm run build
cd ../..
echo "✅ App build complete!"
echo ""

# Deploy both to Firebase
echo "☁️  Deploying to Firebase (both targets)..."
firebase deploy --only hosting

echo ""
echo "✨ Complete deployment successful!"
echo "🌐 Landing: https://igniteai.com (after DNS setup)"
echo "🌐 App: https://app.igniteai.com (after DNS setup)"

#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Check Branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo -e "${RED}❌ Error: You are on branch '$CURRENT_BRANCH'. Please switch to 'main' before deploying.${NC}"
    exit 1
fi

# Auto-bump version before deployment
echo -e "${BLUE}🔢 Bumping version...${NC}"
./bump-version.sh

# Commit version bump
git commit -m "chore: bump version [skip ci]" --no-verify 2>/dev/null || echo -e "${YELLOW}⚠️  No version changes to commit${NC}"

echo -e "${BLUE}🚀 Starting Parallel Deployment...${NC}"

# 1. Push to GitHub (Origin) - Background
echo -e "${BLUE}📦 Pushing to GitHub (Origin)...${NC}"
git push origin main &
PID_GITHUB=$!

# 2. Push to Hugging Face (Backend) - Background
echo -e "${BLUE}🤗 Deploying to Hugging Face (Backend)...${NC}"
git push huggingface main &
PID_HF=$!

# 3. Deploy Frontend to Vercel - Background
echo -e "${BLUE}△ Deploying to Vercel (Frontend)...${NC}"

# Load NVM if available (for Node.js/npx)
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    export NVM_DIR="$HOME/.nvm"
    source "$NVM_DIR/nvm.sh"
fi

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: npx not found. Skipping Vercel deployment.${NC}"
    echo -e "${YELLOW}   Install Node.js or run: brew install node${NC}"
    VERCEL_STATUS=2  # Mark as skipped
    PID_VERCEL=""
else
    (cd projects/frontend && npx vercel --prod) &
    PID_VERCEL=$!
fi

# 4. Wait for all
wait $PID_GITHUB
GITHUB_STATUS=$?

wait $PID_HF
HF_STATUS=$?

if [ -n "$PID_VERCEL" ]; then
    wait $PID_VERCEL
    VERCEL_STATUS=$?
fi

echo ""
if [ $GITHUB_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ GitHub Sync Successful!${NC}"
else
    echo -e "${RED}❌ GitHub Sync Failed.${NC}"
fi

if [ $HF_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ Hugging Face Deployment Triggered!${NC}"
else
    echo -e "${RED}❌ Hugging Face Deployment Failed.${NC}"
fi

if [ -z "$PID_VERCEL" ]; then
    echo -e "${YELLOW}⏭️  Vercel Deployment Skipped (npx not available).${NC}"
elif [ $VERCEL_STATUS -eq 0 ]; then
    echo -e "${GREEN}✅ Vercel Deployment Successful!${NC}"
else
    echo -e "${RED}❌ Vercel Deployment Failed.${NC}"
fi

# Exit with error if any critical deployment failed
if [ $GITHUB_STATUS -ne 0 ] || [ $HF_STATUS -ne 0 ]; then
    echo -e "\n${RED}⚠️  Some deployments failed. Please check errors above.${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 Deployment Complete!${NC}"

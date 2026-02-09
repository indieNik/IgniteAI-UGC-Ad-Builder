#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}1. Checking/Installing Google Cloud SDK...${NC}"
if ! command -v gcloud &> /dev/null; then
    echo "gcloud not found. Installing..."
    # Download and install with prompts disabled
    curl https://sdk.cloud.google.com | bash -s -- --disable-prompts
    
    # Source path.bash.inc if it exists to make gcloud available in this script
    if [ -f "$HOME/google-cloud-sdk/path.bash.inc" ]; then
        source "$HOME/google-cloud-sdk/path.bash.inc"
    fi
else
    echo "gcloud is already installed."
fi

echo -e "${GREEN}2. Checking/Installing Firebase CLI...${NC}"
if ! command -v firebase &> /dev/null; then
    echo "firebase not found. Installing..."
    curl -sL https://firebase.tools | bash
else
    echo "firebase is already installed."
fi

echo -e "${GREEN}Installation checks complete.${NC}"
echo "Please restart your terminal or run 'source ~/.zshrc' to ensure tools are in your PATH."

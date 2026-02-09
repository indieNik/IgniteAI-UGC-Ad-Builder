#!/bin/bash

# Version bump script - automatically increments patch version
# Usage: ./bump-version.sh

VERSION_FILE="projects/frontend/src/app/version.ts"

# Extract current version
CURRENT_VERSION=$(grep "APP_VERSION" "$VERSION_FILE" | sed "s/.*'\(.*\)'.*/\1/")

# Split version into major.minor.patch
IFS='.' read -r -a VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR="${VERSION_PARTS[0]}"
MINOR="${VERSION_PARTS[1]}"
PATCH="${VERSION_PARTS[2]}"

# Increment patch version
NEW_PATCH=$((PATCH + 1))
NEW_VERSION="$MAJOR.$MINOR.$NEW_PATCH"

# Get current date
BUILD_DATE=$(date +%Y-%m-%d)

# Update version.ts file
cat > "$VERSION_FILE" << EOF
export const APP_VERSION = '$NEW_VERSION';
export const BUILD_DATE = '$BUILD_DATE';
EOF

echo "✅ Version bumped: $CURRENT_VERSION → $NEW_VERSION"
echo "📅 Build date: $BUILD_DATE"

# Stage the version file
git add "$VERSION_FILE"

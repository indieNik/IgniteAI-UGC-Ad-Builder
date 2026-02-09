#!/bin/bash

# Pilot Test: 1-Scene Video with Skills Integration
# Tests Voice Generator (eleven_v3 + tags) and Caption Generator (chunked)

echo "======================================================================"
echo "🧪 PILOT TEST: 1-Scene Video with Skills Integration"
echo "======================================================================"
echo ""
echo "📋 Test Configuration:"
echo "   • Scenes: 1 (via NUM_SCENES=1)"
echo "   • Voice: ElevenLabs v3 with expressive tags"
echo "   • Captions: Chunked 2-word style"
echo "   • Provider: Gemini + Veo"
echo ""
echo "======================================================================"
echo ""

# Set environment variables
export NUM_SCENES=1
export LLM_PROVIDER="gemini"
export IMAGE_PROVIDER="veo"
export PRODUCT_DESCRIPTION="The Jaggery Point cafe - cozy Bangalore coffee shop"
export PRODUCT_IMAGE_PATH="brand/designs/image.png"

echo "🚀 Starting workflow..."
echo ""

# Run workflow module
python3 -m execution.workflow 2>&1 | tee pilot_test.log

echo ""
echo "======================================================================"
echo "✅ PILOT TEST COMPLETED - Check pilot_test.log for full output"
echo "======================================================================"

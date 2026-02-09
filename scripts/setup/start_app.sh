#!/bin/bash

# Function to kill child processes on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

echo "🚀 Igniting AI Video Builder (Integrated Mode)..."
PROJECT_ROOT=$(pwd)

# 0. Cleanup existing processes
echo "🧹 Cleaning up existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:4200 | xargs kill -9 2>/dev/null

# 1. Start Backend in Background
echo "🔌 Starting Backend Server (Port 8000)..."
cd "$PROJECT_ROOT/projects/backend"

# Check if venv exists, otherwise use system python
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# CRITICAL: Set PYTHONPATH to project root so 'projects.backend' imports work
export PYTHONPATH=$PROJECT_ROOT

# Run uvicorn using python3 (Assuming local environment has dependencies installed)
# We use python3 directly which should be the system/brew python with modules installed
python3 -m uvicorn main:app --reload &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# 2. Start Frontend in Background
echo "🎨 Starting Frontend Server (Port 4200)..."
cd "$PROJECT_ROOT/projects/frontend"

# LOAD NVM (Node Version Manager)
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm

# Use correct node version
if command -v nvm &> /dev/null; then
    nvm use 20 || nvm use default
fi

npm start &
FRONTEND_PID=$!

echo "✅ Both servers running. Press Ctrl+C to stop."
wait

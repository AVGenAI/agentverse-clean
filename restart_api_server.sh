#!/bin/bash

echo "🔄 Restarting AgentVerse API Server..."

# Kill any existing processes on port 8000
echo "Stopping existing server..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Navigate to API directory
cd /Users/vallu/z_AV_Labs_Gemini_June2025/aiagents/agentverse_api

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Using existing virtual environment"
    source venv/bin/activate
fi

# Start the server
echo "🚀 Starting API server on port 8000..."
uvicorn main:app --reload --port 8000 --log-level info
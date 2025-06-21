#!/bin/bash

echo "🚀 Starting AgentVerse Complete System"
echo "====================================="

# Kill any existing processes
echo "🔄 Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 2

# Start API server
echo ""
echo "📡 Starting API Backend (Port 8000)..."
cd /Users/vallu/z_AV_Labs_Gemini_June2025/aiagents/agentverse_api
./venv/bin/uvicorn main:app --reload --port 8000 --log-level info &
API_PID=$!
echo "API Server PID: $API_PID"

# Wait for API to be ready
echo "Waiting for API to start..."
sleep 5

# Test API
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ API is running!"
else
    echo "❌ API failed to start"
    exit 1
fi

# Start UI server
echo ""
echo "🎨 Starting UI Frontend..."
cd /Users/vallu/z_AV_Labs_Gemini_June2025/aiagents/agentverse_ui
npm run dev &
UI_PID=$!
echo "UI Server PID: $UI_PID"

# Wait a bit
sleep 5

echo ""
echo "✅ Both servers should be running!"
echo "====================================="
echo "📍 API Backend: http://localhost:8000"
echo "📍 UI Frontend: http://localhost:3000 (or check console output above)"
echo "📍 Health Check: http://localhost:8000/health"
echo ""
echo "To stop servers: kill $API_PID $UI_PID"
echo ""
echo "🎯 Quick Links:"
echo "   - MCP Integration: http://localhost:3000/mcp-integration"
echo "   - Chat: http://localhost:3000/chat"
echo "   - SRE Agent: Look for 'SRE ServiceNow Specialist' with ⭐"
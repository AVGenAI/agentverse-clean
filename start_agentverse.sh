#!/bin/bash

# AgentVerse Platform Startup Script
# This script starts both the FastAPI backend and React frontend

echo "🚀 Starting AgentVerse Platform..."
echo "=================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16 or higher.${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${BLUE}🛑 Stopping AgentVerse services...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up trap for cleanup
trap cleanup INT TERM

# Start Backend
echo -e "${BLUE}📡 Starting AgentVerse API Backend...${NC}"
cd agentverse_api

# Install backend dependencies if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -q -r requirements.txt 2>/dev/null || {
    echo -e "${RED}❌ Failed to install backend dependencies${NC}"
    exit 1
}

# Start FastAPI backend
uvicorn main:app --reload --port 8000 --log-level info &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Backend started successfully!${NC}"

# Start Frontend
echo -e "\n${BLUE}🎨 Starting AgentVerse UI Frontend...${NC}"
cd ../agentverse_ui

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start React frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to start..."
sleep 5

echo -e "\n${GREEN}✨ AgentVerse Platform is running!${NC}"
echo "=================================="
echo -e "${BLUE}🌐 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}📡 Backend API:${NC} http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo "=================================="
echo -e "Press ${RED}Ctrl+C${NC} to stop all services"

# Keep script running
wait
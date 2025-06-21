@echo off
REM AgentVerse Platform Startup Script for Windows
REM This script starts both the FastAPI backend and React frontend

echo Starting AgentVerse Platform...
echo ==================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python 3 is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed. Please install Node.js 16 or higher.
    pause
    exit /b 1
)

REM Start Backend in new window
echo Starting AgentVerse API Backend...
cd agentverse_api

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Start backend in new window
start "AgentVerse Backend" cmd /k "venv\Scripts\activate && pip install -q -r requirements.txt && uvicorn main:app --reload --port 8000"

REM Wait for backend to start
echo Waiting for backend to start...
timeout /t 10 /nobreak >nul

REM Start Frontend in new window
echo Starting AgentVerse UI Frontend...
cd ..\agentverse_ui

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

REM Start frontend in new window
start "AgentVerse Frontend" cmd /k "npm run dev"

REM Display success message
echo.
echo AgentVerse Platform is running!
echo ==================================
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo ==================================
echo Close this window to keep services running
echo Or press Ctrl+C in each window to stop services
echo.
pause
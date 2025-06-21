# AgentVerse Web UI Setup Guide

## Overview
AgentVerse provides a modern web interface for managing and interacting with AI agents. The platform consists of a FastAPI backend and a React frontend.

## Architecture
```
AgentVerse Platform
├── Backend (FastAPI)
│   ├── REST API endpoints
│   ├── WebSocket support
│   └── Agent management
└── Frontend (React + Vite)
    ├── Dashboard
    ├── Agent Browser
    ├── Chat Interface
    ├── Team Builder
    └── Marketplace (Coming Soon)
```

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager

### One-Command Setup
```bash
# Run the startup script
./start_agentverse.sh
```

This will:
1. Install all dependencies
2. Start the FastAPI backend on http://localhost:8000
3. Start the React frontend on http://localhost:3000
4. Open your browser to the AgentVerse dashboard

### Manual Setup

#### Backend Setup
```bash
cd agentverse_api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend
uvicorn main:app --reload --port 8000
```

#### Frontend Setup
```bash
cd agentverse_ui

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Features

### 1. Dashboard
- Real-time platform statistics
- Agent distribution by domain
- System health monitoring
- Quick action buttons

### 2. Agent Browser
- Search and filter 1000+ agents
- View agent capabilities and skills
- Direct chat initiation
- Team assembly integration

### 3. Chat Interface
- Real-time conversations with agents
- Session management
- Message history
- Agent expertise display

### 4. Team Builder
- Select project types (E-commerce, Mobile App, Data Platform)
- Specify custom requirements
- Automatic team assembly based on skills
- Team composition visualization

### 5. Marketplace (Coming Soon)
- Pre-built agent team templates
- Community contributions
- One-click deployment

## API Endpoints

### Core Endpoints
- `GET /health` - Health check
- `GET /agents/{agent_id}` - Get specific agent
- `POST /agents` - Query agents with filters
- `GET /domains` - List all domains
- `POST /search` - Full-text search

### Team Management
- `POST /team/assemble` - Build optimal team
- `GET /team/{team_id}` - Get team details

### Chat System
- `POST /chat/session` - Create chat session
- `POST /chat/message` - Send message
- `WS /ws` - WebSocket connection

## Configuration

### Environment Variables
Create a `.env` file in the `agentverse_api` directory:
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI Configuration (optional)
OPENAI_API_KEY=your_api_key_here

# Database (if needed)
DATABASE_URL=postgresql://user:password@localhost/agentverse

# Redis (for caching)
REDIS_URL=redis://localhost:6379
```

### Frontend Configuration
The frontend is configured to proxy API requests through Vite:
- API calls to `/api/*` are proxied to `http://localhost:8000`
- WebSocket connections are proxied to `ws://localhost:8000`

## Development

### Backend Development
```bash
# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest

# Format code
black .
```

### Frontend Development
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill process on port 8000 (backend)
   lsof -ti:8000 | xargs kill -9
   
   # Kill process on port 3000 (frontend)
   lsof -ti:3000 | xargs kill -9
   ```

2. **CORS Errors**
   - Ensure backend is running on port 8000
   - Check that frontend proxy configuration is correct

3. **WebSocket Connection Failed**
   - Verify WebSocket support in your environment
   - Check firewall settings

4. **Missing Dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt --upgrade
   
   # Frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

## Production Deployment

### Backend Deployment
```bash
# Using Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t agentverse-api .
docker run -p 8000:8000 agentverse-api
```

### Frontend Deployment
```bash
# Build static files
npm run build

# Serve with nginx or any static file server
# Files will be in dist/ directory
```

## Next Steps

1. **Add Authentication**
   - Implement user registration/login
   - Add JWT token support
   - Secure API endpoints

2. **Enhance Chat Features**
   - Add file uploads
   - Implement voice chat
   - Add conversation export

3. **Expand Team Builder**
   - Add more project templates
   - Implement team performance tracking
   - Add collaboration tools

4. **Complete Marketplace**
   - Build template submission system
   - Add rating and review features
   - Implement one-click deployment

## Support

For issues or questions:
- Check the [GitHub Issues](https://github.com/agentverse/platform/issues)
- Join our [Discord Community](https://discord.gg/agentverse)
- Email: support@agentverse.ai
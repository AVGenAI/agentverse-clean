# 🐳 AgentVerse Docker Setup

## Quick Start

```bash
# Run once
./docker_test.sh once

# Run in infinite loop for testing
./docker_test.sh loop
```

## Manual Commands

```bash
# Build and start all services
docker-compose up --build -d

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

## Services

- **PostgreSQL**: Port 5432 - Relational database
- **Redis**: Port 6379 - Cache layer
- **MongoDB**: Port 27017 - Document store
- **Backend API**: Port 8000 - FastAPI service
- **Frontend UI**: Port 3000 - React application
- **Nginx**: Ports 80/443 - Reverse proxy

## Optional Services

Enable with profiles:

```bash
# With Ollama (local LLM)
docker-compose --profile with-ollama up -d

# With ServiceNow MCP
docker-compose --profile with-mcp up -d
```

## Development Mode

The `docker-compose.override.yml` enables hot reloading:

```bash
# Development mode (with hot reload)
docker-compose up -d

# Production mode (no override)
docker-compose -f docker-compose.yml up -d
```

## URLs

- API: http://localhost:8000
- UI: http://localhost:3000
- API Docs: http://localhost:8000/docs

## Troubleshooting

```bash
# Check logs for specific service
docker-compose logs backend
docker-compose logs frontend

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend

# Reset everything
docker-compose down -v
docker system prune -af
```
# 🗄️ AgentVerse Database Setup Guide

## Overview

AgentVerse now supports massive scale with three databases working in harmony:

1. **PostgreSQL** - Structured data, relationships, and fast queries
2. **Redis** - High-speed caching and real-time data
3. **MongoDB** - Full agent documents and chat history

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   PostgreSQL    │     │     Redis       │     │    MongoDB      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ • Agent basics  │     │ • Agent cache   │     │ • Full agents   │
│ • Relationships │     │ • Session data  │     │ • Chat history  │
│ • Chat metadata │     │ • Fast lookups  │     │ • Documents     │
│ • Analytics     │     │ • Sorted sets   │     │ • Flexible data │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Features

### 1. Bulk Agent Management
- Generate 10K, 100K, or 1M agents with diverse characteristics
- Balanced distribution across domains
- Realistic metadata and capabilities

### 2. Chat History Storage
- Complete conversation tracking
- Tool usage logging
- Token consumption metrics
- Session management

### 3. High-Performance Retrieval
- Redis caching for <1ms lookups
- PostgreSQL indexes for complex queries
- MongoDB full-text search

### 4. Scalability
- Optimized for 1M+ agents
- Batch processing
- Connection pooling
- Async operations

## Quick Start

### 1. Start Databases
```bash
./setup_databases.sh
```

### 2. Generate & Load Agents

**10,000 agents (Development)**
```bash
python database/setup_and_load.py --count 10000
```

**100,000 agents (Testing)**
```bash
python database/setup_and_load.py --count 100000
```

**1,000,000 agents (Production)**
```bash
python database/setup_and_load.py --count 1000000
```

### 3. Test Performance
```bash
python database/setup_and_load.py --test
```

## Database Schema

### PostgreSQL Tables
- `agents` - Core agent data
- `agent_metadata` - Extended properties
- `agent_capabilities` - Skills and tools
- `chat_sessions` - Conversation tracking
- `chat_messages` - Individual messages
- `chat_tool_usage` - Tool execution logs

### Redis Keys
- `agent:{id}` - Cached agent data
- `agents:domain:{domain}` - Domain sets
- `agents:by_trust` - Trust score sorted set
- `chat:session:{id}` - Recent messages

### MongoDB Collections
- `agents` - Complete agent documents
- `chat_history` - Full conversation logs

## API Integration

The API automatically uses databases when available:

```python
# Chat endpoint saves history
@app.post("/chat/message")
async def send_message(request):
    # ... get response ...
    await APIDatabase.save_chat_interaction(
        session_id=request.session_id,
        agent_id=session.agent_id,
        user_message=request.message,
        agent_response=response
    )
```

## Performance Benchmarks

With proper setup, expect:
- **Single agent lookup**: <5ms
- **Domain search (100 results)**: <50ms
- **Chat message save**: <10ms
- **Bulk insert rate**: 10,000+ agents/second

## Monitoring

View database status:
```bash
# Docker containers
cd database && docker-compose ps

# Logs
docker-compose logs -f

# PostgreSQL
docker exec -it agentverse_postgres psql -U postgres -d agentverse -c "SELECT COUNT(*) FROM agents;"

# Redis
docker exec -it agentverse_redis redis-cli DBSIZE

# MongoDB
docker exec -it agentverse_mongodb mongosh agentverse --eval "db.agents.countDocuments()"
```

## Troubleshooting

1. **Containers not starting**
   - Check ports 5432, 6379, 27017 are free
   - Ensure Docker is running

2. **Slow performance**
   - Check indexes are created
   - Monitor connection pools
   - Verify Redis is being used

3. **Out of memory**
   - Adjust Docker memory limits
   - Reduce batch sizes
   - Configure Redis maxmemory

---

The system is now ready to handle millions of agents with full chat history tracking! 🚀
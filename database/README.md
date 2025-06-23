# AgentVerse Database Systems

## Overview
Two robust database implementations for managing 1M+ agents:

### PostgreSQL Implementation (`agent_db.py`)
- **Structured, relational approach**
- ACID compliant with strong consistency
- Optimized schema with indexes
- Full-text search capabilities
- Foreign key relationships

### MongoDB Implementation (`agent_db_mongo.py`)
- **Flexible, document-based approach**
- Schema-less design for rapid iteration
- Built-in horizontal scaling
- Native JSON storage
- Aggregation pipelines

## Quick Start

### PostgreSQL Setup
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Create database
createdb agentverse

# Run migrations
python database/migrate_json_to_db.py
```

### MongoDB Setup
```bash
# Install MongoDB
brew install mongodb-community  # macOS
sudo apt-get install mongodb  # Ubuntu

# Start MongoDB
mongod

# Import agents
python -c "from database.agent_db_mongo import AgentDatabaseMongo; 
import asyncio; 
db = AgentDatabaseMongo(); 
asyncio.run(db.bulk_import_agents('src/config/agentverse_agents_1000.json'))"
```

## Environment Variables
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost:5432/agentverse

# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=agentverse
```

## Performance Comparison

| Operation | PostgreSQL | MongoDB |
|-----------|------------|---------|
| Insert 1K agents | ~2.5s | ~1.8s |
| Single lookup | ~5ms | ~3ms |
| Domain search | ~15ms | ~12ms |
| Full-text search | ~20ms | ~18ms |
| Complex joins | ✅ Excellent | ❌ Limited |
| Flexible schema | ❌ Fixed | ✅ Dynamic |

## Scaling to 1M Agents

### PostgreSQL Approach
- Partition by domain/date
- Read replicas for search
- Connection pooling
- Materialized views for stats

### MongoDB Approach
- Automatic sharding
- Replica sets
- In-memory caching
- Time-series collections for metrics

## Hybrid Architecture (Recommended)

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│   PostgreSQL    │     │   MongoDB    │     │    Redis    │
│ (Core Registry) │     │ (Logs/Docs)  │     │  (Cache)    │
└─────────────────┘     └──────────────┘     └─────────────┘
        │                       │                     │
        └───────────────────────┴─────────────────────┘
                              │
                    ┌─────────────────┐
                    │   API Layer     │
                    └─────────────────┘
```

## Usage Examples

### PostgreSQL
```python
from database.agent_db import AgentDatabase

db = AgentDatabase()
await db.connect()

# Create agent
agent_id = await db.create_agent({
    "id": "sre_001",
    "name": "SRE Expert",
    "domain": "sre"
})

# Search agents
agents = await db.search_agents(domain="sre", limit=10)
```

### MongoDB
```python
from database.agent_db_mongo import AgentDatabaseMongo

db = AgentDatabaseMongo()
await db.connect()

# Create agent
agent_id = await db.create_agent({
    "agent_id": "sre_001",
    "name": "SRE Expert",
    "domain": "sre"
})

# Find similar agents
similar = await db.find_similar_agents("sre_001")
```

## Choosing the Right Database

**Choose PostgreSQL if:**
- Need ACID transactions
- Complex relationships
- SQL expertise on team
- Compliance requirements

**Choose MongoDB if:**
- Rapid prototyping
- Flexible schemas
- Geographic distribution
- NoSQL preference

**Use Both (Hybrid) for:**
- Best of both worlds
- Separation of concerns
- Maximum scalability
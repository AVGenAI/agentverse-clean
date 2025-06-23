#!/usr/bin/env python3
"""
Database Manager for AgentVerse
Handles PostgreSQL, Redis, and MongoDB connections
Optimized for handling 1M+ agents
"""
import os
import json
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import asynccontextmanager

import asyncpg
import redis.asyncio as redis
import motor.motor_asyncio
from pymongo import IndexModel, ASCENDING, TEXT
import uuid

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Unified database manager for AgentVerse"""
    
    def __init__(self):
        self.postgres_pool = None
        self.redis_client = None
        self.mongo_client = None
        self.mongo_db = None
        
    async def initialize(self):
        """Initialize all database connections"""
        await self._init_postgres()
        await self._init_redis()
        await self._init_mongodb()
        logger.info("✅ All databases initialized")
        
    async def _init_postgres(self):
        """Initialize PostgreSQL connection pool"""
        self.postgres_pool = await asyncpg.create_pool(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            user=os.getenv('POSTGRES_USER', 'postgres'),
            password=os.getenv('POSTGRES_PASSWORD', 'postgres'),
            database=os.getenv('POSTGRES_DB', 'agentverse'),
            min_size=10,
            max_size=20,
            command_timeout=60
        )
        logger.info("✅ PostgreSQL connected")
        
    async def _init_redis(self):
        """Initialize Redis connection"""
        self.redis_client = await redis.from_url(
            f"redis://{os.getenv('REDIS_HOST', 'localhost')}:{os.getenv('REDIS_PORT', 6379)}",
            encoding="utf-8",
            decode_responses=True,
            max_connections=50
        )
        await self.redis_client.ping()
        logger.info("✅ Redis connected")
        
    async def _init_mongodb(self):
        """Initialize MongoDB connection"""
        mongo_url = f"mongodb://{os.getenv('MONGO_HOST', 'localhost')}:{os.getenv('MONGO_PORT', 27017)}"
        self.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
            mongo_url,
            maxPoolSize=50
        )
        self.mongo_db = self.mongo_client[os.getenv('MONGO_DB', 'agentverse')]
        
        # Create indexes for agents collection
        agents_collection = self.mongo_db.agents
        await agents_collection.create_indexes([
            IndexModel([("enhanced_metadata.agent_uuid", ASCENDING)], unique=True),
            IndexModel([("enhanced_metadata.taxonomy.domain", ASCENDING)]),
            IndexModel([("enhanced_metadata.canonical_name", ASCENDING)]),
            IndexModel([("enhanced_metadata.display_name", TEXT)]),
            IndexModel([("enhanced_metadata.capabilities.primary_expertise", ASCENDING)]),
            IndexModel([("enhanced_metadata.quality.trust_score", ASCENDING)])
        ])
        
        # Create indexes for chat history
        chat_collection = self.mongo_db.chat_history
        await chat_collection.create_indexes([
            IndexModel([("session_id", ASCENDING)]),
            IndexModel([("agent_id", ASCENDING)]),
            IndexModel([("created_at", ASCENDING)])
        ])
        
        logger.info("✅ MongoDB connected and indexed")
        
    async def close(self):
        """Close all database connections"""
        if self.postgres_pool:
            await self.postgres_pool.close()
        if self.redis_client:
            await self.redis_client.close()
        if self.mongo_client:
            self.mongo_client.close()
            
    # === Agent Management ===
    
    async def bulk_insert_agents(self, agents: List[Dict[str, Any]], batch_size: int = 1000):
        """Bulk insert agents into all databases"""
        total = len(agents)
        inserted = 0
        
        for i in range(0, total, batch_size):
            batch = agents[i:i + batch_size]
            
            # PostgreSQL: Insert basic agent data
            await self._bulk_insert_postgres(batch)
            
            # MongoDB: Insert full agent documents
            await self._bulk_insert_mongodb(batch)
            
            # Redis: Cache frequently accessed agents
            await self._cache_agents_redis(batch)
            
            inserted += len(batch)
            logger.info(f"Inserted {inserted}/{total} agents")
            
        return inserted
        
    async def _bulk_insert_postgres(self, agents: List[Dict[str, Any]]):
        """Bulk insert agents into PostgreSQL"""
        async with self.postgres_pool.acquire() as conn:
            # Prepare agent data
            agent_records = []
            metadata_records = []
            capability_records = []
            
            for agent in agents:
                agent_uuid = str(uuid.uuid4())
                meta = agent.get("enhanced_metadata", {})
                
                # Main agent record
                agent_records.append((
                    agent_uuid,
                    meta.get("agent_uuid"),
                    meta.get("display_name"),
                    meta.get("taxonomy", {}).get("type", "specialist"),
                    meta.get("taxonomy", {}).get("domain", "general"),
                    meta.get("taxonomy", {}).get("specialization"),
                    meta.get("version", "1.0.0"),
                    "active",
                    agent.get("instructions")
                ))
                
                # Metadata record
                metadata_records.append((
                    agent_uuid,
                    meta.get("canonical_name"),
                    meta.get("display_name"),
                    meta.get("avatar_emoji"),
                    meta.get("quality", {}).get("trust_score", 0.8),
                    meta.get("quality", {}).get("reliability_score", 0.8),
                    float(meta.get("performance", {}).get("avg_response_time", "2.0").rstrip("s")),
                    meta.get("collaboration", {}).get("style", ["collaborative"])[0]
                ))
                
                # Capabilities
                for skill in meta.get("capabilities", {}).get("primary_expertise", []):
                    capability_records.append((
                        agent_uuid,
                        "expertise",
                        skill,
                        "expert"
                    ))
                    
            # Execute bulk inserts
            await conn.executemany("""
                INSERT INTO agents (id, agent_id, name, type, domain, subdomain, version, status, instructions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (agent_id) DO NOTHING
            """, agent_records)
            
            await conn.executemany("""
                INSERT INTO agent_metadata (agent_id, canonical_name, display_name, avatar, trust_score, reliability_rating, response_time_avg, collaboration_style)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (agent_id) DO NOTHING
            """, metadata_records)
            
            await conn.executemany("""
                INSERT INTO agent_capabilities (agent_id, capability_type, capability_name, capability_level)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (agent_id, capability_type, capability_name) DO NOTHING
            """, capability_records)
            
    async def _bulk_insert_mongodb(self, agents: List[Dict[str, Any]]):
        """Bulk insert agents into MongoDB"""
        collection = self.mongo_db.agents
        
        # Add insertion timestamp
        for agent in agents:
            agent["inserted_at"] = datetime.utcnow()
            agent["_id"] = agent["enhanced_metadata"]["agent_uuid"]
            
        await collection.insert_many(agents, ordered=False)
        
    async def _cache_agents_redis(self, agents: List[Dict[str, Any]]):
        """Cache agents in Redis for fast access"""
        pipe = self.redis_client.pipeline()
        
        for agent in agents:
            agent_id = agent["enhanced_metadata"]["agent_uuid"]
            
            # Cache full agent data
            pipe.setex(
                f"agent:{agent_id}",
                3600,  # 1 hour TTL
                json.dumps(agent)
            )
            
            # Add to domain set
            domain = agent["enhanced_metadata"]["taxonomy"]["domain"]
            pipe.sadd(f"agents:domain:{domain}", agent_id)
            
            # Add to trust score sorted set
            trust_score = agent["enhanced_metadata"]["quality"]["trust_score"]
            pipe.zadd("agents:by_trust", {agent_id: trust_score})
            
        await pipe.execute()
        
    # === Agent Retrieval ===
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID with caching"""
        # Try Redis first
        cached = await self.redis_client.get(f"agent:{agent_id}")
        if cached:
            return json.loads(cached)
            
        # Fallback to MongoDB
        agent = await self.mongo_db.agents.find_one({"_id": agent_id})
        
        if agent:
            # Cache for next time
            await self.redis_client.setex(
                f"agent:{agent_id}",
                3600,
                json.dumps(agent, default=str)
            )
            
        return agent
        
    async def search_agents(
        self,
        query: Optional[str] = None,
        domain: Optional[str] = None,
        skills: Optional[List[str]] = None,
        min_trust_score: float = 0.0,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search agents with various filters"""
        # Build MongoDB query
        mongo_query = {}
        
        if domain:
            mongo_query["enhanced_metadata.taxonomy.domain"] = domain
            
        if skills:
            mongo_query["enhanced_metadata.capabilities.primary_expertise"] = {
                "$in": skills
            }
            
        if min_trust_score > 0:
            mongo_query["enhanced_metadata.quality.trust_score"] = {
                "$gte": min_trust_score
            }
            
        if query:
            mongo_query["$text"] = {"$search": query}
            
        # Execute search
        cursor = self.mongo_db.agents.find(mongo_query).skip(offset).limit(limit)
        
        agents = []
        async for agent in cursor:
            agents.append(agent)
            
        return agents
        
    # === Chat History ===
    
    async def save_chat_message(
        self,
        session_id: str,
        agent_id: str,
        message_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None
    ):
        """Save chat message to both PostgreSQL and MongoDB"""
        message_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # PostgreSQL: Structured data
        async with self.postgres_pool.acquire() as conn:
            # Get agent UUID
            agent_uuid = await conn.fetchval(
                "SELECT id FROM agents WHERE agent_id = $1",
                agent_id
            )
            
            if agent_uuid:
                # Ensure session exists
                await conn.execute("""
                    INSERT INTO chat_sessions (session_id, agent_id, user_id)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (session_id) DO NOTHING
                """, session_id, agent_uuid, "default_user")
                
                # Get session UUID
                session_uuid = await conn.fetchval(
                    "SELECT id FROM chat_sessions WHERE session_id = $1",
                    session_id
                )
                
                # Insert message
                await conn.execute("""
                    INSERT INTO chat_messages (id, session_id, message_type, content, metadata, tokens_used, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                """, message_id, session_uuid, message_type, content, json.dumps(metadata), tokens_used, timestamp)
                
        # MongoDB: Full document
        await self.mongo_db.chat_history.insert_one({
            "_id": message_id,
            "session_id": session_id,
            "agent_id": agent_id,
            "message_type": message_type,
            "content": content,
            "metadata": metadata,
            "tokens_used": tokens_used,
            "created_at": timestamp
        })
        
        # Redis: Cache recent messages
        await self.redis_client.lpush(
            f"chat:session:{session_id}",
            json.dumps({
                "id": message_id,
                "type": message_type,
                "content": content,
                "timestamp": timestamp.isoformat()
            })
        )
        await self.redis_client.ltrim(f"chat:session:{session_id}", 0, 99)  # Keep last 100
        await self.redis_client.expire(f"chat:session:{session_id}", 3600)  # 1 hour TTL
        
    async def get_chat_history(
        self,
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get chat history"""
        query = {}
        
        if session_id:
            query["session_id"] = session_id
        if agent_id:
            query["agent_id"] = agent_id
            
        cursor = self.mongo_db.chat_history.find(query).sort("created_at", -1).limit(limit)
        
        messages = []
        async for msg in cursor:
            messages.append(msg)
            
        return list(reversed(messages))
        
    # === Analytics ===
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get overall agent statistics"""
        async with self.postgres_pool.acquire() as conn:
            total_agents = await conn.fetchval("SELECT COUNT(*) FROM agents")
            
            domain_stats = await conn.fetch("""
                SELECT domain, COUNT(*) as count
                FROM agents
                GROUP BY domain
                ORDER BY count DESC
            """)
            
            avg_trust_score = await conn.fetchval("""
                SELECT AVG(trust_score) FROM agent_metadata
            """)
            
        # Get Redis stats
        active_sessions = await self.redis_client.dbsize()
        
        return {
            "total_agents": total_agents,
            "domains": {row["domain"]: row["count"] for row in domain_stats},
            "avg_trust_score": float(avg_trust_score) if avg_trust_score else 0.0,
            "active_sessions": active_sessions
        }

# Global instance
db_manager = DatabaseManager()

async def initialize_databases():
    """Initialize all databases"""
    await db_manager.initialize()
    
async def close_databases():
    """Close all database connections"""
    await db_manager.close()
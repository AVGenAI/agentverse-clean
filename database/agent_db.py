#!/usr/bin/env python3
"""
AgentVerse PostgreSQL Database Manager
Handles storage and retrieval of 1M+ agents efficiently
"""
import os
import json
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import asynccontextmanager
import asyncpg
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentDatabase:
    """PostgreSQL database manager for AgentVerse agents"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5432/agentverse"
        )
        self.pool = None
        
    async def connect(self):
        """Create connection pool"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=10,
            max_size=20,
            command_timeout=60
        )
        logger.info("Connected to PostgreSQL database")
        
    async def disconnect(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Disconnected from database")
            
    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool"""
        async with self.pool.acquire() as connection:
            yield connection
            
    async def create_tables(self):
        """Create database tables from schema"""
        with open("database/schema.sql", "r") as f:
            schema = f.read()
            
        async with self.acquire() as conn:
            await conn.execute(schema)
            logger.info("Database tables created successfully")
            
    async def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """Create a new agent"""
        async with self.acquire() as conn:
            # Insert main agent record
            agent_record = await conn.fetchrow("""
                INSERT INTO agents (agent_id, name, type, domain, subdomain, 
                                  version, status, instructions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
            """, 
                agent_data["id"],
                agent_data["name"],
                agent_data.get("type", "specialist"),
                agent_data["domain"],
                agent_data.get("subdomain"),
                agent_data.get("version", "1.0.0"),
                agent_data.get("status", "active"),
                agent_data.get("instructions", "")
            )
            
            agent_uuid = agent_record["id"]
            
            # Insert metadata
            metadata = agent_data.get("enhanced_metadata", {})
            if metadata:
                await conn.execute("""
                    INSERT INTO agent_metadata 
                    (agent_id, canonical_name, display_name, avatar, trust_score,
                     reliability_rating, response_time_avg, collaboration_style)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                    agent_uuid,
                    metadata.get("canonical_name", f"agentverse.{agent_data['domain']}.{agent_data['id']}"),
                    metadata.get("display_name", agent_data["name"]),
                    metadata.get("avatar", "🤖"),
                    metadata.get("trust_score", 0.80),
                    metadata.get("reliability_rating", 0.80),
                    metadata.get("response_time_avg", 2.0),
                    metadata.get("collaboration_style", "collaborative")
                )
            
            # Insert capabilities
            capabilities = agent_data.get("capabilities", {})
            
            # Primary expertise
            for expertise in capabilities.get("primary_expertise", []):
                await conn.execute("""
                    INSERT INTO agent_capabilities (agent_id, capability_type, 
                                                  capability_name, capability_level)
                    VALUES ($1, 'expertise', $2, 'expert')
                """, agent_uuid, expertise)
            
            # Tools mastery
            for tool, level in capabilities.get("tools_mastery", {}).items():
                await conn.execute("""
                    INSERT INTO agent_capabilities (agent_id, capability_type,
                                                  capability_name, capability_level)
                    VALUES ($1, 'tool', $2, $3)
                """, agent_uuid, tool, level)
            
            # Tools
            for tool_name in agent_data.get("tools", []):
                await conn.execute("""
                    INSERT INTO agent_tools (agent_id, tool_name, is_active)
                    VALUES ($1, $2, true)
                """, agent_uuid, tool_name)
            
            # Model preferences
            model_prefs = agent_data.get("model_preferences", {})
            if model_prefs:
                await conn.execute("""
                    INSERT INTO agent_model_preferences
                    (agent_id, llm_provider, primary_model, fallback_model, reasoning_model)
                    VALUES ($1, $2, $3, $4, $5)
                """,
                    agent_uuid,
                    model_prefs.get("llm_provider", "openai"),
                    model_prefs.get("primary", "gpt-4o-mini"),
                    model_prefs.get("fallback", "gpt-3.5-turbo"),
                    model_prefs.get("reasoning")
                )
            
            logger.info(f"Created agent: {agent_data['id']} ({agent_uuid})")
            return str(agent_uuid)
            
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID"""
        async with self.acquire() as conn:
            # Try both UUID and agent_id
            agent = await conn.fetchrow("""
                SELECT a.*, m.*, 
                       array_agg(DISTINCT c.capability_name) FILTER (WHERE c.capability_type = 'expertise') as expertise,
                       array_agg(DISTINCT t.tool_name) FILTER (WHERE t.tool_name IS NOT NULL) as tools
                FROM agents a
                LEFT JOIN agent_metadata m ON a.id = m.agent_id
                LEFT JOIN agent_capabilities c ON a.id = c.agent_id
                LEFT JOIN agent_tools t ON a.id = t.agent_id
                WHERE a.agent_id = $1 OR a.id::text = $1
                GROUP BY a.id, m.agent_id
            """, agent_id)
            
            if not agent:
                return None
                
            return self._format_agent(agent)
            
    async def search_agents(
        self, 
        query: Optional[str] = None,
        domain: Optional[str] = None,
        subdomain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search agents with various filters"""
        async with self.acquire() as conn:
            where_clauses = ["a.status = 'active'"]
            params = []
            param_count = 0
            
            if query:
                param_count += 1
                params.append(query)
                where_clauses.append(f"a.search_vector @@ plainto_tsquery('english', ${param_count})")
            
            if domain:
                param_count += 1
                params.append(domain)
                where_clauses.append(f"a.domain = ${param_count}")
                
            if subdomain:
                param_count += 1
                params.append(subdomain)
                where_clauses.append(f"a.subdomain = ${param_count}")
            
            param_count += 1
            params.append(limit)
            limit_param = f"${param_count}"
            
            param_count += 1
            params.append(offset)
            offset_param = f"${param_count}"
            
            where_clause = " AND ".join(where_clauses)
            
            agents = await conn.fetch(f"""
                SELECT a.*, m.*,
                       array_agg(DISTINCT c.capability_name) FILTER (WHERE c.capability_type = 'expertise') as expertise,
                       array_agg(DISTINCT t.tool_name) FILTER (WHERE t.tool_name IS NOT NULL) as tools
                FROM agents a
                LEFT JOIN agent_metadata m ON a.id = m.agent_id
                LEFT JOIN agent_capabilities c ON a.id = c.agent_id
                LEFT JOIN agent_tools t ON a.id = t.agent_id
                WHERE {where_clause}
                GROUP BY a.id, m.agent_id
                ORDER BY m.trust_score DESC NULLS LAST
                LIMIT {limit_param} OFFSET {offset_param}
            """, *params)
            
            return [self._format_agent(agent) for agent in agents]
            
    async def update_agent_metrics(self, agent_id: str, success: bool, response_time: float):
        """Update agent performance metrics"""
        async with self.acquire() as conn:
            # Get agent UUID
            agent_uuid = await conn.fetchval(
                "SELECT id FROM agents WHERE agent_id = $1",
                agent_id
            )
            
            if not agent_uuid:
                return
                
            # Upsert today's metrics
            await conn.execute("""
                INSERT INTO agent_metrics (agent_id, metric_date, interactions_count,
                                         success_count, error_count, avg_response_time)
                VALUES ($1, CURRENT_DATE, 1, $2, $3, $4)
                ON CONFLICT (agent_id, metric_date)
                DO UPDATE SET
                    interactions_count = agent_metrics.interactions_count + 1,
                    success_count = agent_metrics.success_count + $2,
                    error_count = agent_metrics.error_count + $3,
                    avg_response_time = (
                        (agent_metrics.avg_response_time * agent_metrics.interactions_count + $4) /
                        (agent_metrics.interactions_count + 1)
                    )
            """, 
                agent_uuid,
                1 if success else 0,
                0 if success else 1,
                response_time
            )
            
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get overall agent statistics"""
        async with self.acquire() as conn:
            stats = await conn.fetchrow("""
                SELECT 
                    COUNT(*) as total_agents,
                    COUNT(DISTINCT domain) as total_domains,
                    COUNT(DISTINCT subdomain) as total_subdomains,
                    AVG(m.trust_score) as avg_trust_score,
                    AVG(m.reliability_rating) as avg_reliability
                FROM agents a
                LEFT JOIN agent_metadata m ON a.id = m.agent_id
                WHERE a.status = 'active'
            """)
            
            domain_breakdown = await conn.fetch("""
                SELECT domain, COUNT(*) as count
                FROM agents
                WHERE status = 'active'
                GROUP BY domain
                ORDER BY count DESC
            """)
            
            return {
                "total_agents": stats["total_agents"],
                "total_domains": stats["total_domains"],
                "total_subdomains": stats["total_subdomains"],
                "avg_trust_score": float(stats["avg_trust_score"] or 0),
                "avg_reliability": float(stats["avg_reliability"] or 0),
                "domains": {row["domain"]: row["count"] for row in domain_breakdown}
            }
            
    async def bulk_import_agents(self, json_file: str):
        """Import agents from JSON file"""
        with open(json_file, "r") as f:
            agents = json.load(f)
            
        logger.info(f"Importing {len(agents)} agents...")
        
        success_count = 0
        error_count = 0
        
        # Process in batches for efficiency
        batch_size = 100
        for i in range(0, len(agents), batch_size):
            batch = agents[i:i + batch_size]
            
            for agent in batch:
                try:
                    await self.create_agent(agent)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error importing agent {agent.get('id')}: {e}")
                    error_count += 1
            
            logger.info(f"Progress: {i + len(batch)}/{len(agents)}")
            
        logger.info(f"Import complete: {success_count} success, {error_count} errors")
        
    def _format_agent(self, record) -> Dict[str, Any]:
        """Format database record to agent dictionary"""
        return {
            "id": record["agent_id"],
            "uuid": str(record["id"]),
            "name": record["name"],
            "type": record["type"],
            "domain": record["domain"],
            "subdomain": record["subdomain"],
            "version": record["version"],
            "status": record["status"],
            "instructions": record["instructions"],
            "enhanced_metadata": {
                "canonical_name": record.get("canonical_name"),
                "display_name": record.get("display_name"),
                "avatar": record.get("avatar"),
                "trust_score": float(record.get("trust_score", 0.80)),
                "reliability_rating": float(record.get("reliability_rating", 0.80)),
                "response_time_avg": float(record.get("response_time_avg", 2.0)),
                "collaboration_style": record.get("collaboration_style")
            },
            "capabilities": {
                "primary_expertise": record.get("expertise", []),
            },
            "tools": record.get("tools", []),
            "created_at": record["created_at"].isoformat(),
            "updated_at": record["updated_at"].isoformat()
        }


async def main():
    """Test database operations"""
    db = AgentDatabase()
    await db.connect()
    
    try:
        # Create tables
        await db.create_tables()
        
        # Test creating an agent
        test_agent = {
            "id": "test_agent_001",
            "name": "Test Agent",
            "domain": "test",
            "subdomain": "demo",
            "instructions": "This is a test agent",
            "enhanced_metadata": {
                "display_name": "Test Agent Demo",
                "avatar": "🧪",
                "trust_score": 0.95
            },
            "capabilities": {
                "primary_expertise": ["Testing", "Demo"],
                "tools_mastery": {"pytest": "expert"}
            },
            "tools": ["test_tool", "demo_tool"]
        }
        
        agent_id = await db.create_agent(test_agent)
        print(f"Created agent: {agent_id}")
        
        # Test retrieving
        agent = await db.get_agent("test_agent_001")
        print(f"Retrieved agent: {agent}")
        
        # Test search
        agents = await db.search_agents(domain="test")
        print(f"Found {len(agents)} test agents")
        
        # Get stats
        stats = await db.get_agent_stats()
        print(f"Database stats: {stats}")
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
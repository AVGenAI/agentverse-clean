#!/usr/bin/env python3
"""
AgentVerse MongoDB Database Manager
NoSQL approach for 1M+ agents with flexible schema
"""
import os
import json
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import logging
from bson import ObjectId

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentDatabaseMongo:
    """MongoDB database manager for AgentVerse agents"""
    
    def __init__(self):
        self.mongo_url = os.getenv(
            "MONGODB_URL",
            "mongodb://localhost:27017"
        )
        self.db_name = os.getenv("MONGODB_DATABASE", "agentverse")
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.client[self.db_name]
        
        # Create indexes for performance
        await self._create_indexes()
        logger.info("Connected to MongoDB database")
        
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
            
    async def _create_indexes(self):
        """Create indexes for optimal performance"""
        agents_collection = self.db.agents
        
        # Create indexes
        await agents_collection.create_index("agent_id", unique=True)
        await agents_collection.create_index("domain")
        await agents_collection.create_index("subdomain")
        await agents_collection.create_index("status")
        await agents_collection.create_index("enhanced_metadata.trust_score")
        await agents_collection.create_index("enhanced_metadata.canonical_name", unique=True)
        
        # Text search index
        await agents_collection.create_index([
            ("name", "text"),
            ("instructions", "text"),
            ("domain", "text"),
            ("subdomain", "text")
        ])
        
        # Compound indexes for common queries
        await agents_collection.create_index([
            ("domain", 1),
            ("subdomain", 1),
            ("status", 1)
        ])
        
        logger.info("MongoDB indexes created")
        
    async def create_agent(self, agent_data: Dict[str, Any]) -> str:
        """Create a new agent"""
        agents_collection = self.db.agents
        
        # Add timestamps
        agent_data["created_at"] = datetime.utcnow()
        agent_data["updated_at"] = datetime.utcnow()
        
        # Ensure required fields
        agent_data.setdefault("status", "active")
        agent_data.setdefault("version", "1.0.0")
        agent_data.setdefault("type", "specialist")
        
        # Add default metadata if not present
        if "enhanced_metadata" not in agent_data:
            agent_data["enhanced_metadata"] = {
                "canonical_name": f"agentverse.{agent_data['domain']}.{agent_data['id']}",
                "display_name": agent_data["name"],
                "avatar": "🤖",
                "trust_score": 0.80,
                "reliability_rating": 0.80,
                "response_time_avg": 2.0,
                "collaboration_style": "collaborative"
            }
        
        # Add performance metrics subdocument
        agent_data["metrics"] = {
            "total_interactions": 0,
            "success_count": 0,
            "error_count": 0,
            "avg_response_time": 0,
            "last_active": datetime.utcnow()
        }
        
        # Insert the agent
        result = await agents_collection.insert_one(agent_data)
        agent_id = str(result.inserted_id)
        
        logger.info(f"Created agent: {agent_data['id']} (MongoDB ID: {agent_id})")
        return agent_id
        
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent by ID (either MongoDB _id or agent_id)"""
        agents_collection = self.db.agents
        
        # Try to find by agent_id first
        agent = await agents_collection.find_one({"agent_id": agent_id})
        
        # If not found, try MongoDB _id
        if not agent and ObjectId.is_valid(agent_id):
            agent = await agents_collection.find_one({"_id": ObjectId(agent_id)})
            
        if agent:
            agent["_id"] = str(agent["_id"])  # Convert ObjectId to string
            
        return agent
        
    async def search_agents(
        self, 
        query: Optional[str] = None,
        domain: Optional[str] = None,
        subdomain: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "enhanced_metadata.trust_score",
        sort_order: int = -1  # -1 for descending, 1 for ascending
    ) -> List[Dict[str, Any]]:
        """Search agents with various filters"""
        agents_collection = self.db.agents
        
        # Build query
        filter_query = {"status": "active"}
        
        if query:
            # Use text search
            filter_query["$text"] = {"$search": query}
            
        if domain:
            filter_query["domain"] = domain
            
        if subdomain:
            filter_query["subdomain"] = subdomain
            
        # Execute query with pagination
        cursor = agents_collection.find(filter_query)
        cursor = cursor.sort(sort_by, sort_order)
        cursor = cursor.skip(offset).limit(limit)
        
        agents = []
        async for agent in cursor:
            agent["_id"] = str(agent["_id"])
            agents.append(agent)
            
        return agents
        
    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> bool:
        """Update an agent"""
        agents_collection = self.db.agents
        
        # Add updated timestamp
        updates["updated_at"] = datetime.utcnow()
        
        # Update the agent
        result = await agents_collection.update_one(
            {"agent_id": agent_id},
            {"$set": updates}
        )
        
        return result.modified_count > 0
        
    async def update_agent_metrics(self, agent_id: str, success: bool, response_time: float):
        """Update agent performance metrics"""
        agents_collection = self.db.agents
        
        # Atomic update of metrics
        update_doc = {
            "$inc": {
                "metrics.total_interactions": 1,
                "metrics.success_count": 1 if success else 0,
                "metrics.error_count": 0 if success else 1
            },
            "$set": {
                "metrics.last_active": datetime.utcnow()
            }
        }
        
        # Update average response time
        agent = await self.get_agent(agent_id)
        if agent:
            current_metrics = agent.get("metrics", {})
            total = current_metrics.get("total_interactions", 0)
            current_avg = current_metrics.get("avg_response_time", 0)
            
            # Calculate new average
            new_avg = ((current_avg * total) + response_time) / (total + 1)
            update_doc["$set"]["metrics.avg_response_time"] = new_avg
            
        await agents_collection.update_one(
            {"agent_id": agent_id},
            update_doc
        )
        
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get overall agent statistics using aggregation pipeline"""
        agents_collection = self.db.agents
        
        # Aggregation pipeline for statistics
        pipeline = [
            {"$match": {"status": "active"}},
            {
                "$group": {
                    "_id": None,
                    "total_agents": {"$sum": 1},
                    "avg_trust_score": {"$avg": "$enhanced_metadata.trust_score"},
                    "avg_reliability": {"$avg": "$enhanced_metadata.reliability_rating"},
                    "total_interactions": {"$sum": "$metrics.total_interactions"},
                    "domains": {"$addToSet": "$domain"},
                    "subdomains": {"$addToSet": "$subdomain"}
                }
            }
        ]
        
        stats_cursor = agents_collection.aggregate(pipeline)
        stats = await stats_cursor.to_list(length=1)
        
        if stats:
            stats = stats[0]
            del stats["_id"]
            stats["total_domains"] = len(stats["domains"])
            stats["total_subdomains"] = len(stats["subdomains"])
            del stats["domains"]
            del stats["subdomains"]
        else:
            stats = {
                "total_agents": 0,
                "avg_trust_score": 0,
                "avg_reliability": 0,
                "total_interactions": 0,
                "total_domains": 0,
                "total_subdomains": 0
            }
            
        # Get domain breakdown
        domain_pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": "$domain", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        
        domain_cursor = agents_collection.aggregate(domain_pipeline)
        domains = await domain_cursor.to_list(length=None)
        
        stats["domains"] = {d["_id"]: d["count"] for d in domains if d["_id"]}
        
        return stats
        
    async def find_similar_agents(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find agents similar to the given agent"""
        agent = await self.get_agent(agent_id)
        if not agent:
            return []
            
        agents_collection = self.db.agents
        
        # Find agents in same domain/subdomain
        similar_agents = await agents_collection.find({
            "agent_id": {"$ne": agent_id},
            "status": "active",
            "$or": [
                {"domain": agent["domain"]},
                {"subdomain": agent.get("subdomain")},
                {"capabilities.primary_expertise": {"$in": agent.get("capabilities", {}).get("primary_expertise", [])}}
            ]
        }).sort("enhanced_metadata.trust_score", -1).limit(limit).to_list(length=limit)
        
        for a in similar_agents:
            a["_id"] = str(a["_id"])
            
        return similar_agents
        
    async def bulk_import_agents(self, json_file: str):
        """Import agents from JSON file"""
        with open(json_file, "r") as f:
            agents = json.load(f)
            
        logger.info(f"Importing {len(agents)} agents to MongoDB...")
        
        agents_collection = self.db.agents
        
        # Prepare documents
        for agent in agents:
            agent["created_at"] = datetime.utcnow()
            agent["updated_at"] = datetime.utcnow()
            agent.setdefault("status", "active")
            agent.setdefault("version", "1.0.0")
            
            # Add metrics subdocument
            agent["metrics"] = {
                "total_interactions": 0,
                "success_count": 0,
                "error_count": 0,
                "avg_response_time": 0,
                "last_active": datetime.utcnow()
            }
            
        # Bulk insert
        try:
            result = await agents_collection.insert_many(agents, ordered=False)
            logger.info(f"Successfully imported {len(result.inserted_ids)} agents")
        except Exception as e:
            logger.error(f"Error during bulk import: {e}")
            
            
async def main():
    """Test MongoDB operations"""
    db = AgentDatabaseMongo()
    await db.connect()
    
    try:
        # Test creating an agent
        test_agent = {
            "id": "mongo_test_001",
            "agent_id": "mongo_test_001",
            "name": "MongoDB Test Agent",
            "domain": "test",
            "subdomain": "mongodb",
            "instructions": "This is a MongoDB test agent",
            "enhanced_metadata": {
                "display_name": "MongoDB Test Agent",
                "avatar": "🍃",
                "trust_score": 0.99
            },
            "capabilities": {
                "primary_expertise": ["NoSQL", "MongoDB", "Testing"],
                "tools_mastery": {"mongodb": "expert"}
            },
            "tools": ["query_tool", "aggregate_tool"]
        }
        
        agent_id = await db.create_agent(test_agent)
        print(f"Created agent: {agent_id}")
        
        # Test retrieving
        agent = await db.get_agent("mongo_test_001")
        print(f"Retrieved agent: {agent['name']}")
        
        # Test search
        agents = await db.search_agents(domain="test")
        print(f"Found {len(agents)} test agents")
        
        # Test text search
        agents = await db.search_agents(query="MongoDB")
        print(f"Found {len(agents)} agents matching 'MongoDB'")
        
        # Update metrics
        await db.update_agent_metrics("mongo_test_001", True, 1.23)
        
        # Find similar agents
        similar = await db.find_similar_agents("mongo_test_001")
        print(f"Found {len(similar)} similar agents")
        
        # Get stats
        stats = await db.get_agent_stats()
        print(f"Database stats: {stats}")
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
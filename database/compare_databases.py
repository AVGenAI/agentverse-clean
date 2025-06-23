#!/usr/bin/env python3
"""
Compare PostgreSQL vs MongoDB for AgentVerse
Shows performance and features of both databases
"""
import asyncio
import time
from agent_db import AgentDatabase
from agent_db_mongo import AgentDatabaseMongo
import json


async def compare_databases():
    """Compare both database systems"""
    print("🔄 AgentVerse Database Comparison: PostgreSQL vs MongoDB")
    print("="*60)
    
    # Initialize both databases
    pg_db = AgentDatabase()
    mongo_db = AgentDatabaseMongo()
    
    await pg_db.connect()
    await mongo_db.connect()
    
    try:
        # Test data
        test_agents = [
            {
                "id": f"perf_test_{i}",
                "agent_id": f"perf_test_{i}",
                "name": f"Performance Test Agent {i}",
                "domain": ["engineering", "data", "security", "devops"][i % 4],
                "subdomain": ["backend", "analytics", "monitoring", "cloud"][i % 4],
                "instructions": f"Test agent {i} for performance comparison",
                "enhanced_metadata": {
                    "display_name": f"Test Agent {i}",
                    "trust_score": 0.80 + (i % 20) / 100,
                    "canonical_name": f"agentverse.test.agent_{i}"
                },
                "capabilities": {
                    "primary_expertise": ["Testing", "Performance"],
                },
                "tools": ["test_tool_1", "test_tool_2"]
            }
            for i in range(100)
        ]
        
        print("\n📊 1. INSERT PERFORMANCE (100 agents)")
        print("-"*40)
        
        # PostgreSQL inserts
        pg_start = time.time()
        for agent in test_agents:
            await pg_db.create_agent(agent.copy())
        pg_insert_time = time.time() - pg_start
        print(f"PostgreSQL: {pg_insert_time:.2f} seconds ({100/pg_insert_time:.0f} agents/sec)")
        
        # MongoDB inserts
        mongo_start = time.time()
        for agent in test_agents:
            await mongo_db.create_agent(agent.copy())
        mongo_insert_time = time.time() - mongo_start
        print(f"MongoDB: {mongo_insert_time:.2f} seconds ({100/mongo_insert_time:.0f} agents/sec)")
        
        print("\n📊 2. QUERY PERFORMANCE")
        print("-"*40)
        
        # Test 1: Get single agent
        pg_start = time.time()
        await pg_db.get_agent("perf_test_50")
        pg_single = time.time() - pg_start
        
        mongo_start = time.time()
        await mongo_db.get_agent("perf_test_50")
        mongo_single = time.time() - mongo_start
        
        print(f"Single agent lookup:")
        print(f"  PostgreSQL: {pg_single*1000:.2f} ms")
        print(f"  MongoDB: {mongo_single*1000:.2f} ms")
        
        # Test 2: Search by domain
        pg_start = time.time()
        pg_results = await pg_db.search_agents(domain="engineering")
        pg_domain = time.time() - pg_start
        
        mongo_start = time.time()
        mongo_results = await mongo_db.search_agents(domain="engineering")
        mongo_domain = time.time() - mongo_start
        
        print(f"\nDomain search (found {len(pg_results)} agents):")
        print(f"  PostgreSQL: {pg_domain*1000:.2f} ms")
        print(f"  MongoDB: {mongo_domain*1000:.2f} ms")
        
        # Test 3: Full text search
        pg_start = time.time()
        pg_results = await pg_db.search_agents(query="performance")
        pg_text = time.time() - pg_start
        
        mongo_start = time.time()
        mongo_results = await mongo_db.search_agents(query="performance")
        mongo_text = time.time() - mongo_start
        
        print(f"\nFull text search:")
        print(f"  PostgreSQL: {pg_text*1000:.2f} ms")
        print(f"  MongoDB: {mongo_text*1000:.2f} ms")
        
        print("\n📊 3. FEATURES COMPARISON")
        print("-"*40)
        print("PostgreSQL:")
        print("  ✅ ACID compliance")
        print("  ✅ Strong consistency")
        print("  ✅ Complex joins")
        print("  ✅ Mature ecosystem")
        print("  ✅ Foreign key constraints")
        print("  ⚠️  Fixed schema")
        
        print("\nMongoDB:")
        print("  ✅ Flexible schema")
        print("  ✅ Horizontal scaling")
        print("  ✅ Document-based (JSON-like)")
        print("  ✅ Fast writes")
        print("  ✅ Built-in sharding")
        print("  ⚠️  Eventual consistency")
        
        print("\n📊 4. STORAGE COMPARISON")
        print("-"*40)
        
        # Get stats
        pg_stats = await pg_db.get_agent_stats()
        mongo_stats = await mongo_db.get_agent_stats()
        
        print(f"PostgreSQL stats: {pg_stats['total_agents']} agents")
        print(f"MongoDB stats: {mongo_stats['total_agents']} agents")
        
        print("\n🎯 RECOMMENDATIONS")
        print("-"*40)
        print("Use PostgreSQL when:")
        print("  • Need ACID transactions")
        print("  • Complex relationships between agents")
        print("  • Strong consistency requirements")
        print("  • Team familiar with SQL")
        
        print("\nUse MongoDB when:")
        print("  • Need flexible agent schemas")
        print("  • Rapid prototyping")
        print("  • Geographic distribution")
        print("  • Expecting 10M+ agents")
        
        print("\n💡 HYBRID APPROACH:")
        print("  • PostgreSQL for core agent registry")
        print("  • MongoDB for agent logs/metrics")
        print("  • Redis for real-time agent state")
        
    finally:
        await pg_db.disconnect()
        await mongo_db.disconnect()


if __name__ == "__main__":
    asyncio.run(compare_databases())
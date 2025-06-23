#!/usr/bin/env python3
"""
Setup databases and load agents
Handles 10K, 100K, and 1M agents
"""
import asyncio
import json
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_manager import db_manager, initialize_databases, close_databases
from bulk_agent_generator import generate_bulk_agents, save_agents

async def load_agents_to_db(agent_count: int):
    """Generate and load agents to databases"""
    print(f"\n🚀 Loading {agent_count:,} agents to databases...")
    
    # Generate agents
    print(f"📝 Generating {agent_count:,} agents...")
    start_time = time.time()
    agents = generate_bulk_agents(agent_count)
    gen_time = time.time() - start_time
    print(f"✅ Generated in {gen_time:.2f} seconds")
    
    # Save to JSON file
    filename = f"agentverse_agents_{agent_count}.json"
    save_agents(agents, filename)
    
    # Load to databases
    print(f"\n💾 Loading to databases...")
    start_time = time.time()
    
    try:
        # Initialize databases
        await initialize_databases()
        
        # Bulk insert
        inserted = await db_manager.bulk_insert_agents(agents, batch_size=5000)
        
        load_time = time.time() - start_time
        print(f"✅ Loaded {inserted:,} agents in {load_time:.2f} seconds")
        print(f"   Rate: {inserted/load_time:.0f} agents/second")
        
        # Get stats
        stats = await db_manager.get_agent_stats()
        print(f"\n📊 Database Statistics:")
        print(f"   Total agents: {stats['total_agents']:,}")
        print(f"   Domains: {stats['domains']}")
        print(f"   Avg trust score: {stats['avg_trust_score']:.3f}")
        
    finally:
        await close_databases()

async def test_retrieval():
    """Test agent retrieval performance"""
    print("\n🔍 Testing retrieval performance...")
    
    await initialize_databases()
    
    try:
        # Test single agent retrieval
        start = time.time()
        agent = await db_manager.get_agent("engineering_backend_0001")
        single_time = (time.time() - start) * 1000
        
        if agent:
            print(f"✅ Single agent retrieval: {single_time:.2f}ms")
            print(f"   Agent: {agent['enhanced_metadata']['display_name']}")
        
        # Test search
        start = time.time()
        results = await db_manager.search_agents(
            domain="engineering",
            skills=["Python", "Docker"],
            min_trust_score=0.9,
            limit=100
        )
        search_time = (time.time() - start) * 1000
        
        print(f"✅ Search retrieval: {search_time:.2f}ms")
        print(f"   Found: {len(results)} agents")
        
        # Test chat history save
        start = time.time()
        await db_manager.save_chat_message(
            session_id="test_session_001",
            agent_id="engineering_backend_0001",
            message_type="user",
            content="Show me all Python best practices",
            metadata={"test": True},
            tokens_used=50
        )
        chat_time = (time.time() - start) * 1000
        
        print(f"✅ Chat message save: {chat_time:.2f}ms")
        
    finally:
        await close_databases()

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup and load agents to databases")
    parser.add_argument("--count", type=int, default=10000, 
                       help="Number of agents to generate (10000, 100000, 1000000)")
    parser.add_argument("--test", action="store_true", 
                       help="Run retrieval tests")
    
    args = parser.parse_args()
    
    if args.test:
        await test_retrieval()
    else:
        # Validate count
        if args.count not in [10000, 100000, 1000000]:
            print("⚠️  Count must be 10000, 100000, or 1000000")
            return
            
        await load_agents_to_db(args.count)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════╗
║     AgentVerse Database Setup & Load     ║
╚══════════════════════════════════════════╝
    """)
    
    # First, ensure databases are running
    print("📦 Ensure Docker containers are running:")
    print("   cd database && docker-compose up -d")
    print("\n⏳ Waiting for databases to be ready...")
    time.sleep(5)
    
    asyncio.run(main())
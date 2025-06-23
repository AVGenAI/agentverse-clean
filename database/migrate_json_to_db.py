#!/usr/bin/env python3
"""
Migrate JSON agents to PostgreSQL database
One-time migration script
"""
import asyncio
import json
import os
from agent_db import AgentDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def migrate_agents():
    """Migrate all JSON agents to PostgreSQL"""
    db = AgentDatabase()
    await db.connect()
    
    try:
        # Create tables if they don't exist
        logger.info("Creating database tables...")
        await db.create_tables()
        
        # Find all agent JSON files
        config_dir = "src/config"
        json_files = [
            "agentverse_agents_1000.json",
            "agents_config.json",
            "1000_agents.json",
            "essential_agents.json"
        ]
        
        total_imported = 0
        
        for json_file in json_files:
            filepath = os.path.join(config_dir, json_file)
            if os.path.exists(filepath):
                logger.info(f"Importing from {json_file}...")
                await db.bulk_import_agents(filepath)
                
                with open(filepath, "r") as f:
                    agents = json.load(f)
                    total_imported += len(agents)
        
        # Get final stats
        stats = await db.get_agent_stats()
        logger.info(f"\nMigration Complete!")
        logger.info(f"Total agents imported: {total_imported}")
        logger.info(f"Database stats: {stats}")
        
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(migrate_agents())
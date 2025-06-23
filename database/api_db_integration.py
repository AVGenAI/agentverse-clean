"""
API Database Integration
Connects the FastAPI backend to PostgreSQL, Redis, and MongoDB
"""
from typing import Optional, List, Dict, Any
from fastapi import Depends
from db_manager import db_manager
import logging

logger = logging.getLogger(__name__)

class APIDatabase:
    """Database operations for the API"""
    
    @staticmethod
    async def save_chat_interaction(
        session_id: str,
        agent_id: str,
        user_message: str,
        agent_response: str,
        metadata: Optional[Dict[str, Any]] = None,
        tokens_used: Optional[int] = None
    ):
        """Save a complete chat interaction"""
        try:
            # Save user message
            await db_manager.save_chat_message(
                session_id=session_id,
                agent_id=agent_id,
                message_type="user",
                content=user_message,
                metadata=metadata
            )
            
            # Save agent response
            await db_manager.save_chat_message(
                session_id=session_id,
                agent_id=agent_id,
                message_type="agent",
                content=agent_response,
                metadata=metadata,
                tokens_used=tokens_used
            )
            
            logger.info(f"Saved chat interaction for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error saving chat interaction: {e}")
            
    @staticmethod
    async def get_agent_from_db(agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent from database with caching"""
        try:
            return await db_manager.get_agent(agent_id)
        except Exception as e:
            logger.error(f"Error getting agent {agent_id}: {e}")
            return None
            
    @staticmethod
    async def search_agents_db(
        query: Optional[str] = None,
        domain: Optional[str] = None,
        skills: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search agents in database"""
        try:
            return await db_manager.search_agents(
                query=query,
                domain=domain,
                skills=skills,
                limit=limit,
                offset=offset
            )
        except Exception as e:
            logger.error(f"Error searching agents: {e}")
            return []
            
    @staticmethod
    async def get_chat_history_db(
        session_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get chat history from database"""
        try:
            return await db_manager.get_chat_history(
                session_id=session_id,
                agent_id=agent_id,
                limit=limit
            )
        except Exception as e:
            logger.error(f"Error getting chat history: {e}")
            return []

# Update main.py to use database
def update_main_py():
    """Add database integration to main.py"""
    integration_code = '''
# Add to imports
from database.api_db_integration import APIDatabase
from database.db_manager import initialize_databases, close_databases

# Add to startup event
@app.on_event("startup")
async def startup_event():
    """Initialize databases on startup"""
    try:
        await initialize_databases()
        logger.info("✅ Databases initialized")
    except Exception as e:
        logger.error(f"Failed to initialize databases: {e}")

# Add to shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown"""
    await close_databases()

# Update chat endpoint to save history
@app.post("/chat/message")
async def send_message(request: MessageRequest):
    """Send a message in a chat session with history tracking"""
    # ... existing code ...
    
    # After getting response, save to database
    if response:
        await APIDatabase.save_chat_interaction(
            session_id=request.session_id,
            agent_id=session.agent_id,
            user_message=request.message,
            agent_response=response,
            metadata={"tools_used": tools_used} if tools_used else None,
            tokens_used=tokens_used
        )
    
    return {"message": response}

# Add chat history endpoint
@app.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 100):
    """Get chat history for a session"""
    history = await APIDatabase.get_chat_history_db(
        session_id=session_id,
        limit=limit
    )
    return {"session_id": session_id, "messages": history}

# Update agents endpoint to use database
@app.post("/agents")
async def get_agents(query: AgentQuery):
    """Get agents with database support"""
    # First try database
    if db_manager.postgres_pool:
        agents = await APIDatabase.search_agents_db(
            query=query.query,
            domain=query.domain,
            skills=[query.skill] if query.skill else None,
            limit=query.limit,
            offset=query.offset
        )
        if agents:
            return {"agents": agents, "total": len(agents), "source": "database"}
    
    # Fallback to file-based
    # ... existing code ...
'''
    
    return integration_code

# Add migration script
async def migrate_existing_agents():
    """Migrate existing agents from JSON to database"""
    import json
    
    # Load existing agents
    with open("src/config/agentverse_agents_1000.json", "r") as f:
        agents = json.load(f)
        
    print(f"Migrating {len(agents)} agents to database...")
    
    # Initialize databases
    await initialize_databases()
    
    try:
        # Insert agents
        inserted = await db_manager.bulk_insert_agents(agents, batch_size=100)
        print(f"✅ Migrated {inserted} agents")
        
    finally:
        await close_databases()

if __name__ == "__main__":
    # Run migration
    import asyncio
    asyncio.run(migrate_existing_agents())
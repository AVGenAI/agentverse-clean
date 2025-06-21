#!/usr/bin/env python3
"""Direct test of agent manager to verify tools are being created"""
import asyncio
import sys
import os

# Change to agentverse_api directory
os.chdir('./agentverse_api')
sys.path.insert(0, '.')

from agent_manager import agent_manager

async def test_agent_tools():
    print("Testing Agent Tools Creation")
    print("=" * 60)
    
    # Test the SRE agent
    agent_id = "sre_servicenow_001"
    
    # Get or create the agent
    print(f"\n1. Creating agent: {agent_id}")
    agent = agent_manager.get_or_create_agent(agent_id)
    
    if agent:
        print(f"✅ Agent created: {agent.name}")
        print(f"   Instructions: {agent.instructions[:100]}...")
        print(f"   Number of tools: {len(agent.tools)}")
        
        if agent.tools:
            print("\n   Available tools:")
            for tool in agent.tools:
                print(f"   - {tool.name}: {tool.description}")
        else:
            print("   ❌ No tools configured!")
    else:
        print("❌ Failed to create agent")
    
    # Test a chat message
    print("\n2. Testing chat with agent...")
    response = await agent_manager.chat_with_agent(agent_id, "Show me all critical incidents")
    print(f"Response: {response[:200]}...")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent_tools())
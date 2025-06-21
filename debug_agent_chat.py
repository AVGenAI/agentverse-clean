#!/usr/bin/env python3
"""
Debug why agent chat is returning demo responses
"""
import sys
sys.path.insert(0, 'agentverse_api')

from agent_manager import agent_manager
import asyncio

async def test_chat():
    print("🔍 Debugging Agent Chat")
    print("="*50)
    
    # Check agent manager state
    print(f"\n1. Agent Manager Configuration:")
    print(f"   API Key present: {bool(agent_manager.api_key)}")
    print(f"   API Key: {agent_manager.api_key[:20] if agent_manager.api_key else 'None'}...")
    print(f"   Use Ollama: {agent_manager.use_ollama}")
    print(f"   Ollama Available: {agent_manager.ollama_available}")
    print(f"   Agents loaded: {len(agent_manager.agent_configs)}")
    
    # Test with SRE agent
    agent_id = "sre_servicenow_001"
    message = "Hello, can you help me?"
    
    print(f"\n2. Testing chat with agent {agent_id}")
    print(f"   Message: {message}")
    
    # Call the chat method
    response = await agent_manager.chat_with_agent(agent_id, message)
    
    print(f"\n3. Response:")
    print(response)
    
    # Check if it's a demo response
    if "[Note: This is a demo response" in response:
        print("\n❌ Got demo response - OpenAI is not being used")
        print("\nPossible reasons:")
        print("1. API key might be invalid")
        print("2. Agent creation might be failing")
        print("3. OpenAI call might be erroring")
    else:
        print("\n✅ Got real response - OpenAI is working!")

if __name__ == "__main__":
    asyncio.run(test_chat())
#!/usr/bin/env python3
"""
AgentVerse Chat - Chat with any AgentVerse agent
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key
import json
import argparse

load_dotenv()

def chat_with_agentverse_agent(agentverse_id: str):
    """Chat with an AgentVerse agent"""
    # Load AgentVerse agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    # Find agent by AgentVerse ID
    agent_data = None
    for agent in agents:
        if agent.get("enhanced_metadata", {}).get("canonical_name") == agentverse_id:
            agent_data = agent
            break
    
    if not agent_data:
        print(f"❌ Agent '{agentverse_id}' not found in AgentVerse")
        return
    
    # Set up OpenAI
    if os.getenv("OPENAI_API_KEY"):
        set_default_openai_key(os.getenv("OPENAI_API_KEY"))
    else:
        print("❌ No OpenAI API key found")
        return
    
    # Create agent
    metadata = agent_data["enhanced_metadata"]
    agent = Agent(
        name=metadata["display_name"],
        instructions=agent_data["instructions"],
        model="gpt-4o-mini"
    )
    
    print(f"\n🌌 Welcome to AgentVerse Chat")
    print(f"💬 Chatting with: {metadata['avatar_emoji']} {metadata['display_name']}")
    print(f"🆔 AgentVerse ID: {metadata['canonical_name']}")
    print(f"🎯 Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
    print("\nType 'exit' to quit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'exit':
                print("\n👋 Leaving AgentVerse. See you soon!")
                break
            
            result = Runner.run_sync(agent, user_input)
            print(f"\n{metadata['display_name']}: {result.final_output}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Leaving AgentVerse. See you soon!")
            break

def main():
    parser = argparse.ArgumentParser(description="Chat with AgentVerse agents")
    parser.add_argument("--agent", "-a", required=True, help="AgentVerse agent ID (e.g., agentverse.engineering.frontend.react)")
    
    args = parser.parse_args()
    chat_with_agentverse_agent(args.agent)

if __name__ == "__main__":
    main()

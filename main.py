#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
from agents import Runner, set_default_openai_key
from src.core.agent_factory import AgentFactory, AgentConfig
from src.providers import ProviderConfig
import argparse
import json


def setup_providers(factory: AgentFactory):
    """Setup all available providers"""
    load_dotenv()
    
    # Set OpenAI API key globally for the agents library
    if os.getenv("OPENAI_API_KEY"):
        set_default_openai_key(os.getenv("OPENAI_API_KEY"))
        print("✓ OpenAI API key configured")
        
        # Still register provider for our factory pattern
        openai_config = ProviderConfig(
            name="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o-mini"
        )
        factory.register_provider("openai", openai_config)
    
    # Ollama Provider (for local LLMs)
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        import requests
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        if response.status_code == 200:
            ollama_config = ProviderConfig(
                name="ollama",
                base_url=f"{ollama_url}/v1",
                model="llama2"  # Default model
            )
            factory.register_provider("ollama", ollama_config)
            print("✓ Ollama provider registered")
    except:
        print("✗ Ollama not available")


def interactive_mode(factory: AgentFactory, agent_name: str):
    """Run interactive chat with an agent"""
    agent = factory.get_agent(agent_name)
    if not agent:
        print(f"Agent '{agent_name}' not found!")
        return
    
    print(f"\nChatting with {agent_name}")
    print("Type 'exit' to quit, 'switch <agent>' to change agents")
    print("-" * 50)
    
    conversation = []
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'exit':
                break
            
            if user_input.lower().startswith('switch '):
                new_agent = user_input[7:].strip()
                if factory.get_agent(new_agent):
                    agent_name = new_agent
                    agent = factory.get_agent(agent_name)
                    print(f"\nSwitched to {agent_name}")
                    conversation = []  # Reset conversation
                else:
                    print(f"Agent '{new_agent}' not found!")
                continue
            
            # Run the agent
            result = Runner.run_sync(agent, user_input, context=conversation)
            response = result.final_output
            
            print(f"\n{agent_name}: {response}")
            
            # Update conversation history
            conversation.append({"role": "user", "content": user_input})
            conversation.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="AI Agent System")
    parser.add_argument("--agent", "-a", help="Agent name to use", default="GeneralAssistant")
    parser.add_argument("--list", "-l", action="store_true", help="List available agents")
    parser.add_argument("--config", "-c", help="Path to agents config file", 
                        default="src/config/agents_config.json")
    parser.add_argument("--query", "-q", help="Single query to run (non-interactive)")
    
    args = parser.parse_args()
    
    # Initialize factory
    factory = AgentFactory()
    setup_providers(factory)
    
    # Load agents from config
    if os.path.exists(args.config):
        agents = factory.load_agents_from_file(args.config)
        print(f"\n✓ Loaded {len(agents)} agents from config")
    else:
        print(f"\n✗ Config file not found: {args.config}")
        # Create a default agent
        default_config = AgentConfig(
            name="GeneralAssistant",
            instructions="You are a helpful AI assistant.",
            provider="openai"
        )
        factory.create_agent(default_config)
    
    # List agents
    if args.list:
        print("\nAvailable Agents:")
        for name in factory.list_agents():
            agent = factory.get_agent(name)
            print(f"  - {name}")
        return
    
    # Single query mode
    if args.query:
        agent = factory.get_agent(args.agent)
        if not agent:
            print(f"Agent '{args.agent}' not found!")
            return
        
        result = Runner.run_sync(agent, args.query)
        print(result.final_output)
        return
    
    # Interactive mode
    interactive_mode(factory, args.agent)


if __name__ == "__main__":
    main()
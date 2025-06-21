#!/usr/bin/env python3
"""
Simple main script using the corrected agent API
"""
import os
import argparse
from dotenv import load_dotenv
from agents import Runner, run_demo_loop
from src.core.simple_factory import (
    SimpleAgentFactory, 
    SimpleAgentConfig,
    create_calculator_tool,
    create_file_reader_tool
)

def create_default_agents(factory: SimpleAgentFactory):
    """Create some default agents"""
    
    # General Assistant
    general = SimpleAgentConfig(
        name="GeneralAssistant",
        instructions="You are a helpful general-purpose AI assistant.",
        model="gpt-4o-mini"
    )
    factory.create_agent(general)
    
    # Code Assistant with calculator
    calc_tool = create_calculator_tool()
    code = SimpleAgentConfig(
        name="CodeAssistant",
        instructions="""You are an expert programming assistant. 
        You can help with code reviews, debugging, and writing code.
        Use the calculator tool for any mathematical computations.""",
        model="gpt-4o-mini",
        tools=[calc_tool]
    )
    factory.create_agent(code)
    
    # Multi-language Support System
    spanish = SimpleAgentConfig(
        name="SpanishAssistant",
        instructions="You only speak Spanish. Always respond in Spanish.",
        model="gpt-4o-mini"
    )
    factory.create_agent(spanish)
    
    english = SimpleAgentConfig(
        name="EnglishAssistant", 
        instructions="You only speak English. Always respond in English.",
        model="gpt-4o-mini"
    )
    factory.create_agent(english)
    
    triage = SimpleAgentConfig(
        name="LanguageTriage",
        instructions="""You are a language detection agent. 
        Detect the language of the user's message and handoff to the appropriate agent:
        - For Spanish messages, handoff to SpanishAssistant
        - For English messages, handoff to EnglishAssistant""",
        model="gpt-4o-mini",
        handoffs=["SpanishAssistant", "EnglishAssistant"]
    )
    factory.create_agent(triage)


def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="AI Agent System")
    parser.add_argument("--agent", "-a", help="Agent name to use", default="GeneralAssistant")
    parser.add_argument("--list", "-l", action="store_true", help="List available agents")
    parser.add_argument("--query", "-q", help="Single query to run")
    parser.add_argument("--demo", "-d", action="store_true", help="Run interactive demo mode")
    
    args = parser.parse_args()
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ No OPENAI_API_KEY found in environment")
        print("Please create a .env file with your OpenAI API key")
        return
    
    # Create factory and agents
    factory = SimpleAgentFactory()
    create_default_agents(factory)
    print("✓ Agents initialized")
    
    # List agents
    if args.list:
        print("\nAvailable Agents:")
        for name in factory.list_agents():
            agent = factory.get_agent(name)
            print(f"  - {name}")
            config = factory.export_config(name)
            if config.get('tools'):
                print(f"    Tools: {len(config['tools'])} available")
            if config.get('handoffs'):
                print(f"    Handoffs: {', '.join(config['handoffs'])}")
        return
    
    # Get the requested agent
    agent = factory.get_agent(args.agent)
    if not agent:
        print(f"❌ Agent '{args.agent}' not found!")
        print(f"Available agents: {', '.join(factory.list_agents())}")
        return
    
    # Single query mode
    if args.query:
        print(f"\nUsing agent: {args.agent}")
        result = Runner.run_sync(agent, args.query)
        print(f"\n{result.final_output}")
        return
    
    # Demo mode (streaming)
    if args.demo:
        print(f"\nStarting demo mode with {args.agent}")
        print("Type 'exit' to quit")
        print("-" * 50)
        import asyncio
        asyncio.run(run_demo_loop(agent, stream=True))
        return
    
    # Interactive mode
    print(f"\nChatting with {args.agent}")
    print("Type 'exit' to quit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'exit':
                break
            
            result = Runner.run_sync(agent, user_input)
            print(f"\n{args.agent}: {result.final_output}")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
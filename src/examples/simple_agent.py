import os
from dotenv import load_dotenv
from agents import Runner
from ..core.agent_factory import AgentFactory, AgentConfig
from ..providers import ProviderConfig


def create_simple_agent():
    load_dotenv()
    
    # Initialize factory
    factory = AgentFactory()
    
    # Register OpenAI provider
    openai_config = ProviderConfig(
        name="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0.7
    )
    factory.register_provider("openai", openai_config)
    
    # Create agent
    agent_config = AgentConfig(
        name="Assistant",
        instructions="""You are a helpful AI assistant. You can:
        - Answer questions
        - Help with coding tasks
        - Provide explanations
        - Assist with various tasks
        
        Be concise, accurate, and helpful.""",
        provider="openai",
        model="gpt-4o-mini"
    )
    
    return factory.create_agent(agent_config)


def main():
    agent = create_simple_agent()
    
    # Run a simple conversation
    print("Simple Agent Example")
    print("-" * 40)
    
    queries = [
        "Hello! What can you help me with?",
        "Can you write a Python function to calculate fibonacci numbers?",
        "Explain how recursion works in simple terms"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        result = Runner.run_sync(agent, query)
        print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    main()
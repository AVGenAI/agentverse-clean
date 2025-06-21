import os
from dotenv import load_dotenv
from agents import Runner, Tool
from typing import Dict, Any
import json
import requests
import math
from ..core.agent_factory import AgentFactory, AgentConfig
from ..providers import ProviderConfig


def calculate(expression: str) -> float:
    """Evaluate a mathematical expression"""
    try:
        # Safe evaluation of mathematical expressions
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        return eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        return f"Error: {str(e)}"


def web_search(query: str) -> str:
    """Search the web for information (mock implementation)"""
    # In a real implementation, this would use a search API
    return f"Mock search results for: {query}"


def read_file(filepath: str) -> str:
    """Read contents of a file"""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def create_tool_agent():
    load_dotenv()
    
    # Initialize factory
    factory = AgentFactory()
    
    # Register provider
    openai_config = ProviderConfig(
        name="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        model="gpt-4o-mini",
        temperature=0.7
    )
    factory.register_provider("openai", openai_config)
    
    # Define tools
    calc_tool = Tool(
        name="calculate",
        description="Evaluate mathematical expressions",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate"
                }
            },
            "required": ["expression"]
        },
        function=calculate
    )
    
    search_tool = Tool(
        name="web_search",
        description="Search the web for information",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                }
            },
            "required": ["query"]
        },
        function=web_search
    )
    
    file_tool = Tool(
        name="read_file",
        description="Read contents of a file",
        parameters={
            "type": "object",
            "properties": {
                "filepath": {
                    "type": "string",
                    "description": "Path to the file to read"
                }
            },
            "required": ["filepath"]
        },
        function=read_file
    )
    
    # Create agent with tools
    agent_config = AgentConfig(
        name="ToolAgent",
        instructions="""You are an AI assistant with access to several tools:
        - calculate: For mathematical calculations
        - web_search: To search for information online
        - read_file: To read file contents
        
        Use these tools when appropriate to help answer user questions.""",
        provider="openai",
        model="gpt-4o-mini",
        tools=[calc_tool, search_tool, file_tool]
    )
    
    return factory.create_agent(agent_config)


def main():
    import math  # Import for calculator tool
    
    agent = create_tool_agent()
    
    print("Agent with Tools Example")
    print("-" * 40)
    
    queries = [
        "What is 234 * 567 + 89?",
        "Search for information about the Python openai-agents library",
        "Calculate the square root of 144"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        result = Runner.run_sync(agent, query)
        print(f"Agent: {result.final_output}")


if __name__ == "__main__":
    main()
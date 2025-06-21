#!/usr/bin/env python3
"""
Test script with tools following the openai-agents library pattern
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_default_openai_key
import math

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    set_default_openai_key(api_key)
else:
    print("❌ No OpenAI API key found")
    exit(1)

# Define tools using the @function_tool decorator
@function_tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression"""
    try:
        # Safe evaluation with math functions
        allowed_names = {
            k: v for k, v in math.__dict__.items() if not k.startswith("__")
        }
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"

@function_tool
def get_weather(city: str) -> str:
    """Get the weather for a city (mock implementation)"""
    # In a real implementation, this would call a weather API
    weather_data = {
        "Tokyo": "sunny, 22°C",
        "London": "cloudy, 15°C", 
        "New York": "rainy, 18°C",
        "Paris": "partly cloudy, 20°C"
    }
    return f"The weather in {city} is {weather_data.get(city, 'unknown')}"

# Create agent with tools
agent = Agent(
    name="ToolAssistant",
    instructions="""You are a helpful assistant with access to tools.
    You can calculate mathematical expressions and check the weather.
    Always use the tools when appropriate.""",
    tools=[calculate, get_weather],
)

# Test the agent
print("Testing agent with tools...\n")

queries = [
    "What is 15 * 23 + 45?",
    "What's the weather in Tokyo?",
    "Calculate the square root of 144",
    "What's the weather in London and what is 100 / 4?"
]

for query in queries:
    print(f"Query: {query}")
    result = Runner.run_sync(agent, query)
    print(f"Response: {result.final_output}\n")
    print("-" * 40)
#!/usr/bin/env python3
"""
Simple test script that mimics the openai-agents library examples
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key

# Load environment variables
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    set_default_openai_key(api_key)
    print("✓ OpenAI API key configured")
else:
    print("❌ No OpenAI API key found in .env file")
    exit(1)

# Create a simple agent (mimicking their example)
agent = Agent(
    name="Assistant", 
    instructions="You are a helpful assistant"
)

# Test with a simple query
print("\nTesting basic agent...")
result = Runner.run_sync(agent, "Write a haiku about Python programming")
print(f"Response: {result.final_output}")

# Test with multiple agents and handoffs
print("\n" + "="*50 + "\n")
print("Testing multi-agent system...")

spanish_agent = Agent(
    name="Spanish agent",
    instructions="You only speak Spanish.",
)

english_agent = Agent(
    name="English agent",
    instructions="You only speak English",
)

triage_agent = Agent(
    name="Triage agent",
    instructions="Handoff to the appropriate agent based on the language of the request.",
    handoffs=[spanish_agent, english_agent],
)

# Test English request
result = Runner.run_sync(triage_agent, "Hello, how are you?")
print(f"English test: {result.final_output}")

# Test Spanish request  
result = Runner.run_sync(triage_agent, "Hola, ¿cómo estás?")
print(f"Spanish test: {result.final_output}")
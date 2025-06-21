#!/usr/bin/env python3
"""
Example of creating custom agents with various capabilities
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_default_openai_key
import json
import datetime

load_dotenv()

# Set API key
if os.getenv("OPENAI_API_KEY"):
    set_default_openai_key(os.getenv("OPENAI_API_KEY"))
else:
    print("No API key found")
    exit(1)

# Define custom tools
@function_tool
def get_current_time() -> str:
    """Get the current date and time"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@function_tool
def word_count(text: str) -> str:
    """Count words in a text"""
    words = text.split()
    return f"The text contains {len(words)} words"

@function_tool
def save_to_file(filename: str, content: str) -> str:
    """Save content to a file"""
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return f"Successfully saved to {filename}"
    except Exception as e:
        return f"Error saving file: {str(e)}"

@function_tool
def search_web(query: str) -> str:
    """Search the web (mock implementation)"""
    # In real implementation, this would use a search API
    mock_results = {
        "python": "Python is a high-level programming language...",
        "ai": "Artificial Intelligence is the simulation of human intelligence...",
        "openai": "OpenAI is an AI research company..."
    }
    
    for key, value in mock_results.items():
        if key in query.lower():
            return value
    
    return "No results found for your query"

# Create specialized agents
research_agent = Agent(
    name="ResearchAgent",
    instructions="""You are a research specialist. Your job is to:
    - Search for information using the search_web tool
    - Analyze and summarize findings
    - Provide citations when possible
    Always use the search tool to find information.""",
    tools=[search_web, get_current_time]
)

writer_agent = Agent(
    name="WriterAgent",
    instructions="""You are a professional writer. Your job is to:
    - Create well-structured content
    - Count words to ensure appropriate length
    - Save important content to files
    Use your tools to enhance your writing process.""",
    tools=[word_count, save_to_file, get_current_time]
)

analyst_agent = Agent(
    name="DataAnalyst",
    instructions="""You are a data analyst. You can:
    - Analyze text and provide insights
    - Count words and analyze content structure
    - Save analysis results
    Always provide data-driven insights.""",
    tools=[word_count, save_to_file]
)

# Create a coordinator agent that can delegate
coordinator_agent = Agent(
    name="Coordinator",
    instructions="""You are a project coordinator. Based on the user's request:
    - For research tasks, handoff to ResearchAgent
    - For writing tasks, handoff to WriterAgent  
    - For analysis tasks, handoff to DataAnalyst
    Make smart decisions about which agent is best suited for each task.""",
    handoffs=[research_agent, writer_agent, analyst_agent]
)

def demo_agents():
    """Run demonstrations of different agents"""
    
    print("=== Custom Agents Demo ===\n")
    
    # Test Research Agent
    print("1. Testing Research Agent")
    print("-" * 40)
    result = Runner.run_sync(research_agent, "Search for information about Python programming")
    print(f"Result: {result.final_output}\n")
    
    # Test Writer Agent
    print("2. Testing Writer Agent")
    print("-" * 40)
    result = Runner.run_sync(writer_agent, "Write a short paragraph about AI and tell me how many words it has")
    print(f"Result: {result.final_output}\n")
    
    # Test Coordinator with handoffs
    print("3. Testing Coordinator Agent")
    print("-" * 40)
    result = Runner.run_sync(coordinator_agent, "I need to research about OpenAI")
    print(f"Result: {result.final_output}\n")
    
    # Test saving functionality
    print("4. Testing File Save")
    print("-" * 40)
    result = Runner.run_sync(writer_agent, "Write a haiku about coding and save it to haiku.txt")
    print(f"Result: {result.final_output}\n")

def interactive_demo():
    """Run interactive session with coordinator"""
    print("\n=== Interactive Mode with Coordinator ===")
    print("You can ask for research, writing, or analysis tasks")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == 'exit':
            break
            
        result = Runner.run_sync(coordinator_agent, user_input)
        print(f"\nCoordinator: {result.final_output}\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_demo()
    else:
        demo_agents()
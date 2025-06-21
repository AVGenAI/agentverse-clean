#!/usr/bin/env python3
"""
Load and interact with 1000 agents
"""
import os
import json
import argparse
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key
from typing import List, Dict, Any
import random

load_dotenv()

class AgentManager:
    def __init__(self):
        self.agents_data = {}
        self.agents = {}
        
        # Set API key
        if os.getenv("OPENAI_API_KEY"):
            set_default_openai_key(os.getenv("OPENAI_API_KEY"))
        
    def load_all_agents(self):
        """Load all 1000 agents from configuration"""
        config_file = "src/config/1000_agents.json"
        with open(config_file, 'r') as f:
            self.agents_data = json.load(f)
        print(f"Loaded {len(self.agents_data)} agent configurations")
        
    def create_agent(self, agent_data: Dict[str, Any]) -> Agent:
        """Create an agent from configuration"""
        return Agent(
            name=agent_data['name'],
            instructions=agent_data['instructions'],
            model=agent_data.get('model', 'gpt-4o-mini')
        )
    
    def get_agent_by_name(self, name: str) -> Agent:
        """Get or create agent by name"""
        if name not in self.agents:
            # Find agent data
            agent_data = next((a for a in self.agents_data if a['name'] == name), None)
            if agent_data:
                self.agents[name] = self.create_agent(agent_data)
            else:
                return None
        return self.agents.get(name)
    
    def list_categories(self) -> List[str]:
        """List all categories"""
        categories = set()
        for agent in self.agents_data:
            categories.add(agent['category'])
        return sorted(list(categories))
    
    def list_agents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """List agents in a category"""
        return [a for a in self.agents_data if a['category'] == category]
    
    def search_agents(self, query: str) -> List[Dict[str, Any]]:
        """Search agents by name, skills, or instructions"""
        query_lower = query.lower()
        results = []
        
        for agent in self.agents_data:
            if (query_lower in agent['name'].lower() or
                query_lower in agent['instructions'].lower() or
                any(query_lower in skill.lower() for skill in agent.get('skills', []))):
                results.append(agent)
        
        return results
    
    def get_random_agent(self, category: str = None) -> Dict[str, Any]:
        """Get a random agent, optionally from a specific category"""
        if category:
            agents = self.list_agents_by_category(category)
        else:
            agents = self.agents_data
        
        return random.choice(agents) if agents else None


def main():
    parser = argparse.ArgumentParser(description="Interact with 1000 agents")
    parser.add_argument("--list-categories", action="store_true", help="List all categories")
    parser.add_argument("--category", "-c", help="Filter by category")
    parser.add_argument("--search", "-s", help="Search agents")
    parser.add_argument("--agent", "-a", help="Use specific agent")
    parser.add_argument("--random", "-r", action="store_true", help="Use random agent")
    parser.add_argument("--query", "-q", help="Query to send to agent")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = AgentManager()
    manager.load_all_agents()
    
    # Show stats
    if args.stats:
        print("\n=== Agent Statistics ===")
        categories = manager.list_categories()
        for category in categories:
            agents = manager.list_agents_by_category(category)
            print(f"{category}: {len(agents)} agents")
        print(f"\nTotal: {len(manager.agents_data)} agents")
        return
    
    # List categories
    if args.list_categories:
        print("\n=== Categories ===")
        for category in manager.list_categories():
            print(f"- {category}")
        return
    
    # List agents in category
    if args.category and not args.query and not args.agent:
        agents = manager.list_agents_by_category(args.category)
        print(f"\n=== {args.category} Agents ({len(agents)}) ===")
        for agent in agents[:20]:  # Show first 20
            print(f"- {agent['name']} ({agent.get('subcategory', 'General')})")
        if len(agents) > 20:
            print(f"... and {len(agents) - 20} more")
        return
    
    # Search agents
    if args.search:
        results = manager.search_agents(args.search)
        print(f"\n=== Search Results ({len(results)}) ===")
        for agent in results[:10]:
            print(f"- {agent['name']} ({agent['category']} - {agent.get('subcategory', 'General')})")
            print(f"  Skills: {', '.join(agent.get('skills', []))}")
        if len(results) > 10:
            print(f"... and {len(results) - 10} more")
        return
    
    # Get agent to use
    if args.random:
        agent_data = manager.get_random_agent(args.category)
        if agent_data:
            print(f"\n=== Using Random Agent: {agent_data['name']} ===")
            print(f"Category: {agent_data['category']} - {agent_data.get('subcategory', 'General')}")
            print(f"Skills: {', '.join(agent_data.get('skills', []))}")
    elif args.agent:
        agent_data = next((a for a in manager.agents_data if a['name'] == args.agent), None)
        if not agent_data:
            # Try searching
            results = manager.search_agents(args.agent)
            if results:
                agent_data = results[0]
                print(f"\n=== Using: {agent_data['name']} ===")
            else:
                print(f"Agent '{args.agent}' not found")
                return
    else:
        # Default to first agent
        agent_data = manager.agents_data[0]
    
    # Create and use agent
    if args.query and agent_data:
        agent = manager.create_agent(agent_data)
        print(f"\nQuery: {args.query}")
        print("-" * 50)
        result = Runner.run_sync(agent, args.query)
        print(f"Response: {result.final_output}")
    elif agent_data:
        # Interactive mode
        agent = manager.create_agent(agent_data)
        print(f"\nChatting with {agent_data['name']}")
        print("Type 'exit' to quit, 'switch' to change agent")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'switch':
                    agent_data = manager.get_random_agent(args.category)
                    agent = manager.create_agent(agent_data)
                    print(f"\nSwitched to: {agent_data['name']}")
                    print(f"Category: {agent_data['category']} - {agent_data.get('subcategory', 'General')}")
                    continue
                
                result = Runner.run_sync(agent, user_input)
                print(f"\n{agent_data['name']}: {result.final_output}")
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break


if __name__ == "__main__":
    main()
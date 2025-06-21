#!/usr/bin/env python3
"""
AgentVerse Explorer - Discover and interact with AgentVerse agents
"""
import json
import argparse
from typing import List, Dict, Any

class AgentVerseExplorer:
    def __init__(self):
        # Load AgentVerse agents
        with open("src/config/agentverse_agents_1000.json", 'r') as f:
            self.agents = json.load(f)
        
        print("\n🌌 Welcome to AgentVerse")
        print("   A Universe of {} AI Agents\n".format(len(self.agents)))
    
    def list_domains(self):
        """List all AgentVerse domains"""
        domains = {}
        for agent in self.agents:
            domain = agent.get("enhanced_metadata", {}).get("canonical_name", "").split(".")[1]
            if domain:
                domains[domain] = domains.get(domain, 0) + 1
        
        print("🌐 AgentVerse Domains:")
        print("-" * 40)
        for domain, count in sorted(domains.items()):
            print(f"  agentverse.{domain}.*  →  {count} agents")
    
    def search_agents(self, query: str):
        """Search for agents"""
        results = []
        query_lower = query.lower()
        
        for agent in self.agents:
            metadata = agent.get("enhanced_metadata", {})
            if (query_lower in metadata.get("display_name", "").lower() or
                query_lower in str(metadata.get("capabilities", {})).lower()):
                results.append(agent)
        
        print(f"\n🔍 Found {len(results)} agents matching '{query}':")
        for agent in results[:10]:
            metadata = agent["enhanced_metadata"]
            print(f"\n  {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"     AgentVerse ID: {metadata['canonical_name']}")
            print(f"     Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")

def main():
    parser = argparse.ArgumentParser(description="Explore AgentVerse")
    parser.add_argument("--list-domains", action="store_true", help="List all AgentVerse domains")
    parser.add_argument("--search", "-s", help="Search for agents")
    parser.add_argument("--agent", "-a", help="Get details for specific agent")
    
    args = parser.parse_args()
    explorer = AgentVerseExplorer()
    
    if args.list_domains:
        explorer.list_domains()
    elif args.search:
        explorer.search_agents(args.search)
    else:
        explorer.list_domains()

if __name__ == "__main__":
    main()

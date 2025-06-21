#!/usr/bin/env python3
"""
Display a summary of all 1000 agents
"""
import json
from collections import defaultdict

def display_summary():
    # Load agents
    with open("src/config/1000_agents.json", 'r') as f:
        agents = json.load(f)
    
    # Categorize
    by_category = defaultdict(lambda: defaultdict(list))
    skills_count = defaultdict(int)
    
    for agent in agents:
        category = agent['category']
        subcategory = agent.get('subcategory', 'General')
        by_category[category][subcategory].append(agent)
        
        for skill in agent.get('skills', []):
            skills_count[skill] += 1
    
    print("=" * 80)
    print("1000 AI AGENTS - COMPREHENSIVE SUMMARY")
    print("=" * 80)
    print()
    
    # Display by category
    total = 0
    for category in sorted(by_category.keys()):
        print(f"\n{category.upper()} ({sum(len(agents) for agents in by_category[category].values())} agents)")
        print("-" * 60)
        
        for subcategory in sorted(by_category[category].keys()):
            agents = by_category[category][subcategory]
            print(f"  {subcategory}: {len(agents)} agents")
            
            # Show some example agents
            for agent in agents[:3]:
                print(f"    • {agent['name']}")
            if len(agents) > 3:
                print(f"    ... and {len(agents) - 3} more")
            
            total += len(agents)
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL AGENTS: {total}")
    print(f"{'=' * 80}")
    
    # Top skills
    print("\nTOP 20 SKILLS ACROSS ALL AGENTS:")
    print("-" * 60)
    sorted_skills = sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:20]
    for skill, count in sorted_skills:
        print(f"  {skill}: {count} agents")
    
    print("\nUSAGE EXAMPLES:")
    print("-" * 60)
    print("# Show all categories")
    print("python load_1000_agents.py --list-categories")
    print()
    print("# List engineering agents")
    print("python load_1000_agents.py --category Engineering")
    print()
    print("# Search for Python agents")
    print("python load_1000_agents.py --search Python")
    print()
    print("# Chat with a random SRE agent")
    print("python load_1000_agents.py --random --category 'SRE/DevOps'")
    print()
    print("# Use specific agent")
    print("python load_1000_agents.py --agent ReactDeveloper_1 --query 'How do I optimize React performance?'")


if __name__ == "__main__":
    display_summary()
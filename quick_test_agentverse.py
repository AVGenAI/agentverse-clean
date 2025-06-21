#!/usr/bin/env python3
"""
Quick AgentVerse Tests - See it in action!
"""
import os
import json
import random
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key

load_dotenv()

def test_1_list_domains():
    """Test 1: List all AgentVerse domains"""
    print("\n🌌 TEST 1: List AgentVerse Domains")
    print("-" * 50)
    
    # Load agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    domains = {}
    for agent in agents:
        domain = agent.get("enhanced_metadata", {}).get("canonical_name", "").split(".")[1]
        if domain:
            domains[domain] = domains.get(domain, 0) + 1
    
    print(f"\n📊 Found {len(domains)} domains with {len(agents)} total agents:")
    for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
        print(f"  • agentverse.{domain}.*  →  {count} agents")


def test_2_random_agent_chat():
    """Test 2: Chat with a random agent"""
    print("\n\n🌌 TEST 2: Chat with Random Agent")
    print("-" * 50)
    
    # Set API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ No OpenAI API key found")
        return
    
    set_default_openai_key(os.getenv("OPENAI_API_KEY"))
    
    # Load agents and pick random one
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    agent_data = random.choice(agents)
    metadata = agent_data["enhanced_metadata"]
    
    print(f"\n🎲 Randomly selected: {metadata['avatar_emoji']} {metadata['display_name']}")
    print(f"🆔 ID: {metadata['canonical_name']}")
    print(f"🎯 Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
    
    # Create agent
    agent = Agent(
        name=metadata['display_name'],
        instructions=agent_data['instructions'],
        model="gpt-4o-mini"
    )
    
    # Chat
    query = "What are your top 3 recommendations for someone starting in your field?"
    print(f"\n💬 User: {query}")
    
    result = Runner.run_sync(agent, query)
    print(f"\n🤖 {metadata['display_name']}: {result.final_output}")


def test_3_find_specialists():
    """Test 3: Find specialists for a specific skill"""
    print("\n\n🌌 TEST 3: Find Specialists")
    print("-" * 50)
    
    # Load agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    # Skills to search
    skills_to_find = ["React", "Python", "Kubernetes", "Security", "Data Science"]
    
    for skill in skills_to_find:
        specialists = []
        
        for agent in agents:
            agent_skills = agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])
            if skill in agent_skills:
                specialists.append(agent)
        
        print(f"\n🔍 {skill} Specialists: {len(specialists)} found")
        
        # Show first 3
        for agent in specialists[:3]:
            metadata = agent["enhanced_metadata"]
            print(f"  • {metadata['avatar_emoji']} {metadata['display_name']} ({metadata['canonical_name']})")


def test_4_team_assembly():
    """Test 4: Assemble a team for a project"""
    print("\n\n🌌 TEST 4: Auto Team Assembly")
    print("-" * 50)
    
    print("\n🎯 Project: Build a Mobile Banking App")
    
    # Load agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    # Required roles
    roles_needed = {
        "Mobile Developer": ["React Native", "iOS", "Android", "Mobile"],
        "Backend Developer": ["Python", "API", "Security", "Authentication"],
        "Security Expert": ["Security", "Authentication", "Encryption", "Compliance"],
        "UI/UX Designer": ["UI/UX", "Design", "Frontend", "User Experience"],
        "Database Expert": ["Database", "PostgreSQL", "MongoDB", "Performance"]
    }
    
    team = {}
    
    for role, keywords in roles_needed.items():
        best_agent = None
        best_score = 0
        
        for agent in agents:
            skills = " ".join(agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])).lower()
            score = sum(1 for keyword in keywords if keyword.lower() in skills)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent:
            team[role] = best_agent
    
    print("\n✅ Assembled Team:")
    for role, agent in team.items():
        metadata = agent["enhanced_metadata"]
        print(f"\n  {role}:")
        print(f"    {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"    Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")


def test_5_collaboration_network():
    """Test 5: Show collaboration possibilities"""
    print("\n\n🌌 TEST 5: Collaboration Network")
    print("-" * 50)
    
    # Load agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    # Pick a frontend developer
    frontend_agent = next((a for a in agents if "frontend" in a.get("enhanced_metadata", {}).get("canonical_name", "")), None)
    
    if frontend_agent:
        metadata = frontend_agent["enhanced_metadata"]
        print(f"\n🤖 Agent: {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"🆔 ID: {metadata['canonical_name']}")
        
        # Show who they can collaborate with
        print("\n🤝 Can collaborate with:")
        
        # Find potential collaborators based on upstream dependencies
        collab_domains = set()
        for dep in metadata.get("network", {}).get("upstream", []):
            if "." in dep:
                domain = dep.split(".")[1]
                collab_domains.add(domain)
        
        for domain in collab_domains:
            # Find agents in that domain
            domain_agents = [a for a in agents[:50] if domain in a.get("enhanced_metadata", {}).get("canonical_name", "")]
            if domain_agents:
                print(f"\n  {domain.upper()} specialists:")
                for agent in domain_agents[:3]:
                    meta = agent["enhanced_metadata"]
                    print(f"    • {meta['avatar_emoji']} {meta['display_name']}")


def main():
    print("\n" + "="*80)
    print("🌌 AGENTVERSE QUICK TESTS")
    print("="*80)
    
    # Run all tests
    test_1_list_domains()
    test_2_random_agent_chat()
    test_3_find_specialists()
    test_4_team_assembly()
    test_5_collaboration_network()
    
    print("\n" + "="*80)
    print("✨ Tests Complete! AgentVerse is working!")
    print("="*80)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Show AgentVerse Platform Overview - Non-interactive
"""
import json
import random
from collections import defaultdict

def load_agents():
    """Load AgentVerse agents"""
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        return json.load(f)

def show_platform_overview():
    """Show complete platform overview"""
    agents = load_agents()
    
    print("\n" + "="*80)
    print("🌌 AGENTVERSE PLATFORM OVERVIEW")
    print("="*80)
    print(f"\n✅ Total Agents: {len(agents)}")
    
    # 1. Domain Structure
    print("\n📂 DOMAIN STRUCTURE:")
    print("-"*60)
    
    domains = defaultdict(lambda: defaultdict(int))
    for agent in agents:
        canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "")
        if "." in canonical:
            parts = canonical.split(".")
            domain = parts[1]
            subdomain = parts[2] if len(parts) > 2 else "general"
            domains[domain][subdomain] += 1
    
    for domain, subdomains in sorted(domains.items()):
        total = sum(subdomains.values())
        print(f"\nagentverse.{domain}.*  ({total} agents)")
        for subdomain, count in sorted(subdomains.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  └─ {subdomain}: {count} agents")
    
    # 2. Top Skills
    print("\n\n🏆 TOP 15 SKILLS:")
    print("-"*60)
    
    skills_count = defaultdict(int)
    for agent in agents:
        skills = agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])
        for skill in skills:
            skills_count[skill] += 1
    
    for i, (skill, count) in enumerate(sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:15], 1):
        bar = "█" * (count // 5)
        print(f"{i:2}. {skill:25} {bar} {count}")
    
    # 3. Sample Agents
    print("\n\n🤖 SAMPLE AGENTS:")
    print("-"*60)
    
    # Pick one agent from each major domain
    domain_samples = {}
    for agent in agents:
        canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "")
        domain = canonical.split(".")[1] if "." in canonical else "unknown"
        
        if domain not in domain_samples and len(domain_samples) < 6:
            domain_samples[domain] = agent
    
    for domain, agent in domain_samples.items():
        metadata = agent["enhanced_metadata"]
        print(f"\n{metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"  🆔 {metadata['canonical_name']}")
        print(f"  🎯 {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
        print(f"  🤝 {', '.join(metadata['collaboration']['style'])}")
    
    # 4. Example Team Assembly
    print("\n\n👥 EXAMPLE: AUTO-ASSEMBLED TEAM FOR E-COMMERCE PROJECT:")
    print("-"*60)
    
    roles = {
        "Frontend Lead": ["React", "UI/UX", "E-commerce"],
        "Backend Architect": ["Python", "API Design", "Microservices"],
        "Database Expert": ["PostgreSQL", "Performance", "Scaling"],
        "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD"],
        "Security Specialist": ["Security", "Authentication", "OWASP"]
    }
    
    for role, keywords in roles.items():
        best_agent = None
        best_score = 0
        
        for agent in agents[:300]:
            skills = " ".join(agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])).lower()
            score = sum(1 for k in keywords if k.lower() in skills)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent:
            metadata = best_agent["enhanced_metadata"]
            print(f"\n{role}:")
            print(f"  {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"  Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
    
    # 5. Platform Statistics
    print("\n\n📊 PLATFORM STATISTICS:")
    print("-"*60)
    
    categories = defaultdict(int)
    collab_styles = defaultdict(int)
    
    for agent in agents:
        cat = agent.get("category", "Unknown")
        categories[cat] += 1
        
        for style in agent.get("enhanced_metadata", {}).get("collaboration", {}).get("style", []):
            collab_styles[style] += 1
    
    print(f"\nCategories: {len(categories)}")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  • {cat}: {count} agents")
    
    print(f"\nCollaboration Patterns:")
    for style, count in sorted(collab_styles.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(agents)) * 100
        print(f"  • {style}: {count} agents ({percentage:.1f}%)")
    
    # 6. How to Use
    print("\n\n🚀 HOW TO USE AGENTVERSE:")
    print("-"*60)
    print("""
1. SETUP (if you want chat features):
   ./setup_agentverse.sh
   # Add your OpenAI API key to .env file

2. EXPLORE AGENTS:
   python agentverse_explorer.py --list-domains
   python agentverse_explorer.py --search "kubernetes"

3. CHAT WITH AGENTS (requires API key):
   python agentverse_chat.py --agent agentverse.engineering.backend.django

4. INTERACTIVE DEMO:
   python interactive_agentverse_demo.py

5. VIEW THIS OVERVIEW:
   python show_agentverse_platform.py
""")
    
    print("="*80)
    print("✨ Welcome to AgentVerse - Where 1000 AI Agents Collaborate!")
    print("="*80)

if __name__ == "__main__":
    show_platform_overview()
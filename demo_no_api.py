#!/usr/bin/env python3
"""
AgentVerse Demo - No API Required
Shows the platform capabilities without needing OpenAI API
"""
import json
import random
from collections import defaultdict

def load_agents():
    """Load AgentVerse agents"""
    try:
        with open("src/config/agentverse_agents_1000.json", 'r') as f:
            return json.load(f)
    except:
        print("❌ Could not load agents. Please run: python rebrand_to_agentverse.py")
        return []

def show_banner():
    """Show AgentVerse banner"""
    print("\n" + "="*80)
    try:
        with open("agentverse_logo.txt", 'r') as f:
            print(f.read())
    except:
        print("🌌 AGENTVERSE - Where AI Agents Collaborate")
    print("="*80)

def demo_1_explore_domains(agents):
    """Demo 1: Explore agent domains"""
    print("\n📍 DEMO 1: AgentVerse Domain Structure")
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
        print(f"\n🌐 agentverse.{domain}.*  ({total} agents)")
        
        # Show top 3 subdomains
        for subdomain, count in sorted(subdomains.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"   └─ {subdomain}: {count} agents")

def demo_2_skill_distribution(agents):
    """Demo 2: Skill distribution analysis"""
    print("\n\n📍 DEMO 2: Top Skills in AgentVerse")
    print("-"*60)
    
    skills_count = defaultdict(int)
    
    for agent in agents:
        skills = agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])
        for skill in skills:
            skills_count[skill] += 1
    
    print("\n🏆 Top 20 Skills:")
    for skill, count in sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:20]:
        bar = "█" * (count // 5)
        print(f"{skill:25} {bar} {count}")

def demo_3_agent_showcase(agents):
    """Demo 3: Showcase random agents"""
    print("\n\n📍 DEMO 3: Meet Some AgentVerse Agents")
    print("-"*60)
    
    # Pick 5 random agents from different domains
    domains_seen = set()
    showcased = []
    
    for agent in random.sample(agents, min(50, len(agents))):
        canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "")
        domain = canonical.split(".")[1] if "." in canonical else "unknown"
        
        if domain not in domains_seen and len(showcased) < 5:
            domains_seen.add(domain)
            showcased.append(agent)
    
    for agent in showcased:
        metadata = agent["enhanced_metadata"]
        print(f"\n{metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"   🆔 ID: {metadata['canonical_name']}")
        print(f"   🎯 Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
        print(f"   🛠️ Tools: {', '.join(list(metadata['capabilities']['tools_mastery'].keys())[:3])}")
        print(f"   🤝 Style: {', '.join(metadata['collaboration']['style'])}")
        print(f"   ⚡ Performance: {metadata['performance']['complexity']} complexity")

def demo_4_team_assembly(agents):
    """Demo 4: Automatic team assembly"""
    print("\n\n📍 DEMO 4: Automatic Team Assembly")
    print("-"*60)
    
    projects = [
        ("E-commerce Platform", {
            "Frontend Developer": ["React", "UI/UX", "JavaScript"],
            "Backend Developer": ["Python", "API Design", "Django"],
            "Database Architect": ["PostgreSQL", "Database", "Performance"],
            "Payment Specialist": ["Payment", "Security", "Integration"],
            "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD"]
        }),
        ("Mobile Banking App", {
            "Mobile Developer": ["React Native", "Mobile", "iOS"],
            "Security Expert": ["Security", "Authentication", "Encryption"],
            "Backend Engineer": ["API Design", "Python", "Microservices"],
            "UX Designer": ["UI/UX", "Design", "Mobile"],
            "Compliance Specialist": ["Compliance", "Finance", "Regulations"]
        })
    ]
    
    for project_name, roles in projects:
        print(f"\n🚀 Project: {project_name}")
        print("   Team:")
        
        for role, keywords in roles.items():
            # Find best match
            best_agent = None
            best_score = 0
            
            for agent in agents[:200]:  # Check first 200 for speed
                skills = " ".join(agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])).lower()
                canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "").lower()
                
                score = sum(2 if keyword.lower() in skills else 1 if keyword.lower() in canonical else 0 
                           for keyword in keywords)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                metadata = best_agent["enhanced_metadata"]
                print(f"   • {role}: {metadata['avatar_emoji']} {metadata['display_name']}")

def demo_5_collaboration_network(agents):
    """Demo 5: Collaboration network analysis"""
    print("\n\n📍 DEMO 5: Collaboration Network")
    print("-"*60)
    
    # Pick a random engineering agent
    eng_agents = [a for a in agents if "engineering" in a.get("enhanced_metadata", {}).get("canonical_name", "")]
    
    if eng_agents:
        agent = random.choice(eng_agents[:10])
        metadata = agent["enhanced_metadata"]
        
        print(f"\n🤖 Agent: {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"   ID: {metadata['canonical_name']}")
        print(f"   Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
        
        print("\n   🤝 Can collaborate with:")
        
        # Show upstream dependencies
        for pattern in metadata.get("network", {}).get("upstream", [])[:3]:
            if "." in pattern:
                domain = pattern.split(".")[1]
                print(f"      → {domain} specialists")
        
        # Show collaboration style
        print(f"\n   💫 Collaboration style: {', '.join(metadata['collaboration']['style'])}")
        print(f"   👥 Preferred team size: {metadata['collaboration']['team_size']}")

def demo_6_statistics(agents):
    """Demo 6: Platform statistics"""
    print("\n\n📍 DEMO 6: AgentVerse Statistics")
    print("-"*60)
    
    # Categories
    categories = defaultdict(int)
    for agent in agents:
        cat = agent.get("category", "Unknown")
        categories[cat] += 1
    
    # Collaboration styles
    collab_styles = defaultdict(int)
    for agent in agents:
        for style in agent.get("enhanced_metadata", {}).get("collaboration", {}).get("style", []):
            collab_styles[style] += 1
    
    # Trust scores
    trust_scores = [
        agent.get("enhanced_metadata", {}).get("quality", {}).get("trust_score", 0)
        for agent in agents
    ]
    avg_trust = sum(trust_scores) / len(trust_scores) if trust_scores else 0
    
    print(f"\n📊 Platform Overview:")
    print(f"   • Total Agents: {len(agents)}")
    print(f"   • Average Trust Score: {avg_trust:.2f}")
    print(f"   • Categories: {len(categories)}")
    
    print("\n📂 Agents by Category:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"   • {cat}: {count} agents")
    
    print("\n🤝 Collaboration Styles:")
    for style, count in sorted(collab_styles.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / len(agents)) * 100
        print(f"   • {style}: {count} agents ({percentage:.1f}%)")

def main():
    """Run all demos"""
    show_banner()
    
    agents = load_agents()
    if not agents:
        return
    
    print(f"\n✅ Loaded {len(agents)} agents from AgentVerse")
    print("\n🎬 Starting AgentVerse Demo (No API Required)")
    
    demos = [
        demo_1_explore_domains,
        demo_2_skill_distribution,
        demo_3_agent_showcase,
        demo_4_team_assembly,
        demo_5_collaboration_network,
        demo_6_statistics
    ]
    
    for demo in demos:
        demo(agents)
        input("\n➡️  Press Enter for next demo...")
    
    print("\n" + "="*80)
    print("✨ AgentVerse Demo Complete!")
    print("\nTo use chat features, set up your OpenAI API key:")
    print("1. Run: ./setup_agentverse.sh")
    print("2. Add your API key to .env file")
    print("3. Run: python interactive_agentverse_demo.py")
    print("="*80)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Update all agents with taxonomy standards
"""
import json
from src.taxonomy import enhance_agent_with_taxonomy, AgentDiscoveryService


def update_agents_with_taxonomy():
    """Update all agents with taxonomy information"""
    
    # Load existing agents
    with open("src/config/1000_agents.json", 'r') as f:
        agents = json.load(f)
    
    print(f"Loaded {len(agents)} agents")
    
    # Enhance each agent with taxonomy
    enhanced_agents = []
    agent_counter = {}  # Track instance numbers per specialty
    
    for i, agent in enumerate(agents):
        # Generate unique instance number per specialty
        category = agent.get("category", "")
        subcategory = agent.get("subcategory", "")
        name_base = agent.get("name", "").split("_")[0]  # Get base name without number
        
        key = f"{category}.{subcategory}.{name_base}"
        if key not in agent_counter:
            agent_counter[key] = 0
        agent_counter[key] += 1
        
        # Enhance with taxonomy
        enhanced_agent = enhance_agent_with_taxonomy(agent, agent_counter[key])
        enhanced_agents.append(enhanced_agent)
        
        if (i + 1) % 100 == 0:
            print(f"Processed {i + 1} agents...")
    
    # Save enhanced agents
    output_file = "src/config/1000_agents_with_taxonomy.json"
    with open(output_file, 'w') as f:
        json.dump(enhanced_agents, f, indent=2)
    
    print(f"\nSaved enhanced agents to {output_file}")
    
    # Test discovery service
    print("\n=== Testing Discovery Service ===")
    discovery = AgentDiscoveryService(enhanced_agents)
    
    # Example: Find collaborators for a backend developer
    backend_agent = next((a for a in enhanced_agents if "backend" in a.get("taxonomy", {}).get("subdomain", "")), None)
    if backend_agent:
        agent_id = backend_agent["taxonomy"]["agent_id"]
        print(f"\nFinding collaborators for {agent_id}:")
        collaborators = discovery.find_collaborators(agent_id)
        for collab in collaborators[:5]:
            print(f"  - {collab['taxonomy']['agent_id']}: {collab['name']}")
    
    # Example: Find all Python specialists
    python_agents = discovery.find_by_skill("Python")
    print(f"\nFound {len(python_agents)} agents with Python skill")
    
    # Example: Find all monitoring agents
    monitoring_agents = discovery.find_by_pattern("sre_devops.monitoring.*")
    print(f"\nFound {len(monitoring_agents)} monitoring agents")
    
    # Generate summary
    print("\n=== Taxonomy Summary ===")
    domains = {}
    for agent in enhanced_agents:
        domain = agent["taxonomy"]["domain"]
        if domain not in domains:
            domains[domain] = 0
        domains[domain] += 1
    
    for domain, count in sorted(domains.items()):
        print(f"{domain}: {count} agents")
    
    # Also save category-specific files with taxonomy
    categories = {}
    for agent in enhanced_agents:
        category = agent['category']
        if category not in categories:
            categories[category] = []
        categories[category].append(agent)
    
    for category, category_agents in categories.items():
        category_file = f"src/config/agents_{category.lower().replace(' ', '_').replace('/', '_')}_taxonomy.json"
        with open(category_file, 'w') as f:
            json.dump(category_agents, f, indent=2)
    
    print(f"\nCreated {len(categories)} category-specific files with taxonomy")


def create_collaboration_graph():
    """Create a visualization of agent collaboration patterns"""
    with open("src/config/1000_agents_with_taxonomy.json", 'r') as f:
        agents = json.load(f)
    
    # Create collaboration report
    report = {
        "total_agents": len(agents),
        "collaboration_patterns": {},
        "domain_connections": {},
        "tier_distribution": {}
    }
    
    for agent in agents:
        taxonomy = agent.get("taxonomy", {})
        domain = taxonomy.get("domain")
        tier = taxonomy.get("tier")
        
        # Count tiers
        if tier not in report["tier_distribution"]:
            report["tier_distribution"][tier] = 0
        report["tier_distribution"][tier] += 1
        
        # Track collaboration patterns
        for pattern in taxonomy.get("can_collaborate_with", []):
            if pattern not in report["collaboration_patterns"]:
                report["collaboration_patterns"][pattern] = []
            report["collaboration_patterns"][pattern].append(taxonomy.get("agent_id"))
    
    # Save report
    with open("src/config/collaboration_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\nCreated collaboration report: src/config/collaboration_report.json")


if __name__ == "__main__":
    update_agents_with_taxonomy()
    create_collaboration_graph()
#!/usr/bin/env python3
"""
Spawn Fresh Agents Script
Creates a clean set of 1000 agents with clear tracking
"""
import json
import os
from datetime import datetime
from typing import List, Dict
import uuid

def create_clean_agent_set():
    """Create a fresh, trackable set of agents"""
    print("🚀 Starting fresh agent creation...")
    print("="*60)
    
    # Start with just essential agents for testing
    essential_agents = [
        {
            "id": "sre_servicenow_001",
            "name": "SRE ServiceNow Specialist",
            "type": "specialist",
            "domain": "sre",
            "subdomain": "servicenow",
            "instructions": """You are an expert Site Reliability Engineer with ServiceNow expertise.
Your primary responsibilities:
- Incident Management and Response
- SLO Monitoring and Management
- Runbook Automation
- Root Cause Analysis

Available tools:
- search_incidents: Find incidents in ServiceNow
- create_incident: Create new incidents
- update_incident: Update incident status
- calculate_slo_status: Check SLO health
- get_runbook: Retrieve runbooks""",
            "capabilities": {
                "primary_expertise": ["Incident Response", "ServiceNow Platform", "SLO Management"],
                "tools_mastery": {
                    "servicenow": "expert",
                    "monitoring": "expert",
                    "automation": "advanced"
                }
            },
            "enhanced_metadata": {
                "agent_uuid": "sre_servicenow_001",
                "canonical_name": "agentverse.sre.servicenow_specialist",
                "display_name": "SRE ServiceNow Specialist",
                "avatar": "🚨",
                "trust_score": 0.95,
                "collaboration_style": "systematic"
            }
        },
        {
            "id": "devops_kubernetes_001",
            "name": "DevOps Kubernetes Expert",
            "type": "specialist",
            "domain": "devops",
            "subdomain": "kubernetes",
            "instructions": "You are a Kubernetes and container orchestration expert.",
            "capabilities": {
                "primary_expertise": ["Kubernetes", "Docker", "CI/CD"],
                "tools_mastery": {
                    "kubernetes": "expert",
                    "docker": "expert",
                    "helm": "advanced"
                }
            },
            "enhanced_metadata": {
                "agent_uuid": "devops_kubernetes_001",
                "canonical_name": "agentverse.devops.kubernetes_expert",
                "display_name": "DevOps Kubernetes Expert",
                "avatar": "☸️",
                "trust_score": 0.92,
                "collaboration_style": "technical"
            }
        },
        {
            "id": "data_analytics_001",
            "name": "Data Analytics Specialist",
            "type": "specialist", 
            "domain": "data",
            "subdomain": "analytics",
            "instructions": "You are a data analytics expert specializing in insights and visualization.",
            "capabilities": {
                "primary_expertise": ["Data Analysis", "SQL", "Python"],
                "tools_mastery": {
                    "sql": "expert",
                    "python": "expert",
                    "tableau": "advanced"
                }
            },
            "enhanced_metadata": {
                "agent_uuid": "data_analytics_001",
                "canonical_name": "agentverse.data.analytics_specialist",
                "display_name": "Data Analytics Specialist",
                "avatar": "📊",
                "trust_score": 0.90,
                "collaboration_style": "analytical"
            }
        }
    ]
    
    # Create config directory if it doesn't exist
    config_dir = "src/config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Save essential agents first
    essential_file = os.path.join(config_dir, "essential_agents.json")
    with open(essential_file, 'w') as f:
        json.dump(essential_agents, f, indent=2)
    print(f"✅ Created {len(essential_agents)} essential agents")
    
    # Generate remaining agents to reach 1000
    all_agents = essential_agents.copy()
    
    # Define domains and subdomains for variety
    domains = {
        "engineering": ["frontend", "backend", "mobile", "qa", "architecture"],
        "data": ["analytics", "science", "engineering", "visualization", "ml"],
        "security": ["appsec", "netsec", "compliance", "forensics", "devsecops"],
        "devops": ["kubernetes", "aws", "azure", "gcp", "terraform"],
        "sre": ["monitoring", "incident", "automation", "performance", "reliability"],
        "product": ["management", "design", "research", "strategy", "growth"],
        "business": ["sales", "marketing", "finance", "hr", "operations"]
    }
    
    agent_count = len(essential_agents)
    
    # Generate agents for each domain
    for domain, subdomains in domains.items():
        for subdomain in subdomains:
            # Skip if we already have this combination in essential agents
            if any(a["domain"] == domain and a["subdomain"] == subdomain for a in essential_agents):
                continue
                
            # Calculate how many agents to create per subdomain
            agents_per_subdomain = (1000 - len(essential_agents)) // sum(len(subs) for subs in domains.values())
            
            for i in range(agents_per_subdomain + 5):  # Add a few extra to ensure we reach 1000
                if len(all_agents) >= 1000:
                    break
                    
                agent_id = f"{domain}_{subdomain}_{str(agent_count).zfill(3)}"
                agent = {
                    "id": agent_id,
                    "name": f"{domain.title()} {subdomain.title()} Agent {i+1}",
                    "type": "specialist",
                    "domain": domain,
                    "subdomain": subdomain,
                    "instructions": f"You are a {domain} expert specializing in {subdomain}.",
                    "capabilities": {
                        "primary_expertise": [subdomain.title(), domain.title()],
                        "tools_mastery": {}
                    },
                    "enhanced_metadata": {
                        "agent_uuid": agent_id,
                        "canonical_name": f"agentverse.{domain}.{subdomain}_{i+1}",
                        "display_name": f"{domain.title()} {subdomain.title()} Agent {i+1}",
                        "avatar": "🤖",
                        "trust_score": 0.80 + (i * 0.001),
                        "collaboration_style": "collaborative"
                    }
                }
                all_agents.append(agent)
            
            if agent_count > 1000:
                break
        if agent_count > 1000:
            break
    
    # Trim to exactly 1000 agents
    all_agents = all_agents[:1000]
    
    # Save to main config file
    main_config_file = os.path.join(config_dir, "agentverse_agents_1000.json")
    with open(main_config_file, 'w') as f:
        json.dump(all_agents, f, indent=2)
    
    print(f"\n✅ Created {len(all_agents)} total agents")
    print(f"📁 Saved to: {main_config_file}")
    
    # Create agent index for easy lookup
    agent_index = {
        "total_agents": len(all_agents),
        "domains": {},
        "essential_agents": [a["id"] for a in essential_agents],
        "created_at": datetime.now().isoformat()
    }
    
    # Build domain index
    for agent in all_agents:
        domain = agent["domain"]
        if domain not in agent_index["domains"]:
            agent_index["domains"][domain] = []
        agent_index["domains"][domain].append(agent["id"])
    
    # Save index
    index_file = os.path.join(config_dir, "agent_index.json")
    with open(index_file, 'w') as f:
        json.dump(agent_index, f, indent=2)
    
    print(f"\n📊 Agent Distribution:")
    for domain, agent_ids in agent_index["domains"].items():
        print(f"  - {domain}: {len(agent_ids)} agents")
    
    print(f"\n🌟 Essential agents ready for testing:")
    for agent in essential_agents:
        print(f"  - {agent['enhanced_metadata']['display_name']} ({agent['id']})")
    
    return len(all_agents)

if __name__ == "__main__":
    try:
        total = create_clean_agent_set()
        print(f"\n✨ Successfully created {total} fresh agents!")
        print("\n💡 Next steps:")
        print("1. Restart the API server to load new agents")
        print("2. Test with essential agents first (especially sre_servicenow_001)")
        print("3. Verify tool execution is working")
    except Exception as e:
        print(f"\n❌ Error creating agents: {e}")
        import traceback
        traceback.print_exc()
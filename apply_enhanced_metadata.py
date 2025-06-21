#!/usr/bin/env python3
"""
Apply enhanced metadata to all 1000 agents
"""
import json
from typing import Dict, List, Any
from collections import defaultdict
from src.taxonomy.enhanced_agent_metadata import enhance_agent_with_rich_metadata


def apply_enhanced_metadata():
    """Apply enhanced metadata to all agents"""
    
    # Load agents
    with open("src/config/1000_agents.json", 'r') as f:
        agents = json.load(f)
    
    print(f"Processing {len(agents)} agents with enhanced metadata...")
    
    # Process each agent
    enhanced_agents = []
    metadata_summary = defaultdict(list)
    
    for i, agent in enumerate(agents):
        # Apply enhanced metadata
        enhanced_agent = enhance_agent_with_rich_metadata(agent)
        enhanced_agents.append(enhanced_agent)
        
        # Track metadata for summary
        metadata = enhanced_agent.get("enhanced_metadata", {})
        canonical_name = metadata.get("canonical_name", "")
        domain = canonical_name.split(".")[1] if "." in canonical_name else "unknown"
        metadata_summary[domain].append({
            "uuid": metadata.get("agent_uuid"),
            "name": metadata.get("display_name"),
            "canonical": canonical_name,
            "emoji": metadata.get("avatar_emoji"),
            "primary_skills": metadata.get("capabilities", {}).get("primary_expertise", [])
        })
        
        if (i + 1) % 100 == 0:
            print(f"  Processed {i + 1} agents...")
    
    # Save enhanced agents
    output_file = "src/config/1000_agents_enhanced.json"
    with open(output_file, 'w') as f:
        json.dump(enhanced_agents, f, indent=2)
    
    print(f"\n✅ Saved enhanced agents to {output_file}")
    
    # Create a discovery index
    create_discovery_index(enhanced_agents)
    
    # Create collaboration network map
    create_collaboration_network(enhanced_agents)
    
    # Print summary
    print_metadata_summary(metadata_summary)


def create_discovery_index(agents: List[Dict[str, Any]]):
    """Create a searchable index for agent discovery"""
    
    index = {
        "by_uuid": {},
        "by_canonical_name": {},
        "by_skill": defaultdict(list),
        "by_domain": defaultdict(list),
        "by_problem": defaultdict(list),
        "by_emoji": defaultdict(list),
        "skill_cloud": defaultdict(int),
        "collaboration_styles": defaultdict(int)
    }
    
    for agent in agents:
        metadata = agent.get("enhanced_metadata", {})
        uuid = metadata.get("agent_uuid")
        canonical = metadata.get("canonical_name")
        
        # Index by identifiers
        index["by_uuid"][uuid] = agent
        index["by_canonical_name"][canonical] = agent
        
        # Index by skills
        for skill in metadata.get("capabilities", {}).get("primary_expertise", []):
            index["by_skill"][skill.lower()].append({
                "uuid": uuid,
                "name": metadata.get("display_name"),
                "canonical": canonical
            })
            index["skill_cloud"][skill] += 1
        
        # Index by domain
        domain = canonical.split(".")[1] if "." in canonical else "unknown"
        index["by_domain"][domain].append({
            "uuid": uuid,
            "name": metadata.get("display_name"),
            "emoji": metadata.get("avatar_emoji")
        })
        
        # Index by problem domains
        for problem in metadata.get("discovery", {}).get("problem_domains", []):
            index["by_problem"][problem].append(uuid)
        
        # Index by emoji
        emoji = metadata.get("avatar_emoji", "🤖")
        index["by_emoji"][emoji].append(metadata.get("display_name"))
        
        # Track collaboration styles
        for style in metadata.get("collaboration", {}).get("style", []):
            index["collaboration_styles"][style] += 1
    
    # Save index
    with open("src/config/agent_discovery_index.json", 'w') as f:
        json.dump(dict(index), f, indent=2)
    
    print("\n✅ Created discovery index: src/config/agent_discovery_index.json")


def create_collaboration_network(agents: List[Dict[str, Any]]):
    """Create a network map of agent collaborations"""
    
    network = {
        "nodes": [],
        "edges": [],
        "clusters": defaultdict(list),
        "collaboration_patterns": {}
    }
    
    # Create nodes
    for agent in agents:
        metadata = agent.get("enhanced_metadata", {})
        node = {
            "id": metadata.get("agent_uuid"),
            "label": metadata.get("display_name"),
            "canonical": metadata.get("canonical_name"),
            "emoji": metadata.get("avatar_emoji"),
            "domain": metadata.get("canonical_name", "").split(".")[1] if "." in metadata.get("canonical_name", "") else "unknown",
            "trust_score": metadata.get("quality", {}).get("trust_score", 0.95),
            "collaboration_style": metadata.get("collaboration", {}).get("style", [])
        }
        network["nodes"].append(node)
        
        # Group by domain
        network["clusters"][node["domain"]].append(node["id"])
    
    # Create edges based on dependencies
    for agent in agents:
        metadata = agent.get("enhanced_metadata", {})
        source_id = metadata.get("agent_uuid")
        
        # Add upstream dependencies
        for dep_pattern in metadata.get("network", {}).get("upstream", []):
            # For demo, create edges to agents in matching domains
            domain = dep_pattern.split(".")[1] if "." in dep_pattern else None
            if domain and domain in network["clusters"]:
                for target_id in network["clusters"][domain][:3]:  # Connect to first 3 in domain
                    if target_id != source_id:
                        network["edges"].append({
                            "source": source_id,
                            "target": target_id,
                            "type": "depends_on"
                        })
    
    # Identify collaboration patterns
    collab_counts = defaultdict(int)
    for node in network["nodes"]:
        styles = node.get("collaboration_style", [])
        for style in styles:
            collab_counts[style] += 1
    
    network["collaboration_patterns"] = dict(collab_counts)
    
    # Save network
    with open("src/config/agent_collaboration_network.json", 'w') as f:
        json.dump(dict(network), f, indent=2)
    
    print("✅ Created collaboration network: src/config/agent_collaboration_network.json")


def print_metadata_summary(metadata_summary: Dict[str, List[Dict]]):
    """Print a beautiful summary of the enhanced metadata"""
    
    print("\n" + "="*80)
    print("🤖 ENHANCED AGENT METADATA SUMMARY")
    print("="*80)
    
    # Count by domain
    print("\n📊 AGENTS BY DOMAIN:")
    print("-"*50)
    for domain, agents in sorted(metadata_summary.items()):
        # Get unique emojis for this domain
        emojis = list(set([a["emoji"] for a in agents]))[:5]
        emoji_str = " ".join(emojis)
        print(f"{domain.ljust(20)} {len(agents):4d} agents  {emoji_str}")
    
    # Show sample agents
    print("\n🌟 SAMPLE ENHANCED AGENTS:")
    print("-"*50)
    
    sample_domains = ["engineering", "business", "sre_devops", "data"]
    for domain in sample_domains:
        if domain in metadata_summary:
            agents = metadata_summary[domain][:3]
            print(f"\n{domain.upper()}:")
            for agent in agents:
                print(f"  {agent['emoji']} {agent['name']}")
                print(f"     UUID: {agent['uuid']}")
                print(f"     Canonical: {agent['canonical']}")
                print(f"     Skills: {', '.join(agent['primary_skills'][:3])}")
    
    print("\n" + "="*80)
    print("✨ All agents now have rich metadata for discovery and collaboration!")
    print("="*80)


def create_agent_catalog():
    """Create a human-readable catalog of all agents"""
    
    with open("src/config/1000_agents_enhanced.json", 'r') as f:
        agents = json.load(f)
    
    catalog = []
    
    for agent in agents:
        metadata = agent.get("enhanced_metadata", {})
        entry = {
            "🆔 ID": metadata.get("canonical_name"),
            "📛 Name": f"{metadata.get('avatar_emoji')} {metadata.get('display_name')}",
            "🎯 Primary Skills": ", ".join(metadata.get("capabilities", {}).get("primary_expertise", [])[:3]),
            "🤝 Collaboration": ", ".join(metadata.get("collaboration", {}).get("style", [])),
            "⚡ Performance": metadata.get("performance", {}).get("complexity", "medium"),
            "🔍 Keywords": ", ".join(list(metadata.get("discovery", {}).get("keywords", []))[:5])
        }
        catalog.append(entry)
    
    # Save as formatted JSON
    with open("src/config/agent_catalog.json", 'w') as f:
        json.dump(catalog, f, indent=2)
    
    # Save first 10 as markdown for easy viewing
    with open("AGENT_CATALOG_SAMPLE.md", 'w') as f:
        f.write("# 🤖 AI Agent Catalog Sample\n\n")
        f.write("This is a sample of the first 10 agents from our collection of 1000 AI agents.\n\n")
        
        for i, entry in enumerate(catalog[:10], 1):
            f.write(f"## Agent #{i}\n\n")
            for key, value in entry.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n---\n\n")
    
    print("✅ Created agent catalog: src/config/agent_catalog.json")
    print("✅ Created sample catalog: AGENT_CATALOG_SAMPLE.md")


if __name__ == "__main__":
    apply_enhanced_metadata()
    create_agent_catalog()
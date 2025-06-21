#!/usr/bin/env python3
"""
Demo: Agent Discovery and Collaboration using Enhanced Metadata
"""
import json
import random
from typing import List, Dict, Any


class AgentDiscoveryDemo:
    def __init__(self):
        # Load enhanced agents
        with open("src/config/1000_agents_enhanced.json", 'r') as f:
            self.agents = json.load(f)
        
        # Load discovery index
        with open("src/config/agent_discovery_index.json", 'r') as f:
            self.index = json.load(f)
        
        # Load collaboration network
        with open("src/config/agent_collaboration_network.json", 'r') as f:
            self.network = json.load(f)
        
        # Create quick lookup
        self.agents_by_uuid = {
            agent["enhanced_metadata"]["agent_uuid"]: agent 
            for agent in self.agents
        }
    
    def demo_skill_based_discovery(self):
        """Demo: Find agents by skill"""
        print("\n" + "="*80)
        print("🔍 SKILL-BASED AGENT DISCOVERY")
        print("="*80)
        
        # Show top skills
        skill_cloud = self.index.get("skill_cloud", {})
        top_skills = sorted(skill_cloud.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("\n📊 Top 10 Skills in Agent Network:")
        for skill, count in top_skills:
            print(f"  • {skill}: {count} agents")
        
        # Demo: Find React specialists
        print("\n🎯 Finding React Specialists...")
        react_agents = self.index["by_skill"].get("react", [])[:5]
        for agent_info in react_agents:
            agent = self.agents_by_uuid.get(agent_info["uuid"])
            if agent:
                metadata = agent["enhanced_metadata"]
                print(f"\n  {metadata['avatar_emoji']} {metadata['display_name']}")
                print(f"     ID: {metadata['canonical_name']}")
                print(f"     Skills: {', '.join(metadata['capabilities']['primary_expertise'])}")
                print(f"     Tools: {list(metadata['capabilities']['tools_mastery'].keys())[:3]}")
    
    def demo_collaboration_discovery(self):
        """Demo: Find collaboration partners"""
        print("\n" + "="*80)
        print("🤝 COLLABORATION PARTNER DISCOVERY")
        print("="*80)
        
        # Pick a frontend developer
        frontend_agents = [a for a in self.agents if "frontend" in a.get("enhanced_metadata", {}).get("canonical_name", "")]
        if frontend_agents:
            agent = random.choice(frontend_agents[:10])
            metadata = agent["enhanced_metadata"]
            
            print(f"\n👤 Agent: {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"   ID: {metadata['canonical_name']}")
            print(f"   Collaboration Style: {', '.join(metadata['collaboration']['style'])}")
            
            # Find potential collaborators
            print("\n🔗 Potential Collaboration Partners:")
            
            # Based on upstream dependencies
            for dep_pattern in metadata["network"]["upstream"][:3]:
                domain = dep_pattern.split(".")[1] if "." in dep_pattern else None
                if domain:
                    domain_agents = self.index["by_domain"].get(domain, [])[:2]
                    for partner in domain_agents:
                        print(f"\n   → {partner['emoji']} {partner['name']}")
                        print(f"     Domain: {domain}")
                        print(f"     Reason: Upstream dependency")
    
    def demo_problem_based_discovery(self):
        """Demo: Find agents by problem domain"""
        print("\n" + "="*80)
        print("🎯 PROBLEM-BASED AGENT DISCOVERY")
        print("="*80)
        
        # Show available problem domains
        problem_domains = list(self.index.get("by_problem", {}).keys())[:10]
        print("\n📋 Sample Problem Domains:")
        for domain in problem_domains:
            agent_count = len(self.index["by_problem"][domain])
            print(f"  • {domain}: {agent_count} agents")
        
        # Demo: Find agents for "software development"
        if "software development" in self.index["by_problem"]:
            print("\n💡 Agents for 'Software Development' Problems:")
            agent_uuids = self.index["by_problem"]["software development"][:5]
            for uuid in agent_uuids:
                agent = self.agents_by_uuid.get(uuid)
                if agent:
                    metadata = agent["enhanced_metadata"]
                    print(f"\n  {metadata['avatar_emoji']} {metadata['display_name']}")
                    print(f"     Expertise: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
    
    def demo_team_assembly(self):
        """Demo: Assemble a team for a project"""
        print("\n" + "="*80)
        print("👥 INTELLIGENT TEAM ASSEMBLY")
        print("="*80)
        
        print("\n📋 Project: Build a Full-Stack E-commerce Application")
        print("\n🤖 Assembling optimal team...")
        
        # Define required roles
        required_roles = [
            ("Frontend Developer", ["react", "frontend development"]),
            ("Backend Developer", ["python", "api design"]),
            ("Database Specialist", ["postgresql", "database"]),
            ("DevOps Engineer", ["kubernetes", "ci/cd"]),
            ("Security Specialist", ["security", "authentication"]),
            ("QA Engineer", ["testing", "automation"])
        ]
        
        team = []
        
        for role, skills in required_roles:
            # Find best match
            candidates = []
            for skill in skills:
                if skill in self.index["by_skill"]:
                    candidates.extend(self.index["by_skill"][skill])
            
            if candidates:
                # Pick one with highest trust score
                best_candidate = None
                best_score = 0
                
                for candidate_info in candidates[:10]:  # Check first 10
                    agent = self.agents_by_uuid.get(candidate_info["uuid"])
                    if agent:
                        trust_score = agent["enhanced_metadata"]["quality"]["trust_score"]
                        if trust_score > best_score:
                            best_score = trust_score
                            best_candidate = agent
                
                if best_candidate:
                    team.append((role, best_candidate))
        
        # Display team
        print("\n✅ Assembled Team:")
        for role, agent in team:
            metadata = agent["enhanced_metadata"]
            print(f"\n  {metadata['avatar_emoji']} {role}: {metadata['display_name']}")
            print(f"     ID: {metadata['canonical_name']}")
            print(f"     Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
            print(f"     Trust Score: {metadata['quality']['trust_score']}")
            print(f"     Collaboration: {', '.join(metadata['collaboration']['style'])}")
    
    def demo_agent_network_visualization(self):
        """Demo: Show agent network statistics"""
        print("\n" + "="*80)
        print("🌐 AGENT NETWORK VISUALIZATION")
        print("="*80)
        
        # Network statistics
        print("\n📊 Network Statistics:")
        print(f"  • Total Agents: {len(self.network['nodes'])}")
        print(f"  • Total Connections: {len(self.network['edges'])}")
        print(f"  • Domains: {len(self.network['clusters'])}")
        
        # Collaboration patterns
        print("\n🤝 Collaboration Patterns Distribution:")
        for pattern, count in self.network["collaboration_patterns"].items():
            print(f"  • {pattern}: {count} agents")
        
        # Domain sizes
        print("\n🏢 Agents per Domain:")
        for domain, agent_ids in sorted(self.network["clusters"].items(), key=lambda x: len(x[1]), reverse=True):
            print(f"  • {domain}: {len(agent_ids)} agents")


def main():
    """Run the discovery demo"""
    demo = AgentDiscoveryDemo()
    
    print("\n" + "🤖"*40)
    print("  AGENT DISCOVERY & COLLABORATION DEMO")
    print("🤖"*40)
    
    # Run all demos
    demo.demo_skill_based_discovery()
    demo.demo_collaboration_discovery()
    demo.demo_problem_based_discovery()
    demo.demo_team_assembly()
    demo.demo_agent_network_visualization()
    
    print("\n" + "="*80)
    print("✨ Demo Complete! Agents can now discover and collaborate intelligently.")
    print("="*80)


if __name__ == "__main__":
    main()
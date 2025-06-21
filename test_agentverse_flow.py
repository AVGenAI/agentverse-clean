#!/usr/bin/env python3
"""
Test AgentVerse Platform - Complete Flow Demo
"""
import os
import json
import time
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key
import random

load_dotenv()

class AgentVerseDemo:
    def __init__(self):
        # Set OpenAI key
        if os.getenv("OPENAI_API_KEY"):
            set_default_openai_key(os.getenv("OPENAI_API_KEY"))
        else:
            print("❌ No OpenAI API key found")
            exit(1)
        
        # Load AgentVerse agents
        with open("src/config/agentverse_agents_1000.json", 'r') as f:
            self.agents = json.load(f)
        
        print("\n" + "="*80)
        print("🌌 AGENTVERSE PLATFORM DEMO")
        print("="*80)
        print(f"✅ Loaded {len(self.agents)} agents from AgentVerse")
    
    def demo_1_simple_chat(self):
        """Demo 1: Simple chat with a single agent"""
        print("\n" + "-"*80)
        print("📍 DEMO 1: Simple Chat with a React Developer")
        print("-"*80)
        
        # Find a React developer
        react_agent = next((a for a in self.agents if "ReactDeveloper_1" in a.get("name", "")), None)
        if not react_agent:
            print("❌ React developer not found")
            return
        
        metadata = react_agent["enhanced_metadata"]
        print(f"\n🤖 Agent: {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"🆔 AgentVerse ID: {metadata['canonical_name']}")
        print(f"🎯 Skills: {', '.join(metadata['capabilities']['primary_expertise'])}")
        
        # Create agent
        agent = Agent(
            name=metadata['display_name'],
            instructions=react_agent['instructions'],
            model="gpt-4o-mini"
        )
        
        # Chat
        query = "How do I optimize React performance for a large e-commerce app?"
        print(f"\n💬 User: {query}")
        
        result = Runner.run_sync(agent, query)
        print(f"\n🤖 {metadata['display_name']}: {result.final_output}")
    
    def demo_2_skill_based_discovery(self):
        """Demo 2: Find agents by skill"""
        print("\n" + "-"*80)
        print("📍 DEMO 2: Skill-Based Agent Discovery")
        print("-"*80)
        
        # Find all Python experts
        python_experts = []
        for agent in self.agents:
            skills = agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])
            if "Python" in skills:
                python_experts.append(agent)
        
        print(f"\n🔍 Found {len(python_experts)} Python experts in AgentVerse")
        
        # Show first 5
        print("\n📋 Sample Python Experts:")
        for agent in python_experts[:5]:
            metadata = agent["enhanced_metadata"]
            print(f"\n  {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"     ID: {metadata['canonical_name']}")
            print(f"     Full Skills: {', '.join(skills)}")
    
    def demo_3_multi_agent_collaboration(self):
        """Demo 3: Multi-agent collaboration for a project"""
        print("\n" + "-"*80)
        print("📍 DEMO 3: Multi-Agent Project Collaboration")
        print("-"*80)
        
        print("\n🎯 Project: Build a Real-time Data Dashboard")
        print("\n🤖 Assembling specialist team...")
        
        # Define required specialists
        required_roles = [
            ("Frontend", ["React", "Dashboard", "Data Visualization"]),
            ("Backend", ["Python", "API Design", "Real-time"]),
            ("Database", ["PostgreSQL", "Time-series", "Performance"]),
            ("DevOps", ["Docker", "Kubernetes", "Monitoring"])
        ]
        
        team = []
        
        for role, keywords in required_roles:
            # Find best match
            best_match = None
            best_score = 0
            
            for agent in self.agents[:200]:  # Check first 200 for speed
                metadata = agent.get("enhanced_metadata", {})
                skills = metadata.get("capabilities", {}).get("primary_expertise", [])
                skills_str = " ".join(skills).lower()
                
                # Calculate match score
                score = sum(1 for keyword in keywords if keyword.lower() in skills_str)
                
                if score > best_score:
                    best_score = score
                    best_match = agent
            
            if best_match:
                team.append((role, best_match))
        
        # Display team
        print("\n✅ Assembled Team:")
        for role, agent in team:
            metadata = agent["enhanced_metadata"]
            print(f"\n  {role} Specialist: {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"     ID: {metadata['canonical_name']}")
            print(f"     Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
        
        # Simulate collaboration
        print("\n💬 Team Collaboration Simulation:")
        
        # Frontend asks backend
        if len(team) >= 2:
            frontend_agent = team[0][1]
            backend_agent = team[1][1]
            
            print(f"\n{frontend_agent['enhanced_metadata']['display_name']}: I need a WebSocket endpoint for real-time data updates")
            print(f"{backend_agent['enhanced_metadata']['display_name']}: I'll create a Socket.IO endpoint at /api/v1/stream with JWT auth")
    
    def demo_4_agent_network_visualization(self):
        """Demo 4: Show agent network and relationships"""
        print("\n" + "-"*80)
        print("📍 DEMO 4: AgentVerse Network Analysis")
        print("-"*80)
        
        # Analyze domains
        domains = {}
        collaboration_patterns = {}
        
        for agent in self.agents:
            metadata = agent.get("enhanced_metadata", {})
            canonical = metadata.get("canonical_name", "")
            
            if "." in canonical:
                domain = canonical.split(".")[1]
                domains[domain] = domains.get(domain, 0) + 1
            
            # Count collaboration styles
            for style in metadata.get("collaboration", {}).get("style", []):
                collaboration_patterns[style] = collaboration_patterns.get(style, 0) + 1
        
        print("\n🌐 AgentVerse Domains:")
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * (count // 10)
            print(f"  agentverse.{domain}.*  {bar} {count} agents")
        
        print("\n🤝 Collaboration Patterns:")
        for pattern, count in sorted(collaboration_patterns.items(), key=lambda x: x[1], reverse=True):
            print(f"  {pattern}: {count} agents")
    
    def demo_5_intelligent_routing(self):
        """Demo 5: Intelligent query routing to best agent"""
        print("\n" + "-"*80)
        print("📍 DEMO 5: Intelligent Query Routing")
        print("-"*80)
        
        queries = [
            "How do I implement authentication in Django?",
            "What's the best way to optimize Kubernetes pods?",
            "I need help with React Native navigation",
            "How do I set up CI/CD with GitHub Actions?"
        ]
        
        print("\n🎯 Routing queries to best-matched agents:")
        
        for query in queries:
            print(f"\n💬 Query: {query}")
            
            # Simple keyword matching for demo
            query_lower = query.lower()
            best_agent = None
            best_score = 0
            
            for agent in self.agents[:100]:  # Check first 100
                metadata = agent.get("enhanced_metadata", {})
                
                # Check skills and keywords
                skills = " ".join(metadata.get("capabilities", {}).get("primary_expertise", [])).lower()
                keywords = " ".join(metadata.get("discovery", {}).get("keywords", [])).lower()
                
                score = 0
                if "django" in query_lower and "django" in skills:
                    score += 10
                if "kubernetes" in query_lower and "kubernetes" in skills:
                    score += 10
                if "react native" in query_lower and "react" in skills and "mobile" in keywords:
                    score += 10
                if "github actions" in query_lower and ("ci/cd" in skills or "cicd" in keywords):
                    score += 10
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                metadata = best_agent["enhanced_metadata"]
                print(f"   → Routed to: {metadata['avatar_emoji']} {metadata['display_name']}")
                print(f"     Expertise: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
    
    def demo_6_performance_test(self):
        """Demo 6: Test platform performance"""
        print("\n" + "-"*80)
        print("📍 DEMO 6: Platform Performance Test")
        print("-"*80)
        
        print("\n⚡ Testing agent creation and query speed...")
        
        # Test 1: Agent creation speed
        start_time = time.time()
        test_agents = []
        
        for i in range(10):
            agent_data = self.agents[i]
            agent = Agent(
                name=agent_data["enhanced_metadata"]["display_name"],
                instructions=agent_data["instructions"],
                model="gpt-4o-mini"
            )
            test_agents.append(agent)
        
        creation_time = time.time() - start_time
        print(f"\n✅ Created 10 agents in {creation_time:.2f} seconds")
        print(f"   Average: {creation_time/10:.3f} seconds per agent")
        
        # Test 2: Metadata search speed
        start_time = time.time()
        
        # Search for specific skills
        results = []
        search_terms = ["Python", "React", "Kubernetes", "PostgreSQL", "Security"]
        
        for term in search_terms:
            matches = []
            for agent in self.agents:
                skills = agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])
                if term in skills:
                    matches.append(agent)
            results.append((term, len(matches)))
        
        search_time = time.time() - start_time
        print(f"\n✅ Searched 1000 agents for 5 skills in {search_time:.3f} seconds")
        
        for term, count in results:
            print(f"   {term}: {count} agents found")


def main():
    """Run all demos"""
    demo = AgentVerseDemo()
    
    demos = [
        demo.demo_1_simple_chat,
        demo.demo_2_skill_based_discovery,
        demo.demo_3_multi_agent_collaboration,
        demo.demo_4_agent_network_visualization,
        demo.demo_5_intelligent_routing,
        demo.demo_6_performance_test
    ]
    
    for demo_func in demos:
        demo_func()
        input("\n➡️  Press Enter to continue to next demo...")
    
    print("\n" + "="*80)
    print("✨ AgentVerse Demo Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
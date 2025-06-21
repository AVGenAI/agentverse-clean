#!/usr/bin/env python3
"""
Interactive AgentVerse Demo - Try different features
"""
import os
import json
import random
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key

load_dotenv()

class InteractiveAgentVerseDemo:
    def __init__(self):
        # Load agents
        with open("src/config/agentverse_agents_1000.json", 'r') as f:
            self.agents = json.load(f)
        
        # Set API key if available
        if os.getenv("OPENAI_API_KEY"):
            set_default_openai_key(os.getenv("OPENAI_API_KEY"))
            self.api_available = True
        else:
            self.api_available = False
        
        self.show_banner()
    
    def show_banner(self):
        """Show AgentVerse banner"""
        print("\n" + "="*80)
        print("""
    🌌  A G E N T V E R S E  🌌
    
    Where 1000 AI Agents Discover & Collaborate
        """)
        print("="*80)
        print(f"✅ Loaded {len(self.agents)} agents")
        if not self.api_available:
            print("⚠️  No OpenAI API key - Chat features disabled")
    
    def show_menu(self):
        """Show interactive menu"""
        print("\n🌟 AGENTVERSE FEATURES:")
        print("-" * 50)
        print("1. 🔍 Search agents by skill")
        print("2. 🎲 Meet a random agent")
        print("3. 👥 Assemble a project team")
        print("4. 🌐 Explore agent domains")
        print("5. 🤝 Find collaboration partners")
        print("6. 💬 Chat with an agent (requires API key)")
        print("7. 📊 View platform statistics")
        print("8. 🚀 Quick demo of all features")
        print("0. 🚪 Exit")
        print("-" * 50)
    
    def search_by_skill(self):
        """Search agents by skill"""
        skill = input("\n🔍 Enter skill to search for: ").strip()
        
        matches = []
        for agent in self.agents:
            skills = agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])
            if any(skill.lower() in s.lower() for s in skills):
                matches.append(agent)
        
        print(f"\n📋 Found {len(matches)} agents with '{skill}' skills:")
        
        for agent in matches[:10]:
            metadata = agent["enhanced_metadata"]
            print(f"\n  {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"     ID: {metadata['canonical_name']}")
            print(f"     Skills: {', '.join(metadata['capabilities']['primary_expertise'])}")
        
        if len(matches) > 10:
            print(f"\n  ... and {len(matches) - 10} more")
    
    def meet_random_agent(self):
        """Meet a random agent"""
        agent = random.choice(self.agents)
        metadata = agent["enhanced_metadata"]
        
        print(f"\n🎲 Meet: {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"\n🆔 AgentVerse ID: {metadata['canonical_name']}")
        print(f"🎯 Primary Skills: {', '.join(metadata['capabilities']['primary_expertise'])}")
        print(f"🛠️ Tools: {', '.join(list(metadata['capabilities']['tools_mastery'].keys())[:3])}")
        print(f"🤝 Collaboration Style: {', '.join(metadata['collaboration']['style'])}")
        print(f"⚡ Performance: {metadata['performance']['complexity']} complexity handling")
        print(f"🏆 Trust Score: {metadata['quality']['trust_score']}")
        
        # Show a bit of their instructions
        instructions = agent.get("instructions", "")
        print(f"\n📝 About: {instructions[:200]}...")
    
    def assemble_team(self):
        """Assemble a project team"""
        print("\n👥 PROJECT TEAM ASSEMBLY")
        print("\nSelect project type:")
        print("1. E-commerce Platform")
        print("2. Mobile Banking App")
        print("3. Data Analytics Dashboard")
        print("4. DevOps Infrastructure")
        print("5. AI Chatbot System")
        
        choice = input("\nSelect (1-5): ").strip()
        
        project_roles = {
            "1": [("Frontend Dev", ["React", "E-commerce"]), 
                  ("Backend Dev", ["Python", "API"]),
                  ("Database Expert", ["PostgreSQL", "Performance"]),
                  ("Payment Specialist", ["Payment", "Security"])],
            "2": [("Mobile Dev", ["React Native", "Mobile"]),
                  ("Backend Dev", ["Security", "API"]),
                  ("Security Expert", ["Security", "Authentication"]),
                  ("UX Designer", ["UI/UX", "Mobile"])],
            "3": [("Frontend Dev", ["Dashboard", "Data Visualization"]),
                  ("Data Engineer", ["ETL", "Data Pipeline"]),
                  ("Analytics Expert", ["Analytics", "Business Intelligence"]),
                  ("DevOps", ["Deployment", "Monitoring"])],
            "4": [("DevOps Engineer", ["Kubernetes", "Docker"]),
                  ("SRE", ["Monitoring", "Reliability"]),
                  ("Security Engineer", ["Security", "Infrastructure"]),
                  ("Automation Expert", ["Automation", "CI/CD"])],
            "5": [("AI Engineer", ["NLP", "Machine Learning"]),
                  ("Backend Dev", ["Python", "API"]),
                  ("Frontend Dev", ["Chat", "React"]),
                  ("Data Scientist", ["Model Training", "Analytics"])]
        }
        
        roles = project_roles.get(choice, project_roles["1"])
        
        print("\n🤖 Assembling team...")
        team = []
        
        for role_name, keywords in roles:
            best_agent = None
            best_score = 0
            
            for agent in self.agents:
                skills = " ".join(agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])).lower()
                score = sum(2 if keyword.lower() in skills else 0 for keyword in keywords)
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
            
            if best_agent:
                team.append((role_name, best_agent))
        
        print("\n✅ Your Dream Team:")
        for role, agent in team:
            metadata = agent["enhanced_metadata"]
            print(f"\n  {role}:")
            print(f"    {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"    Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
            print(f"    Trust Score: {metadata['quality']['trust_score']}")
    
    def explore_domains(self):
        """Explore agent domains"""
        domains = {}
        
        for agent in self.agents:
            canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "")
            if "." in canonical:
                parts = canonical.split(".")
                domain = parts[1]
                subdomain = parts[2] if len(parts) > 2 else "general"
                
                if domain not in domains:
                    domains[domain] = {}
                if subdomain not in domains[domain]:
                    domains[domain][subdomain] = 0
                domains[domain][subdomain] += 1
        
        print("\n🌐 AGENTVERSE DOMAINS:")
        print("-" * 50)
        
        for domain, subdomains in sorted(domains.items()):
            total = sum(subdomains.values())
            print(f"\n📁 agentverse.{domain}.*  ({total} agents)")
            
            for subdomain, count in sorted(subdomains.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   └─ {subdomain}: {count} agents")
    
    def find_collaborators(self):
        """Find collaboration partners for an agent"""
        search = input("\n🔍 Enter agent name or skill to find collaborators for: ").strip()
        
        # Find matching agent
        target_agent = None
        for agent in self.agents:
            name = agent.get("enhanced_metadata", {}).get("display_name", "").lower()
            if search.lower() in name:
                target_agent = agent
                break
        
        if not target_agent:
            print(f"❌ No agent found matching '{search}'")
            return
        
        metadata = target_agent["enhanced_metadata"]
        print(f"\n🤖 Finding collaborators for: {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"🆔 ID: {metadata['canonical_name']}")
        
        # Find collaborators based on upstream dependencies
        print("\n🤝 Recommended Collaborators:")
        
        collab_count = 0
        for pattern in metadata.get("network", {}).get("upstream", []):
            if "." in pattern:
                domain = pattern.split(".")[1]
                
                # Find agents in that domain
                for agent in self.agents:
                    if domain in agent.get("enhanced_metadata", {}).get("canonical_name", "") and collab_count < 5:
                        collab_meta = agent["enhanced_metadata"]
                        print(f"\n  {collab_meta['avatar_emoji']} {collab_meta['display_name']}")
                        print(f"     Reason: {domain} specialist")
                        print(f"     Skills: {', '.join(collab_meta['capabilities']['primary_expertise'][:3])}")
                        collab_count += 1
    
    def chat_with_agent(self):
        """Chat with a specific agent"""
        if not self.api_available:
            print("\n❌ OpenAI API key not found. Please set OPENAI_API_KEY in .env file")
            return
        
        name = input("\n🔍 Enter agent name to chat with: ").strip()
        
        # Find agent
        target_agent = None
        for agent in self.agents:
            agent_name = agent.get("enhanced_metadata", {}).get("display_name", "").lower()
            if name.lower() in agent_name:
                target_agent = agent
                break
        
        if not target_agent:
            print(f"❌ No agent found matching '{name}'")
            return
        
        metadata = target_agent["enhanced_metadata"]
        print(f"\n💬 Starting chat with: {metadata['avatar_emoji']} {metadata['display_name']}")
        print(f"🎯 Skills: {', '.join(metadata['capabilities']['primary_expertise'])}")
        print("Type 'exit' to end chat")
        print("-" * 50)
        
        # Create agent
        agent = Agent(
            name=metadata['display_name'],
            instructions=target_agent['instructions'],
            model="gpt-4o-mini"
        )
        
        while True:
            query = input("\nYou: ").strip()
            if query.lower() == 'exit':
                break
            
            result = Runner.run_sync(agent, query)
            print(f"\n{metadata['display_name']}: {result.final_output}")
    
    def show_statistics(self):
        """Show platform statistics"""
        print("\n📊 AGENTVERSE STATISTICS")
        print("-" * 50)
        
        # Count by category
        categories = {}
        skills_count = {}
        collaboration_styles = {}
        
        for agent in self.agents:
            # Category
            cat = agent.get("category", "Unknown")
            categories[cat] = categories.get(cat, 0) + 1
            
            # Skills
            for skill in agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", []):
                skills_count[skill] = skills_count.get(skill, 0) + 1
            
            # Collaboration styles
            for style in agent.get("enhanced_metadata", {}).get("collaboration", {}).get("style", []):
                collaboration_styles[style] = collaboration_styles.get(style, 0) + 1
        
        print(f"\n📈 Total Agents: {len(self.agents)}")
        
        print("\n📂 By Category:")
        for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {cat}: {count} agents")
        
        print("\n🏆 Top 10 Skills:")
        for skill, count in sorted(skills_count.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  • {skill}: {count} agents")
        
        print("\n🤝 Collaboration Styles:")
        for style, count in sorted(collaboration_styles.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {style}: {count} agents")
    
    def quick_demo(self):
        """Run a quick demo of all features"""
        print("\n🚀 QUICK DEMO - Showing all features")
        
        # 1. Random agent
        print("\n1️⃣ Random Agent:")
        agent = random.choice(self.agents)
        metadata = agent["enhanced_metadata"]
        print(f"  {metadata['avatar_emoji']} {metadata['display_name']} - {', '.join(metadata['capabilities']['primary_expertise'][:2])}")
        
        # 2. Top domains
        print("\n2️⃣ Top Domains:")
        domains = {}
        for agent in self.agents:
            domain = agent.get("enhanced_metadata", {}).get("canonical_name", "").split(".")[1] if "." in agent.get("enhanced_metadata", {}).get("canonical_name", "") else "unknown"
            domains[domain] = domains.get(domain, 0) + 1
        
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • agentverse.{domain}.*: {count} agents")
        
        # 3. Quick team
        print("\n3️⃣ Quick Team for Web App:")
        
        # Define role mappings to actual skills/keywords
        role_mappings = {
            "Frontend": ["React", "Vue", "Angular", "frontend"],
            "Backend": ["Django", "FastAPI", "Express", "backend", "API Design"],
            "Database": ["PostgreSQL", "MySQL", "MongoDB", "Database"],
            "DevOps": ["Docker", "Kubernetes", "CI/CD", "devops", "Deployment"]
        }
        
        for role, keywords in role_mappings.items():
            # Find agents matching any of the keywords
            matching_agents = []
            for agent in self.agents:
                agent_skills = " ".join(agent.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", [])).lower()
                agent_canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "").lower()
                
                if any(keyword.lower() in agent_skills or keyword.lower() in agent_canonical for keyword in keywords):
                    matching_agents.append(agent)
            
            if matching_agents:
                # Pick one randomly from first 10 matches
                agent = random.choice(matching_agents[:10])
                metadata = agent["enhanced_metadata"]
                print(f"  • {role}: {metadata['avatar_emoji']} {metadata['display_name']}")
            else:
                print(f"  • {role}: No specialist found")
        
        print("\n✨ Demo complete! Try the full features from the menu.")
    
    def run(self):
        """Run interactive demo"""
        while True:
            self.show_menu()
            choice = input("\n👉 Select option (0-8): ").strip()
            
            if choice == "0":
                print("\n👋 Thanks for exploring AgentVerse!")
                break
            elif choice == "1":
                self.search_by_skill()
            elif choice == "2":
                self.meet_random_agent()
            elif choice == "3":
                self.assemble_team()
            elif choice == "4":
                self.explore_domains()
            elif choice == "5":
                self.find_collaborators()
            elif choice == "6":
                self.chat_with_agent()
            elif choice == "7":
                self.show_statistics()
            elif choice == "8":
                self.quick_demo()
            else:
                print("❌ Invalid option")
            
            input("\n➡️  Press Enter to continue...")


def main():
    demo = InteractiveAgentVerseDemo()
    demo.run()


if __name__ == "__main__":
    main()
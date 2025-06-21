#!/usr/bin/env python3
"""
Rebrand project to Agent Verse (AV)
"""
import json
import os
import re


def update_agent_metadata():
    """Update agent metadata with AgentVerse branding"""
    
    # Load enhanced agents
    with open("src/config/1000_agents_enhanced.json", 'r') as f:
        agents = json.load(f)
    
    print("🌌 Rebranding to AgentVerse...")
    
    # Update each agent
    for agent in agents:
        # Update canonical names from aiagents to agentverse
        if "enhanced_metadata" in agent:
            metadata = agent["enhanced_metadata"]
            
            # Update canonical name
            old_canonical = metadata.get("canonical_name", "")
            new_canonical = old_canonical.replace("aiagents.", "agentverse.")
            metadata["canonical_name"] = new_canonical
            
            # Add AgentVerse branding to network
            metadata["network"]["agentverse_verified"] = True
            metadata["network"]["agentverse_version"] = "1.0.0"
            
            # Update quality badges
            if "badges" in metadata["quality"]:
                metadata["quality"]["badges"].append("agentverse-certified")
            
            # Update instructions with AgentVerse branding
            agentverse_branding = f"\n\n🌌 AgentVerse Certified Agent"
            agentverse_branding += f"\n🆔 AgentVerse ID: {new_canonical}"
            
            # Replace old branding in instructions
            instructions = agent.get("instructions", "")
            instructions = instructions.replace("🤖 Agent ID:", "🌌 AgentVerse ID:")
            instructions = instructions.replace("aiagents.", "agentverse.")
            
            # Add AgentVerse branding if not present
            if "AgentVerse" not in instructions:
                agent["instructions"] = instructions + agentverse_branding
    
    # Save updated agents
    with open("src/config/agentverse_agents_1000.json", 'w') as f:
        json.dump(agents, f, indent=2)
    
    print("✅ Updated agent metadata with AgentVerse branding")
    return agents


def create_agentverse_branding_files():
    """Create AgentVerse branding files"""
    
    # Create AgentVerse README
    agentverse_readme = """# 🌌 AgentVerse

<div align="center">
  <h1>🌌 AGENTVERSE</h1>
  <h3>A Universe of 1000+ AI Agents</h3>
  <p><em>Where AI Agents Discover, Collaborate, and Create Together</em></p>
</div>

---

## 🚀 Welcome to AgentVerse

AgentVerse is a comprehensive AI agent ecosystem featuring:

- **1000+ Specialized Agents** across engineering, business, DevOps, and more
- **Intelligent Discovery** with rich metadata and taxonomy
- **Seamless Collaboration** between agents
- **OpenAI Agents SDK** powered
- **Multi-Provider Support** (OpenAI, Ollama, vLLM)

## 🌟 Key Features

### 🤖 Diverse Agent Population
- 250 Engineering Agents
- 200 Business Workflow Agents
- 150 SRE/DevOps Agents
- 100 ServiceNow Agents
- 100 Data & Analytics Agents
- 50 Security Agents
- 50 Customer Support Agents
- 50 Project Management Agents
- 50 Quality Assurance Agents

### 🔍 Smart Discovery
Each AgentVerse agent has:
- **Unique AgentVerse ID**: `agentverse.domain.subdomain.specialty`
- **Rich Metadata**: Skills, tools, capabilities
- **Collaboration Profiles**: How they work with others
- **Performance Metrics**: Response times, reliability

### 🤝 Intelligent Collaboration
- Automatic partner discovery
- Skill-based team assembly
- Dependency management
- Workflow orchestration

## 🎯 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Explore AgentVerse agents
python agentverse_explorer.py --list-domains

# Chat with an agent
python agentverse_chat.py --agent "agentverse.engineering.frontend.react"

# Discover collaborators
python agentverse_discover.py --skill "kubernetes"

# Assemble a team
python agentverse_team.py --project "e-commerce"
```

## 🌐 AgentVerse Domains

- `agentverse.engineering.*` - Software development agents
- `agentverse.business.*` - Business process agents  
- `agentverse.sre.*` - Site reliability & DevOps
- `agentverse.data.*` - Data & analytics specialists
- `agentverse.security.*` - Security experts
- `agentverse.support.*` - Customer support agents
- `agentverse.qa.*` - Quality assurance specialists

## 📡 AgentVerse Protocol

Agents communicate using the AgentVerse Protocol:

```json
{
  "agentverse_id": "agentverse.engineering.backend.python",
  "message": "I need database optimization help",
  "seeking": ["agentverse.engineering.database.*"],
  "context": {...}
}
```

## 🛠️ Building with AgentVerse

```python
from agentverse import AgentVerse, AgentVerseAgent

# Initialize AgentVerse
agentverse = AgentVerse()

# Get an agent
agent = agentverse.get_agent("agentverse.engineering.frontend.react")

# Find collaborators
partners = av.find_collaborators(agent, skill="api design")

# Assemble a team
team = av.assemble_team(project_type="full-stack")
```

## 🎨 AgentVerse UI (Coming Soon)

- Visual agent explorer
- Drag-and-drop team builder
- Real-time collaboration viewer
- Performance dashboards

## 🌌 Join AgentVerse

Welcome to a universe where AI agents work together seamlessly!

---

<div align="center">
  <p>Built with ❤️ by the AgentVerse Team</p>
  <p>🌌 AgentVerse - Where AI Collaboration Happens</p>
</div>
"""
    
    with open("README_AGENTVERSE.md", 'w') as f:
        f.write(agentverse_readme)
    
    # Create AgentVerse configuration
    agentverse_config = {
        "name": "AgentVerse",
        "version": "1.0.0",
        "short_name": "AgentVerse",
        "tagline": "A Universe of AI Agents",
        "domains": {
            "engineering": "Software Development",
            "business": "Business Workflows", 
            "sre": "Site Reliability Engineering",
            "data": "Data & Analytics",
            "security": "Security & Compliance",
            "support": "Customer Support",
            "qa": "Quality Assurance",
            "servicenow": "ServiceNow Platform",
            "project": "Project Management"
        },
        "branding": {
            "primary_color": "#6B46C1",  # Purple (space/universe theme)
            "secondary_color": "#9333EA",
            "accent_color": "#A78BFA",
            "logo_emoji": "🌌",
            "agent_emoji": "🤖"
        },
        "api": {
            "base_url": "http://localhost:8000/agentverse/api/v1",
            "websocket": "ws://localhost:8000/agentverse/ws"
        }
    }
    
    with open("agentverse_config.json", 'w') as f:
        json.dump(agentverse_config, f, indent=2)
    
    print("✅ Created AgentVerse branding files")


def create_agentverse_scripts():
    """Create AgentVerse-branded scripts"""
    
    # AgentVerse Explorer script
    agentverse_explorer = '''#!/usr/bin/env python3
"""
AgentVerse Explorer - Discover and interact with AgentVerse agents
"""
import json
import argparse
from typing import List, Dict, Any

class AgentVerseExplorer:
    def __init__(self):
        # Load AgentVerse agents
        with open("src/config/agentverse_agents_1000.json", 'r') as f:
            self.agents = json.load(f)
        
        print("\\n🌌 Welcome to AgentVerse")
        print("   A Universe of {} AI Agents\\n".format(len(self.agents)))
    
    def list_domains(self):
        """List all AgentVerse domains"""
        domains = {}
        for agent in self.agents:
            domain = agent.get("enhanced_metadata", {}).get("canonical_name", "").split(".")[1]
            if domain:
                domains[domain] = domains.get(domain, 0) + 1
        
        print("🌐 AgentVerse Domains:")
        print("-" * 40)
        for domain, count in sorted(domains.items()):
            print(f"  agentverse.{domain}.*  →  {count} agents")
    
    def search_agents(self, query: str):
        """Search for agents"""
        results = []
        query_lower = query.lower()
        
        for agent in self.agents:
            metadata = agent.get("enhanced_metadata", {})
            if (query_lower in metadata.get("display_name", "").lower() or
                query_lower in str(metadata.get("capabilities", {})).lower()):
                results.append(agent)
        
        print(f"\\n🔍 Found {len(results)} agents matching '{query}':")
        for agent in results[:10]:
            metadata = agent["enhanced_metadata"]
            print(f"\\n  {metadata['avatar_emoji']} {metadata['display_name']}")
            print(f"     AgentVerse ID: {metadata['canonical_name']}")
            print(f"     Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")

def main():
    parser = argparse.ArgumentParser(description="Explore AgentVerse")
    parser.add_argument("--list-domains", action="store_true", help="List all AgentVerse domains")
    parser.add_argument("--search", "-s", help="Search for agents")
    parser.add_argument("--agent", "-a", help="Get details for specific agent")
    
    args = parser.parse_args()
    explorer = AgentVerseExplorer()
    
    if args.list_domains:
        explorer.list_domains()
    elif args.search:
        explorer.search_agents(args.search)
    else:
        explorer.list_domains()

if __name__ == "__main__":
    main()
'''
    
    with open("agentverse_explorer.py", 'w') as f:
        f.write(agentverse_explorer)
    
    # AgentVerse Chat script
    agentverse_chat = '''#!/usr/bin/env python3
"""
AgentVerse Chat - Chat with any AgentVerse agent
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, set_default_openai_key
import json
import argparse

load_dotenv()

def chat_with_agentverse_agent(agentverse_id: str):
    """Chat with an AgentVerse agent"""
    # Load AgentVerse agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)
    
    # Find agent by AgentVerse ID
    agent_data = None
    for agent in agents:
        if agent.get("enhanced_metadata", {}).get("canonical_name") == agentverse_id:
            agent_data = agent
            break
    
    if not agent_data:
        print(f"❌ Agent '{agentverse_id}' not found in AgentVerse")
        return
    
    # Set up OpenAI
    if os.getenv("OPENAI_API_KEY"):
        set_default_openai_key(os.getenv("OPENAI_API_KEY"))
    else:
        print("❌ No OpenAI API key found")
        return
    
    # Create agent
    metadata = agent_data["enhanced_metadata"]
    agent = Agent(
        name=metadata["display_name"],
        instructions=agent_data["instructions"],
        model="gpt-4o-mini"
    )
    
    print(f"\\n🌌 Welcome to AgentVerse Chat")
    print(f"💬 Chatting with: {metadata['avatar_emoji']} {metadata['display_name']}")
    print(f"🆔 AgentVerse ID: {metadata['canonical_name']}")
    print(f"🎯 Skills: {', '.join(metadata['capabilities']['primary_expertise'][:3])}")
    print("\\nType 'exit' to quit")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\\nYou: ").strip()
            if user_input.lower() == 'exit':
                print("\\n👋 Leaving AgentVerse. See you soon!")
                break
            
            result = Runner.run_sync(agent, user_input)
            print(f"\\n{metadata['display_name']}: {result.final_output}")
            
        except KeyboardInterrupt:
            print("\\n\\n👋 Leaving AgentVerse. See you soon!")
            break

def main():
    parser = argparse.ArgumentParser(description="Chat with AgentVerse agents")
    parser.add_argument("--agent", "-a", required=True, help="AgentVerse agent ID (e.g., agentverse.engineering.frontend.react)")
    
    args = parser.parse_args()
    chat_with_agentverse_agent(args.agent)

if __name__ == "__main__":
    main()
'''
    
    with open("agentverse_chat.py", 'w') as f:
        f.write(agentverse_chat)
    
    print("✅ Created AgentVerse scripts")
    
    # Make scripts executable
    os.chmod("agentverse_explorer.py", 0o755)
    os.chmod("agentverse_chat.py", 0o755)


def update_project_structure():
    """Update project structure for AgentVerse"""
    
    # Create AgentVerse directories
    agentverse_dirs = [
        "agentverse_core",
        "agentverse_api", 
        "agentverse_ui",
        "agentverse_agents",
        "agentverse_discovery"
    ]
    
    for dir_name in agentverse_dirs:
        os.makedirs(dir_name, exist_ok=True)
        # Create __init__.py
        with open(f"{dir_name}/__init__.py", 'w') as f:
            f.write(f'"""AgentVerse - {dir_name.replace("_", " ").title()}"""')
    
    print("✅ Created AgentVerse directory structure")


def create_agentverse_logo():
    """Create ASCII art logo for AgentVerse"""
    
    logo = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║           🌌  A G E N T V E R S E  🌌                         ║
    ║                                                               ║
    ║      ╔═╗╔═╗╔═╗╔╗╔╔╦╗╦  ╦╔═╗╦═╗╔═╗╔═╗                         ║
    ║      ╠═╣║ ╦║╣ ║║║ ║ ╚╗╔╝║╣ ╠╦╝╚═╗║╣                          ║
    ║      ╩ ╩╚═╝╚═╝╝╚╝ ╩  ╚╝ ╚═╝╩╚═╚═╝╚═╝                         ║
    ║                                                               ║
    ║         Where AI Agents Discover & Collaborate                ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    
    with open("agentverse_logo.txt", 'w') as f:
        f.write(logo)
    
    print("✅ Created AgentVerse logo")


def main():
    print("\n🌌 Rebranding to AgentVerse...")
    print("="*50)
    
    # Update agent metadata
    agents = update_agent_metadata()
    
    # Create branding files
    create_agentverse_branding_files()
    
    # Create AgentVerse scripts
    create_agentverse_scripts()
    
    # Update project structure
    update_project_structure()
    
    # Create logo
    create_agentverse_logo()
    
    print("\n" + "="*50)
    print("✨ Rebranding Complete!")
    print("\n🌌 Welcome to AgentVerse")
    print("   A Universe of {} AI Agents".format(len(agents)))
    print("\nNext steps:")
    print("  1. Explore agents: python agentverse_explorer.py")
    print("  2. Chat with agents: python agentverse_chat.py --agent agentverse.engineering.frontend.react")
    print("  3. Read docs: cat README_AGENTVERSE.md")
    print("="*50)


if __name__ == "__main__":
    main()
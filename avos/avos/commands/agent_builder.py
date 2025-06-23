"""
Advanced Agent Builder for A\V OS
"""
import json
import uuid
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.syntax import Syntax
import aiohttp

console = Console()
API_BASE = "http://localhost:8000"

class AgentBuilder:
    """Interactive agent builder with full configuration"""
    
    def __init__(self):
        self.agent_config = {}
        
    async def build_agent(
        self,
        name: str,
        system_prompt: str = None,
        llm_model: str = None,
        mcp_server: str = None,
        domain: str = None,
        tools: list = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        interactive: bool = False
    ):
        """Build a complete agent with all configurations"""
        
        console.print(f"\n[bold cyan]🔨 A\V OS Agent Builder[/bold cyan]")
        console.print(f"Building agent: [yellow]{name}[/yellow]\n")
        
        # Generate agent ID
        agent_id = f"{domain or 'custom'}_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        # Interactive mode
        if interactive:
            system_prompt = system_prompt or Prompt.ask("System prompt", default="You are a helpful AI assistant")
            llm_model = llm_model or Prompt.ask("LLM Model", choices=["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-3", "llama3"], default="gpt-4o-mini")
            domain = domain or Prompt.ask("Domain", choices=["sre", "devops", "data", "engineering", "security", "healthcare", "finance", "custom"], default="custom")
            temperature = float(Prompt.ask("Temperature (0.0-1.0)", default="0.7"))
            max_tokens = int(Prompt.ask("Max tokens", default="2000"))
            
            # Tools selection
            if Confirm.ask("Add tools to this agent?"):
                console.print("\nAvailable tool categories:")
                console.print("1. SRE Tools (incidents, SLO, runbooks)")
                console.print("2. Data Tools (analysis, visualization)")
                console.print("3. DevOps Tools (deployment, monitoring)")
                console.print("4. Custom Tools")
                
                tool_choice = Prompt.ask("Select tool category", choices=["1", "2", "3", "4"])
                tools = self._get_tools_for_category(tool_choice)
                
            # MCP selection
            if Confirm.ask("Connect to MCP server?"):
                mcp_server = Prompt.ask("MCP Server", choices=["servicenow", "postgresql", "mongodb", "prometheus", "custom"])
        
        # Build agent configuration
        self.agent_config = {
            "id": agent_id,
            "name": name,
            "type": "specialist",
            "domain": domain or "custom",
            "version": "1.0.0",
            "status": "active",
            "instructions": system_prompt or f"You are {name}, a helpful AI assistant.",
            "model_preferences": {
                "primary": llm_model or "gpt-4o-mini",
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            "capabilities": {
                "primary_expertise": self._derive_expertise(domain, system_prompt),
                "tools_mastery": {}
            },
            "tools": tools or [],
            "mcp_server": mcp_server,
            "enhanced_metadata": {
                "agent_uuid": agent_id,
                "canonical_name": f"avos.{domain or 'custom'}.{agent_id}",
                "display_name": name,
                "avatar": self._get_avatar(domain),
                "trust_score": 0.80,
                "created_by": "A\V OS Agent Builder",
                "created_at": datetime.now().isoformat()
            }
        }
        
        # Display configuration
        console.print("\n[bold green]Agent Configuration:[/bold green]")
        config_json = json.dumps(self.agent_config, indent=2)
        syntax = Syntax(config_json, "json", theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title="Agent Config", border_style="green"))
        
        # Confirm creation
        if interactive and not Confirm.ask("\nCreate this agent?"):
            console.print("[red]Agent creation cancelled[/red]")
            return None
            
        # Save agent
        success = await self._save_agent()
        
        if success:
            console.print(f"\n[bold green]✅ Agent '{name}' created successfully![/bold green]")
            console.print(f"[dim]Agent ID: {agent_id}[/dim]")
            
            # Connect to MCP if specified
            if mcp_server:
                console.print(f"\n[yellow]Connecting to MCP server '{mcp_server}'...[/yellow]")
                await self._connect_mcp(agent_id, mcp_server)
                
            # Test the agent
            if Confirm.ask("\nTest the agent now?"):
                await self._test_agent(agent_id)
                
            return agent_id
        else:
            console.print("[red]Failed to create agent[/red]")
            return None
    
    def _get_tools_for_category(self, category: str) -> list:
        """Get tools based on category selection"""
        tools_map = {
            "1": ["search_incidents", "create_incident", "update_incident", "calculate_slo_status", "get_runbook"],
            "2": ["analyze_data", "visualize_data", "export_report", "statistical_analysis"],
            "3": ["deploy_service", "check_health", "rollback", "scale_service", "view_logs"],
            "4": []
        }
        return tools_map.get(category, [])
    
    def _derive_expertise(self, domain: str, prompt: str) -> list:
        """Derive expertise from domain and prompt"""
        expertise_map = {
            "sre": ["Incident Response", "Monitoring", "SLO Management"],
            "devops": ["CI/CD", "Infrastructure", "Automation"],
            "data": ["Data Analysis", "Machine Learning", "Visualization"],
            "engineering": ["Software Development", "Architecture", "Code Review"],
            "security": ["Security Analysis", "Compliance", "Threat Detection"],
            "healthcare": ["Medical Knowledge", "Patient Care", "HIPAA Compliance"],
            "finance": ["Financial Analysis", "Risk Management", "Compliance"]
        }
        
        base_expertise = expertise_map.get(domain, ["General Assistant"])
        
        # Add expertise based on prompt keywords
        if prompt:
            prompt_lower = prompt.lower()
            if "python" in prompt_lower:
                base_expertise.append("Python")
            if "kubernetes" in prompt_lower or "k8s" in prompt_lower:
                base_expertise.append("Kubernetes")
            if "database" in prompt_lower or "sql" in prompt_lower:
                base_expertise.append("Database Management")
                
        return base_expertise[:5]  # Limit to 5 expertise areas
    
    def _get_avatar(self, domain: str) -> str:
        """Get avatar emoji based on domain"""
        avatars = {
            "sre": "🚨",
            "devops": "🔧",
            "data": "📊",
            "engineering": "💻",
            "security": "🔒",
            "healthcare": "🏥",
            "finance": "💰",
            "custom": "🤖"
        }
        return avatars.get(domain, "🤖")
    
    async def _save_agent(self) -> bool:
        """Save agent to the system"""
        # For now, save to a local file
        # In production, this would save to the database
        try:
            agents_file = "src/config/avos_agents.json"
            
            # Load existing agents
            try:
                with open(agents_file, "r") as f:
                    agents = json.load(f)
            except:
                agents = []
            
            # Add new agent
            agents.append(self.agent_config)
            
            # Save back
            with open(agents_file, "w") as f:
                json.dump(agents, f, indent=2)
                
            return True
        except Exception as e:
            console.print(f"[red]Error saving agent: {e}[/red]")
            return False
    
    async def _connect_mcp(self, agent_id: str, mcp_server: str):
        """Connect agent to MCP server"""
        async with aiohttp.ClientSession() as session:
            try:
                data = {
                    "agentId": agent_id,
                    "serverId": mcp_server
                }
                
                async with session.post(f"{API_BASE}/api/mcp/couplings", json=data) as resp:
                    if resp.status == 200:
                        console.print(f"[green]✅ Connected to {mcp_server}[/green]")
                    else:
                        console.print(f"[yellow]⚠️  MCP connection pending[/yellow]")
            except Exception as e:
                console.print(f"[red]MCP connection error: {e}[/red]")
    
    async def _test_agent(self, agent_id: str):
        """Test the newly created agent"""
        console.print(f"\n[cyan]Testing agent '{agent_id}'...[/cyan]")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Create session
                async with session.post(f"{API_BASE}/chat/session?agent_id={agent_id}") as resp:
                    if resp.status != 200:
                        console.print("[red]Failed to start test session[/red]")
                        return
                        
                    session_data = await resp.json()
                    session_id = session_data['session_id']
                
                # Send test message
                test_message = "Hello! Please introduce yourself and explain your capabilities."
                data = {
                    "session_id": session_id,
                    "agent_id": agent_id,
                    "message": test_message
                }
                
                async with session.post(f"{API_BASE}/chat/message", json=data) as resp:
                    result = await resp.json()
                    response = result.get('response', 'No response')
                    
                    console.print(f"\n[bold green]Agent Response:[/bold green]")
                    console.print(Panel(response, border_style="green"))
                    
            except Exception as e:
                console.print(f"[red]Test failed: {e}[/red]")
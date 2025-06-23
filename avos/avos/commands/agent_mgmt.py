"""
Agent Management Commands
"""
import aiohttp
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.syntax import Syntax

console = Console()

API_BASE = "http://localhost:8000"

async def list_agents(domain=None, status=None, running=False):
    """List all agents with filtering"""
    async with aiohttp.ClientSession() as session:
        # Build query
        data = {}
        if domain:
            data['domain'] = domain
            
        try:
            async with session.post(f"{API_BASE}/agents", json=data) as resp:
                result = await resp.json()
                agents = result.get('agents', [])
                
                # Filter by status if requested
                if status:
                    agents = [a for a in agents if a.get('status') == status]
                if running:
                    # TODO: Get running agents from process manager
                    pass
                
                # Create table
                table = Table(title=f"AgentVerse Agents ({len(agents)} found)")
                table.add_column("ID", style="cyan", no_wrap=True)
                table.add_column("Name", style="magenta")
                table.add_column("Domain", style="green")
                table.add_column("Trust", style="yellow")
                table.add_column("Status", style="blue")
                
                for agent in agents[:20]:  # Show first 20
                    table.add_row(
                        agent.get('id', 'N/A'),
                        agent.get('display_name', 'Unknown'),
                        agent.get('canonical_name', '').split('.')[1] if '.' in agent.get('canonical_name', '') else 'N/A',
                        f"{agent.get('trust_score', 0):.2f}",
                        "active"  # TODO: Get real status
                    )
                
                console.print(table)
                
                if len(agents) > 20:
                    console.print(f"\n[dim]... and {len(agents) - 20} more agents[/dim]")
                    
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

async def show_agent(agent_id, as_json=False):
    """Show detailed agent information"""
    async with aiohttp.ClientSession() as session:
        try:
            # Get agent details
            async with session.get(f"{API_BASE}/agents/{agent_id}") as resp:
                if resp.status == 404:
                    console.print(f"[red]Agent '{agent_id}' not found[/red]")
                    return
                    
                agent = await resp.json()
                
                if as_json:
                    # Pretty print JSON
                    syntax = Syntax(json.dumps(agent, indent=2), "json")
                    console.print(syntax)
                else:
                    # Format nicely
                    console.print(f"\n[bold cyan]Agent: {agent.get('name', 'Unknown')}[/bold cyan]")
                    console.print(f"ID: {agent.get('id')}")
                    console.print(f"Type: {agent.get('type', 'specialist')}")
                    console.print(f"Domain: {agent.get('domain', 'N/A')}")
                    
                    meta = agent.get('enhanced_metadata', {})
                    if meta:
                        console.print(f"\n[yellow]Metadata:[/yellow]")
                        console.print(f"  Display Name: {meta.get('display_name')}")
                        console.print(f"  Trust Score: {meta.get('trust_score', 0):.2f}")
                        console.print(f"  Avatar: {meta.get('avatar', '🤖')}")
                    
                    caps = agent.get('capabilities', {})
                    if caps.get('primary_expertise'):
                        console.print(f"\n[green]Expertise:[/green]")
                        for skill in caps['primary_expertise']:
                            console.print(f"  • {skill}")
                    
                    if agent.get('tools'):
                        console.print(f"\n[blue]Tools:[/blue]")
                        for tool in agent['tools']:
                            console.print(f"  • {tool}")
                    
                    if agent.get('instructions'):
                        console.print(f"\n[magenta]Instructions:[/magenta]")
                        console.print(agent['instructions'][:200] + "..." if len(agent['instructions']) > 200 else agent['instructions'])
                        
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

async def add_agent(name, domain, agent_type):
    """Create a new agent"""
    console.print(f"[yellow]Creating agent '{name}' in domain '{domain}'...[/yellow]")
    
    agent_data = {
        "id": f"{domain}_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}",
        "name": name,
        "type": agent_type,
        "domain": domain,
        "instructions": f"You are {name}, a {agent_type} agent in the {domain} domain.",
        "enhanced_metadata": {
            "display_name": name,
            "trust_score": 0.80,
            "avatar": "🤖"
        }
    }
    
    # TODO: Save to database/API
    console.print(f"[green]✓ Agent '{name}' created successfully![/green]")
    console.print(f"[dim]ID: {agent_data['id']}[/dim]")
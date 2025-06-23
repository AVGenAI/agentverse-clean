"""
System Commands for A\V OS
"""
import aiohttp
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from datetime import datetime

console = Console()

API_BASE = "http://localhost:8000"

async def system_status():
    """Show comprehensive system status"""
    # Create layout
    layout = Layout()
    
    # System info
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    system_info = f"""[bold cyan]A\V OS System Status[/bold cyan]
    
📊 System Resources:
  CPU Usage: {cpu_percent}%
  Memory: {memory.percent}% ({memory.used // (1024**3)}GB / {memory.total // (1024**3)}GB)
  Disk: {disk.percent}% used
  
🕐 Uptime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    async with aiohttp.ClientSession() as session:
        try:
            # Get API health
            async with session.get(f"{API_BASE}/health") as resp:
                health = await resp.json()
                api_status = "[green]● Online[/green]"
        except:
            api_status = "[red]● Offline[/red]"
            health = {}
        
        # Get agent stats
        try:
            async with session.post(f"{API_BASE}/agents", json={}) as resp:
                agents = await resp.json()
                total_agents = agents.get('total', 0)
        except:
            total_agents = 0
        
        # Agent info
        agent_info = f"""[bold magenta]Agent Statistics[/bold magenta]
        
🤖 Total Agents: {total_agents}
📡 API Status: {api_status}
🔌 MCP Servers: {health.get('mcp_servers', 0)}
📊 Active Sessions: {health.get('active_sessions', 0)}
"""
        
        # Display panels
        console.print(Panel(system_info, title="System", border_style="cyan"))
        console.print(Panel(agent_info, title="Agents", border_style="magenta"))
        
        # Show domain breakdown if available
        if total_agents > 0:
            try:
                # Get domain stats
                domains = {}
                async with session.post(f"{API_BASE}/agents", json={}) as resp:
                    data = await resp.json()
                    for agent in data.get('agents', []):
                        domain = agent.get('canonical_name', '').split('.')[1] if '.' in agent.get('canonical_name', '') else 'unknown'
                        domains[domain] = domains.get(domain, 0) + 1
                
                # Create domain table
                table = Table(title="Agent Distribution by Domain")
                table.add_column("Domain", style="cyan")
                table.add_column("Count", style="magenta")
                table.add_column("Percentage", style="green")
                
                for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_agents) * 100
                    table.add_row(domain, str(count), f"{percentage:.1f}%")
                
                console.print(table)
            except:
                pass
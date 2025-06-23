"""
MCP Operations for A\V OS
"""
import aiohttp
from rich.console import Console
from rich.table import Table

console = Console()

API_BASE = "http://localhost:8000"

async def connect_mcp(agent_id, mcp_server):
    """Connect an agent to an MCP server"""
    console.print(f"[yellow]Connecting {agent_id} to {mcp_server}...[/yellow]")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create coupling
            data = {
                "agent_id": agent_id,
                "mcp_server_id": mcp_server,
                "status": "active"
            }
            
            async with session.post(f"{API_BASE}/api/mcp/couplings", json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    console.print(f"[green]✓ Successfully connected {agent_id} to {mcp_server}[/green]")
                    console.print(f"[dim]Coupling ID: {result.get('coupling_id')}[/dim]")
                else:
                    console.print(f"[red]Failed to connect: {resp.status}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
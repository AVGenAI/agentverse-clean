"""
Agent Execution Commands - Process Management for A\V OS
"""
import asyncio
import aiohttp
import psutil
import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich import print as rprint

console = Console()

API_BASE = "http://localhost:8000"

# In-memory process registry (later will use SQLite)
AGENT_PROCESSES = {}

class AgentProcess:
    """Represents a running agent process"""
    def __init__(self, agent_id, task, pid=None):
        self.agent_id = agent_id
        self.task = task
        self.pid = pid or id(self)
        self.status = "running"
        self.start_time = datetime.now()
        self.session_id = None
        
async def run_agent(agent_id, task, background=False):
    """Run an agent with a task"""
    console.print(f"[yellow]Starting agent '{agent_id}'...[/yellow]")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create chat session
            async with session.post(f"{API_BASE}/chat/session?agent_id={agent_id}") as resp:
                if resp.status != 200:
                    console.print(f"[red]Failed to start agent: {resp.status}[/red]")
                    return
                    
                session_data = await resp.json()
                session_id = session_data['session_id']
                
            # Create process entry
            process = AgentProcess(agent_id, task)
            process.session_id = session_id
            AGENT_PROCESSES[process.pid] = process
            
            if background:
                console.print(f"[green]Agent spawned in background (PID: {process.pid})[/green]")
                # Run in background
                asyncio.create_task(_run_agent_task(process, session_id, task))
            else:
                # Run in foreground
                await _run_agent_task(process, session_id, task)
                del AGENT_PROCESSES[process.pid]
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

async def _run_agent_task(process, session_id, task):
    """Execute the actual agent task"""
    async with aiohttp.ClientSession() as session:
        try:
            # Send message to agent
            data = {
                "session_id": session_id,
                "agent_id": process.agent_id,
                "message": task
            }
            
            async with session.post(f"{API_BASE}/chat/message", json=data) as resp:
                result = await resp.json()
                response = result.get('response', 'No response')
                
                console.print(f"\n[bold cyan]{process.agent_id}:[/bold cyan]")
                console.print(response)
                
                process.status = "completed"
                
        except Exception as e:
            console.print(f"[red]Agent error: {e}[/red]")
            process.status = "error"

async def ps_agents(show_all=False):
    """Show running agent processes"""
    table = Table(title="A\V OS Agent Processes")
    table.add_column("PID", style="cyan", no_wrap=True)
    table.add_column("Agent ID", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Task", style="yellow")
    table.add_column("Runtime", style="blue")
    
    # Get system info
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    console.print(f"[dim]CPU: {cpu_percent}% | Memory: {memory.percent}% | Agents: {len(AGENT_PROCESSES)}[/dim]\n")
    
    for pid, process in AGENT_PROCESSES.items():
        if not show_all and process.status != "running":
            continue
            
        runtime = datetime.now() - process.start_time
        runtime_str = f"{runtime.seconds}s"
        
        status_color = {
            "running": "[green]●[/green] running",
            "completed": "[blue]✓[/blue] completed",
            "error": "[red]✗[/red] error"
        }.get(process.status, process.status)
        
        table.add_row(
            str(pid),
            process.agent_id,
            status_color,
            process.task[:50] + "..." if len(process.task) > 50 else process.task,
            runtime_str
        )
    
    if not AGENT_PROCESSES:
        console.print("[dim]No agent processes running[/dim]")
    else:
        console.print(table)
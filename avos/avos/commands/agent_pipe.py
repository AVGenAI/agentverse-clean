"""
Agent Piping - Connect agents in a pipeline
"""
import asyncio
import aiohttp
import json
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
API_BASE = "http://localhost:8000"

class AgentPipeline:
    """Manages agent-to-agent communication pipelines"""
    
    def __init__(self):
        self.sessions = {}
        
    async def create_session(self, agent_id):
        """Create a chat session for an agent"""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{API_BASE}/chat/session?agent_id={agent_id}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['session_id']
                else:
                    raise Exception(f"Failed to create session for {agent_id}")
                    
    async def send_message(self, agent_id, session_id, message):
        """Send a message to an agent and get response"""
        async with aiohttp.ClientSession() as session:
            data = {
                "session_id": session_id,
                "agent_id": agent_id,
                "message": message
            }
            
            async with session.post(f"{API_BASE}/chat/message", json=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get('response', '')
                else:
                    raise Exception(f"Failed to get response from {agent_id}")
                    
    async def pipe(self, agent1_id, agent2_id, initial_task, show_intermediate=True):
        """Pipe output from agent1 to agent2"""
        console.print(f"\n[bold cyan]Creating pipeline: {agent1_id} → {agent2_id}[/bold cyan]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Create sessions
            task1 = progress.add_task(f"[yellow]Connecting to {agent1_id}...", total=None)
            session1 = await self.create_session(agent1_id)
            progress.update(task1, completed=True)
            
            task2 = progress.add_task(f"[yellow]Connecting to {agent2_id}...", total=None)
            session2 = await self.create_session(agent2_id)
            progress.update(task2, completed=True)
            
            # Send initial task to agent1
            task3 = progress.add_task(f"[yellow]Processing with {agent1_id}...", total=None)
            response1 = await self.send_message(agent1_id, session1, initial_task)
            progress.update(task3, completed=True)
            
            if show_intermediate:
                console.print(f"\n[bold green]{agent1_id} output:[/bold green]")
                console.print(Panel(response1, border_style="green"))
            
            # Pipe output to agent2
            task4 = progress.add_task(f"[yellow]Piping to {agent2_id}...", total=None)
            response2 = await self.send_message(agent2_id, session2, response1)
            progress.update(task4, completed=True)
            
            console.print(f"\n[bold blue]{agent2_id} final output:[/bold blue]")
            console.print(Panel(response2, border_style="blue"))
            
            return response2

async def pipe_agents(agent1_id, agent2_id, task):
    """Execute agent pipeline"""
    pipeline = AgentPipeline()
    
    try:
        result = await pipeline.pipe(agent1_id, agent2_id, task)
        console.print("\n[bold green]✅ Pipeline completed successfully[/bold green]")
        return result
    except Exception as e:
        console.print(f"\n[bold red]❌ Pipeline failed: {e}[/bold red]")
        return None

async def multi_pipe(agents, task):
    """Chain multiple agents together"""
    console.print(f"\n[bold cyan]Creating multi-agent pipeline:[/bold cyan]")
    console.print(" → ".join(agents))
    
    pipeline = AgentPipeline()
    current_output = task
    
    for i in range(len(agents) - 1):
        current_agent = agents[i]
        next_agent = agents[i + 1]
        
        console.print(f"\n[yellow]Step {i+1}: {current_agent} → {next_agent}[/yellow]")
        current_output = await pipeline.pipe(current_agent, next_agent, current_output, show_intermediate=False)
        
        if not current_output:
            console.print("[red]Pipeline broken[/red]")
            return None
            
    return current_output
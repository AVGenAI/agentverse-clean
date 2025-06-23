"""
Agent Communication Commands for A\V OS
"""
import asyncio
import aiohttp
from rich.console import Console
from rich.prompt import Prompt
from rich import print as rprint
from rich.markdown import Markdown

console = Console()

API_BASE = "http://localhost:8000"

async def chat_agent(agent_id):
    """Interactive chat with an agent"""
    console.print(f"\n[bold cyan]Starting chat with {agent_id}[/bold cyan]")
    console.print("[dim]Type 'exit' to quit, 'clear' to clear screen[/dim]\n")
    
    async with aiohttp.ClientSession() as session:
        try:
            # Create chat session
            async with session.post(f"{API_BASE}/chat/session?agent_id={agent_id}") as resp:
                if resp.status != 200:
                    console.print(f"[red]Failed to connect to agent[/red]")
                    return
                    
                session_data = await resp.json()
                session_id = session_data['session_id']
                
            # Interactive chat loop
            while True:
                try:
                    # Get user input
                    user_input = Prompt.ask(f"[bold green]You[/bold green]")
                    
                    if user_input.lower() == 'exit':
                        console.print("[yellow]Ending chat session...[/yellow]")
                        break
                    elif user_input.lower() == 'clear':
                        console.clear()
                        continue
                    
                    # Send to agent
                    data = {
                        "session_id": session_id,
                        "agent_id": agent_id,
                        "message": user_input
                    }
                    
                    console.print("[dim]Agent thinking...[/dim]")
                    
                    async with session.post(f"{API_BASE}/chat/message", json=data) as resp:
                        result = await resp.json()
                        response = result.get('response', 'No response')
                        
                        # Clear the "thinking" message
                        console.print("\033[1A\033[2K", end="")
                        
                        # Display agent response
                        console.print(f"\n[bold cyan]{agent_id}[/bold cyan]:")
                        # Try to render as markdown for better formatting
                        try:
                            md = Markdown(response)
                            console.print(md)
                        except:
                            console.print(response)
                        console.print()
                        
                except KeyboardInterrupt:
                    console.print("\n[yellow]Chat interrupted[/yellow]")
                    break
                except Exception as e:
                    console.print(f"[red]Error: {e}[/red]")
                    
        except Exception as e:
            console.print(f"[red]Connection error: {e}[/red]")
"""
Real-time Agent Monitoring - A\V OS Top Command
"""
import asyncio
import aiohttp
import psutil
import time
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.align import Align

console = Console()

API_BASE = "http://localhost:8000"

class AVOSMonitor:
    """Real-time system and agent monitor"""
    
    def __init__(self):
        self.running = True
        self.agents = []
        self.system_stats = {}
        
    def make_layout(self):
        """Create the display layout"""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        
        layout["body"].split_row(
            Layout(name="stats", ratio=1),
            Layout(name="agents", ratio=2)
        )
        
        return layout
        
    def get_header(self):
        """Generate header panel"""
        return Panel(
            Align.center(
                f"[bold cyan]A\V OS Monitor[/bold cyan] - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                vertical="middle"
            ),
            style="bold white on blue"
        )
        
    def get_system_stats(self):
        """Get system statistics"""
        cpu = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network stats
        net = psutil.net_io_counters()
        
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("CPU Usage", f"{cpu}%")
        stats_table.add_row("Memory", f"{memory.percent}% ({memory.used // 1024 // 1024}MB/{memory.total // 1024 // 1024}MB)")
        stats_table.add_row("Disk", f"{disk.percent}% used")
        stats_table.add_row("Network ↓", f"{net.bytes_recv // 1024 // 1024}MB")
        stats_table.add_row("Network ↑", f"{net.bytes_sent // 1024 // 1024}MB")
        stats_table.add_row("Active Agents", str(len([a for a in self.agents if a.get('status') == 'active'])))
        
        return Panel(stats_table, title="System Stats", border_style="green")
        
    async def get_agents_table(self):
        """Get agents status table"""
        table = Table(title="Agent Status")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Domain", style="yellow")
        table.add_column("LLM", style="blue")
        table.add_column("MCP", style="red")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{API_BASE}/agents") as resp:
                    if resp.status == 200:
                        agents = await resp.json()
                        self.agents = agents
                        
                        for agent in agents[:10]:  # Show top 10
                            status = "🟢 active" if agent.get('status') == 'active' else "🔴 inactive"
                            
                            table.add_row(
                                agent['id'][:20] + "...",
                                agent['name'],
                                status,
                                agent.get('domain', 'general'),
                                agent.get('model_preferences', {}).get('primary', 'unknown'),
                                agent.get('mcp_server', 'none')
                            )
            except:
                pass
                
        return Panel(table, title="Active Agents", border_style="cyan")
        
    def get_footer(self):
        """Generate footer with help"""
        return Panel(
            "[bold]Commands:[/bold] q - quit | r - refresh | ↑↓ - scroll | Enter - select agent",
            style="dim"
        )
        
    async def update_display(self, layout):
        """Update the display with latest data"""
        layout["header"].update(self.get_header())
        layout["stats"].update(self.get_system_stats())
        layout["agents"].update(await self.get_agents_table())
        layout["footer"].update(self.get_footer())
        
    async def run(self):
        """Run the monitor"""
        layout = self.make_layout()
        
        with Live(layout, refresh_per_second=1) as live:
            while self.running:
                await self.update_display(layout)
                
                # Check for keyboard input
                await asyncio.sleep(1)
                
                # For now, run for 30 seconds then exit
                # In a real implementation, we'd handle keyboard input
                if hasattr(self, 'start_time'):
                    if time.time() - self.start_time > 30:
                        self.running = False
                else:
                    self.start_time = time.time()

async def top_command():
    """Run the A\V OS monitor"""
    monitor = AVOSMonitor()
    console.print("[bold yellow]Starting A\V OS Monitor... (runs for 30 seconds)[/bold yellow]")
    await monitor.run()
    console.print("[bold green]Monitor stopped[/bold green]")
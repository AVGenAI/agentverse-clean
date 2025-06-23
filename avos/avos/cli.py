#!/usr/bin/env python3
"""
AVOS - Main CLI Entry Point
"""
import click
import asyncio
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from . import AVOS_LOGO
from .commands import (
    list_agents, show_agent, add_agent, run_agent,
    ps_agents, chat_agent, connect_mcp, system_status
)
from .commands.monitor import top_command
from .commands.agent_pipe import pipe_agents

console = Console()

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """AgentVerse OS - Command Line Interface for AI Agents"""
    if ctx.invoked_subcommand is None:
        console.print(AVOS_LOGO, style="bold cyan")
        console.print("Type 'av --help' for available commands\n")

# Agent Management Commands
@main.command()
@click.option('--domain', '-d', help='Filter by domain')
@click.option('--status', '-s', help='Filter by status')
@click.option('--running', '-r', is_flag=True, help='Show only running agents')
def list(domain, status, running):
    """List all agents (like 'ls')"""
    asyncio.run(list_agents(domain, status, running))

@main.command()
@click.argument('agent_id')
@click.option('--json', '-j', is_flag=True, help='Output as JSON')
def show(agent_id, json):
    """Show agent details (like 'cat')"""
    asyncio.run(show_agent(agent_id, json))

@main.command()
@click.argument('name')
@click.option('--system-prompt', '-s', help='System prompt for the agent')
@click.option('--llm', '-l', help='LLM model (e.g., gpt-4o, gpt-4o-mini, claude-3)')
@click.option('--mcp', '-m', help='MCP server to connect')
@click.option('--domain', '-d', help='Agent domain')
@click.option('--temperature', '-t', type=float, default=0.7, help='Temperature (0.0-1.0)')
@click.option('--max-tokens', default=2000, help='Max tokens')
@click.option('--tools', help='Comma-separated list of tools')
@click.option('--interactive', '-i', is_flag=True, help='Interactive mode')
def add(name, system_prompt, llm, mcp, domain, temperature, max_tokens, tools, interactive):
    """Create new agent with full configuration
    
    Examples:
        av add "Health Assistant" -s "You are a healthcare specialist" -l gpt-4o -d healthcare
        av add "SRE Expert" --llm gpt-4o-mini --mcp servicenow --tools search_incidents,create_incident
        av add "Data Analyst" -i  # Interactive mode
    """
    from .commands.agent_builder import AgentBuilder
    
    builder = AgentBuilder()
    tools_list = tools.split(',') if tools else None
    
    asyncio.run(builder.build_agent(
        name=name,
        system_prompt=system_prompt,
        llm_model=llm,
        mcp_server=mcp,
        domain=domain,
        tools=tools_list,
        temperature=temperature,
        max_tokens=max_tokens,
        interactive=interactive
    ))

# Agent Execution Commands
@main.command()
@click.argument('agent_id')
@click.argument('task')
@click.option('--background', '-b', is_flag=True, help='Run in background')
def run(agent_id, task, background):
    """Run agent with task"""
    asyncio.run(run_agent(agent_id, task, background))

@main.command()
@click.option('--all', '-a', is_flag=True, help='Show all processes')
def ps(all):
    """Show running agents (like 'ps')"""
    asyncio.run(ps_agents(all))

# Communication Commands
@main.command()
@click.argument('agent_id')
def chat(agent_id):
    """Start interactive chat with agent"""
    asyncio.run(chat_agent(agent_id))

@main.command()
@click.argument('agent_id')
@click.argument('query')
def ask(agent_id, query):
    """One-time query to agent"""
    asyncio.run(run_agent(agent_id, query, background=False))

# MCP Commands
@main.command()
@click.argument('agent_id')
@click.argument('mcp_server')
def connect(agent_id, mcp_server):
    """Connect agent to MCP server"""
    asyncio.run(connect_mcp(agent_id, mcp_server))

# System Commands
@main.command()
def status():
    """Show system status"""
    asyncio.run(system_status())

@main.command()
def version():
    """Show AVOS version"""
    from . import __version__
    console.print(f"AVOS version {__version__}", style="bold green")

@main.command()
@click.option('--systemprompt', '-s', required=True, help='System prompt for the agent')
@click.option('--llm', '-l', required=True, help='LLM model (e.g., gpt-4o, gpt-4o-mini, claude-3)')
@click.option('--mcp', '-m', help='MCP server to connect')
@click.option('--name', '-n', help='Agent name (auto-generated if not provided)')
@click.option('--domain', '-d', help='Agent domain')
@click.option('--tools', '-t', help='Comma-separated list of tools')
@click.option('--temperature', type=float, default=0.7, help='Temperature (0.0-1.0)')
def build(systemprompt, llm, mcp, name, domain, tools, temperature):
    """Build an agent with specified configuration
    
    Examples:
        av build --systemprompt "You are a helpful healthcare specialist" --llm gpt-4o --mcp postgresql
        av build -s "Expert in Kubernetes" -l gpt-4o-mini -m prometheus -t deploy,scale,monitor
    """
    from .commands.agent_builder import AgentBuilder
    import random
    
    # Auto-generate name if not provided
    if not name:
        prefixes = ["Expert", "Specialist", "Assistant", "Advisor", "Analyst"]
        suffixes = ["Alpha", "Beta", "Prime", "Pro", "Plus"]
        name = f"{random.choice(prefixes)} {random.choice(suffixes)} {random.randint(100, 999)}"
    
    # Infer domain from prompt if not provided
    if not domain:
        prompt_lower = systemprompt.lower()
        if "health" in prompt_lower or "medical" in prompt_lower:
            domain = "healthcare"
        elif "devops" in prompt_lower or "kubernetes" in prompt_lower:
            domain = "devops"
        elif "data" in prompt_lower or "analytics" in prompt_lower:
            domain = "data"
        elif "security" in prompt_lower or "cyber" in prompt_lower:
            domain = "security"
        else:
            domain = "general"
    
    builder = AgentBuilder()
    tools_list = tools.split(',') if tools else None
    
    asyncio.run(builder.build_agent(
        name=name,
        system_prompt=systemprompt,
        llm_model=llm,
        mcp_server=mcp,
        domain=domain,
        tools=tools_list,
        temperature=temperature,
        max_tokens=2000,
        interactive=False
    ))

# Advanced Commands
@main.command()
@click.argument('agent1')
@click.argument('agent2')
@click.argument('task')
def pipe(agent1, agent2, task):
    """Pipe output from agent1 to agent2"""
    asyncio.run(pipe_agents(agent1, agent2, task))

@main.command()
def top():
    """Real-time agent monitoring (like 'top')"""
    asyncio.run(top_command())

if __name__ == '__main__':
    main()
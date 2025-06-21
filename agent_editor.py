#!/usr/bin/env python3
"""
AgentVerse Agent Editor CLI
Edit, update, and manage all 1000+ agents via command line
"""

import json
import argparse
import sys
import os
from typing import Dict, List, Optional
import re
from datetime import datetime
import shutil
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.panel import Panel
from rich import print as rprint

console = Console()

class AgentEditor:
    def __init__(self, config_file: str = "src/config/agentverse_agents_1000.json"):
        self.config_file = config_file
        self.agents = []
        self.backup_file = None
        self.load_agents()
    
    def load_agents(self):
        """Load agents from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.agents = json.load(f)
            console.print(f"[green]✅ Loaded {len(self.agents)} agents[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error loading agents: {e}[/red]")
            sys.exit(1)
    
    def save_agents(self, create_backup: bool = True):
        """Save agents back to JSON file"""
        if create_backup and not self.backup_file:
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_file = f"{self.config_file}.backup_{timestamp}"
            shutil.copy(self.config_file, self.backup_file)
            console.print(f"[yellow]📦 Created backup: {self.backup_file}[/yellow]")
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.agents, f, indent=2)
            console.print(f"[green]✅ Saved {len(self.agents)} agents[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error saving agents: {e}[/red]")
            if self.backup_file:
                console.print(f"[yellow]Restore from backup: {self.backup_file}[/yellow]")
    
    def find_agent(self, query: str) -> List[Dict]:
        """Find agents by ID, name, or skill"""
        results = []
        query_lower = query.lower()
        
        for agent in self.agents:
            metadata = agent.get('enhanced_metadata', {})
            
            # Search in various fields
            if (query_lower in metadata.get('agent_uuid', '').lower() or
                query_lower in metadata.get('canonical_name', '').lower() or
                query_lower in metadata.get('display_name', '').lower() or
                query_lower in agent.get('name', '').lower() or
                any(query_lower in skill.lower() for skill in agent.get('skills', []))):
                results.append(agent)
        
        return results
    
    def list_agents(self, domain: Optional[str] = None, limit: int = 20):
        """List agents with optional filtering"""
        agents_to_show = self.agents
        
        if domain:
            agents_to_show = [a for a in agents_to_show 
                            if domain.lower() in a.get('enhanced_metadata', {}).get('canonical_name', '').lower()]
        
        # Create table
        table = Table(title=f"AgentVerse Agents (showing {min(limit, len(agents_to_show))} of {len(agents_to_show)})")
        table.add_column("UUID", style="cyan", width=16)
        table.add_column("Name", style="green")
        table.add_column("Domain", style="yellow")
        table.add_column("Skills", style="blue")
        table.add_column("Version", style="magenta")
        
        for agent in agents_to_show[:limit]:
            metadata = agent.get('enhanced_metadata', {})
            uuid = metadata.get('agent_uuid', 'N/A')[:16]
            name = metadata.get('display_name', agent.get('name', 'Unknown'))
            
            # Extract domain from canonical name
            canonical = metadata.get('canonical_name', '')
            domain_match = re.search(r'agentverse\.([^.]+)', canonical)
            domain = domain_match.group(1) if domain_match else 'unknown'
            
            skills = ', '.join(agent.get('skills', [])[:3])
            version = metadata.get('version', '1.0.0')
            
            table.add_row(uuid, name, domain, skills, version)
        
        console.print(table)
    
    def show_agent(self, agent_id: str):
        """Display detailed agent information"""
        agents = self.find_agent(agent_id)
        
        if not agents:
            console.print(f"[red]❌ No agent found with ID: {agent_id}[/red]")
            return
        
        if len(agents) > 1:
            console.print(f"[yellow]⚠️  Found {len(agents)} agents. Showing first match.[/yellow]")
        
        agent = agents[0]
        metadata = agent.get('enhanced_metadata', {})
        
        # Display agent info
        panel_content = f"""
[bold cyan]UUID:[/bold cyan] {metadata.get('agent_uuid', 'N/A')}
[bold cyan]Canonical Name:[/bold cyan] {metadata.get('canonical_name', 'N/A')}
[bold cyan]Display Name:[/bold cyan] {metadata.get('display_name', 'N/A')}
[bold cyan]Avatar:[/bold cyan] {metadata.get('avatar_emoji', '🤖')}
[bold cyan]Version:[/bold cyan] {metadata.get('version', '1.0.0')}
[bold cyan]Created:[/bold cyan] {metadata.get('created_at', 'Unknown')}

[bold green]Category:[/bold green] {agent.get('category', 'N/A')}
[bold green]Subcategory:[/bold green] {agent.get('subcategory', 'N/A')}

[bold yellow]Skills:[/bold yellow] {', '.join(agent.get('skills', []))}
[bold yellow]Tools:[/bold yellow] {', '.join(agent.get('tools', []))}

[bold blue]Primary Expertise:[/bold blue] {', '.join(metadata.get('capabilities', {}).get('primary_expertise', []))}
[bold blue]Secondary Expertise:[/bold blue] {', '.join(metadata.get('capabilities', {}).get('secondary_expertise', []))}
"""
        
        console.print(Panel(panel_content, title=f"Agent: {metadata.get('display_name', 'Unknown')}", border_style="cyan"))
        
        # Show instructions
        instructions = agent.get('instructions', 'No instructions')
        console.print("\n[bold]Instructions:[/bold]")
        console.print(Syntax(instructions, "text", theme="monokai", line_numbers=True))
    
    def edit_agent(self, agent_id: str):
        """Interactive agent editor"""
        agents = self.find_agent(agent_id)
        
        if not agents:
            console.print(f"[red]❌ No agent found with ID: {agent_id}[/red]")
            return
        
        agent = agents[0]
        agent_index = self.agents.index(agent)
        metadata = agent.get('enhanced_metadata', {})
        
        console.print(f"\n[bold cyan]Editing Agent: {metadata.get('display_name', 'Unknown')}[/bold cyan]")
        
        while True:
            # Show edit menu
            console.print("\n[bold]What would you like to edit?[/bold]")
            console.print("1. Display Name")
            console.print("2. Instructions")
            console.print("3. Skills")
            console.print("4. Tools")
            console.print("5. Avatar Emoji")
            console.print("6. Version")
            console.print("7. Category/Subcategory")
            console.print("8. Primary Expertise")
            console.print("9. Collaboration Style")
            console.print("0. Save and Exit")
            console.print("q. Cancel without saving")
            
            choice = Prompt.ask("Enter your choice")
            
            if choice == '0':
                self.agents[agent_index] = agent
                self.save_agents()
                console.print("[green]✅ Changes saved![/green]")
                break
            elif choice == 'q':
                console.print("[yellow]Changes discarded.[/yellow]")
                break
            elif choice == '1':
                new_name = Prompt.ask("Enter new display name", default=metadata.get('display_name', ''))
                metadata['display_name'] = new_name
                agent['name'] = new_name
            elif choice == '2':
                console.print("[dim]Current instructions:[/dim]")
                console.print(agent.get('instructions', '')[:200] + "...")
                console.print("\n[yellow]Enter new instructions (type 'END' on a new line to finish):[/yellow]")
                
                lines = []
                while True:
                    line = input()
                    if line == 'END':
                        break
                    lines.append(line)
                
                agent['instructions'] = '\n'.join(lines)
            elif choice == '3':
                current_skills = ', '.join(agent.get('skills', []))
                new_skills = Prompt.ask("Enter skills (comma-separated)", default=current_skills)
                agent['skills'] = [s.strip() for s in new_skills.split(',')]
                metadata.setdefault('capabilities', {})['primary_expertise'] = agent['skills'][:3]
            elif choice == '4':
                current_tools = ', '.join(agent.get('tools', []))
                new_tools = Prompt.ask("Enter tools (comma-separated)", default=current_tools)
                agent['tools'] = [t.strip() for t in new_tools.split(',')]
            elif choice == '5':
                new_emoji = Prompt.ask("Enter avatar emoji", default=metadata.get('avatar_emoji', '🤖'))
                metadata['avatar_emoji'] = new_emoji
            elif choice == '6':
                current_version = metadata.get('version', '1.0.0')
                new_version = Prompt.ask("Enter version", default=current_version)
                metadata['version'] = new_version
            elif choice == '7':
                new_category = Prompt.ask("Enter category", default=agent.get('category', ''))
                new_subcategory = Prompt.ask("Enter subcategory", default=agent.get('subcategory', ''))
                agent['category'] = new_category
                agent['subcategory'] = new_subcategory
            elif choice == '8':
                capabilities = metadata.setdefault('capabilities', {})
                current_primary = ', '.join(capabilities.get('primary_expertise', []))
                new_primary = Prompt.ask("Enter primary expertise (comma-separated)", default=current_primary)
                capabilities['primary_expertise'] = [e.strip() for e in new_primary.split(',')]
            elif choice == '9':
                collaboration = metadata.setdefault('collaboration', {})
                current_style = ', '.join(collaboration.get('style', []))
                new_style = Prompt.ask("Enter collaboration style (mentor,peer,learner)", default=current_style)
                collaboration['style'] = [s.strip() for s in new_style.split(',')]
    
    def bulk_edit(self, domain: str, field: str, value: str):
        """Bulk edit agents in a domain"""
        matching_agents = [a for a in self.agents 
                          if domain.lower() in a.get('enhanced_metadata', {}).get('canonical_name', '').lower()]
        
        if not matching_agents:
            console.print(f"[red]❌ No agents found in domain: {domain}[/red]")
            return
        
        console.print(f"[yellow]Found {len(matching_agents)} agents in domain '{domain}'[/yellow]")
        
        if not Confirm.ask(f"Update {field} to '{value}' for all {len(matching_agents)} agents?"):
            console.print("[yellow]Operation cancelled.[/yellow]")
            return
        
        updated = 0
        for agent in matching_agents:
            if field == 'version':
                agent['enhanced_metadata']['version'] = value
                updated += 1
            elif field == 'model':
                agent['model'] = value
                updated += 1
            elif field == 'category':
                agent['category'] = value
                updated += 1
            # Add more fields as needed
        
        if updated > 0:
            self.save_agents()
            console.print(f"[green]✅ Updated {updated} agents[/green]")
        else:
            console.print(f"[red]❌ Field '{field}' not supported for bulk edit[/red]")
    
    def add_skill_to_all(self, skill: str, domain: Optional[str] = None):
        """Add a skill to all agents or agents in a domain"""
        if domain:
            agents_to_update = [a for a in self.agents 
                              if domain.lower() in a.get('enhanced_metadata', {}).get('canonical_name', '').lower()]
        else:
            agents_to_update = self.agents
        
        console.print(f"[yellow]Adding skill '{skill}' to {len(agents_to_update)} agents[/yellow]")
        
        if not Confirm.ask("Continue?"):
            return
        
        updated = 0
        for agent in agents_to_update:
            if skill not in agent.get('skills', []):
                agent.setdefault('skills', []).append(skill)
                updated += 1
        
        if updated > 0:
            self.save_agents()
            console.print(f"[green]✅ Added skill to {updated} agents[/green]")
    
    def validate_agents(self):
        """Validate all agents for consistency"""
        console.print("[bold]Validating agents...[/bold]")
        
        issues = []
        
        for i, agent in enumerate(self.agents):
            # Check required fields
            if not agent.get('name'):
                issues.append(f"Agent {i}: Missing name")
            
            if not agent.get('instructions'):
                issues.append(f"Agent {i}: Missing instructions")
            
            metadata = agent.get('enhanced_metadata', {})
            if not metadata.get('agent_uuid'):
                issues.append(f"Agent {i}: Missing UUID")
            
            if not metadata.get('canonical_name'):
                issues.append(f"Agent {i}: Missing canonical name")
        
        if issues:
            console.print(f"[red]Found {len(issues)} issues:[/red]")
            for issue in issues[:10]:  # Show first 10
                console.print(f"  • {issue}")
            if len(issues) > 10:
                console.print(f"  ... and {len(issues) - 10} more")
        else:
            console.print("[green]✅ All agents are valid![/green]")
    
    def export_agents(self, output_file: str, domain: Optional[str] = None):
        """Export agents to a new file"""
        if domain:
            agents_to_export = [a for a in self.agents 
                              if domain.lower() in a.get('enhanced_metadata', {}).get('canonical_name', '').lower()]
        else:
            agents_to_export = self.agents
        
        with open(output_file, 'w') as f:
            json.dump(agents_to_export, f, indent=2)
        
        console.print(f"[green]✅ Exported {len(agents_to_export)} agents to {output_file}[/green]")
    
    def restore_backup(self):
        """Restore from backup"""
        # Find backup files
        backup_files = [f for f in os.listdir('.') if f.startswith(f"{self.config_file}.backup_")]
        
        if not backup_files:
            console.print("[red]❌ No backup files found[/red]")
            return
        
        console.print("[bold]Available backups:[/bold]")
        for i, backup in enumerate(sorted(backup_files, reverse=True)):
            console.print(f"{i+1}. {backup}")
        
        choice = Prompt.ask("Select backup to restore (number)")
        
        try:
            backup_file = sorted(backup_files, reverse=True)[int(choice) - 1]
            shutil.copy(backup_file, self.config_file)
            console.print(f"[green]✅ Restored from {backup_file}[/green]")
            self.load_agents()
        except:
            console.print("[red]❌ Invalid selection[/red]")

def main():
    parser = argparse.ArgumentParser(description="AgentVerse Agent Editor CLI")
    parser.add_argument('--config', default='src/config/agentverse_agents_1000.json', 
                       help='Path to agents config file')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List agents')
    list_parser.add_argument('--domain', help='Filter by domain')
    list_parser.add_argument('--limit', type=int, default=20, help='Number of agents to show')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show agent details')
    show_parser.add_argument('agent_id', help='Agent ID, UUID, or name')
    
    # Edit command
    edit_parser = subparsers.add_parser('edit', help='Edit an agent')
    edit_parser.add_argument('agent_id', help='Agent ID, UUID, or name')
    
    # Bulk edit command
    bulk_parser = subparsers.add_parser('bulk-edit', help='Bulk edit agents')
    bulk_parser.add_argument('domain', help='Domain to filter')
    bulk_parser.add_argument('field', help='Field to update (version, model, category)')
    bulk_parser.add_argument('value', help='New value')
    
    # Add skill command
    skill_parser = subparsers.add_parser('add-skill', help='Add skill to agents')
    skill_parser.add_argument('skill', help='Skill to add')
    skill_parser.add_argument('--domain', help='Limit to specific domain')
    
    # Validate command
    subparsers.add_parser('validate', help='Validate all agents')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export agents')
    export_parser.add_argument('output_file', help='Output file name')
    export_parser.add_argument('--domain', help='Export only specific domain')
    
    # Restore command
    subparsers.add_parser('restore', help='Restore from backup')
    
    # Find command
    find_parser = subparsers.add_parser('find', help='Find agents by query')
    find_parser.add_argument('query', help='Search query')
    
    args = parser.parse_args()
    
    # Create editor instance
    editor = AgentEditor(args.config)
    
    # Execute command
    if args.command == 'list':
        editor.list_agents(args.domain, args.limit)
    elif args.command == 'show':
        editor.show_agent(args.agent_id)
    elif args.command == 'edit':
        editor.edit_agent(args.agent_id)
    elif args.command == 'bulk-edit':
        editor.bulk_edit(args.domain, args.field, args.value)
    elif args.command == 'add-skill':
        editor.add_skill_to_all(args.skill, args.domain)
    elif args.command == 'validate':
        editor.validate_agents()
    elif args.command == 'export':
        editor.export_agents(args.output_file, args.domain)
    elif args.command == 'restore':
        editor.restore_backup()
    elif args.command == 'find':
        results = editor.find_agent(args.query)
        console.print(f"Found {len(results)} agents")
        for agent in results[:10]:
            metadata = agent.get('enhanced_metadata', {})
            console.print(f"• {metadata.get('display_name')} ({metadata.get('agent_uuid', 'N/A')[:16]})")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Differentiate Duplicate Agents
Gives unique specializations to agents with A, B, C suffixes
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich import print as rprint

console = Console()

class AgentDifferentiator:
    """Differentiate duplicate agents with unique specializations"""
    
    def __init__(self, config_file: str = "src/config/agentverse_agents_1000.json"):
        self.config_file = config_file
        self.agents = []
        self.specializations = self._define_specializations()
        self.load_agents()
    
    def load_agents(self):
        """Load existing agents"""
        with open(self.config_file, 'r') as f:
            self.agents = json.load(f)
        console.print(f"[green]✅ Loaded {len(self.agents)} agents[/green]")
    
    def _define_specializations(self) -> Dict[str, List[Dict]]:
        """Define unique specializations for each role type"""
        return {
            "DjangoExpert": [
                {
                    "suffix": "",  # No suffix for base expert
                    "specialty": "General Django Development",
                    "focus": "Full-stack Django applications",
                    "extra_skills": ["Django REST Framework", "Celery", "Redis"],
                    "description": "Expert in all aspects of Django development"
                },
                {
                    "suffix": "A",
                    "specialty": "Django REST API Specialist",
                    "focus": "RESTful API design and implementation",
                    "extra_skills": ["Django REST Framework", "API Versioning", "JWT Authentication", "API Documentation"],
                    "description": "Specializes in building scalable REST APIs with Django"
                },
                {
                    "suffix": "B",
                    "specialty": "Django GraphQL Specialist",
                    "focus": "GraphQL API development with Django",
                    "extra_skills": ["Graphene-Django", "GraphQL Schema Design", "Subscription Handling", "DataLoader"],
                    "description": "Expert in GraphQL implementations with Django"
                },
                {
                    "suffix": "C",
                    "specialty": "Django Microservices Architect",
                    "focus": "Microservices architecture with Django",
                    "extra_skills": ["Service Mesh", "gRPC", "Message Queues", "Event-Driven Architecture"],
                    "description": "Specializes in Django-based microservices"
                },
                {
                    "suffix": "D",
                    "specialty": "Django Performance Expert",
                    "focus": "Performance optimization and scaling",
                    "extra_skills": ["Database Optimization", "Caching Strategies", "Load Balancing", "Profiling"],
                    "description": "Expert in Django performance tuning"
                },
                {
                    "suffix": "E",
                    "specialty": "Django Security Specialist",
                    "focus": "Security hardening and compliance",
                    "extra_skills": ["OWASP", "Security Auditing", "Penetration Testing", "Compliance"],
                    "description": "Focuses on Django security best practices"
                }
            ],
            "ReactExpert": [
                {
                    "suffix": "",
                    "specialty": "General React Development",
                    "focus": "React applications and components",
                    "extra_skills": ["React Hooks", "Context API", "Component Design"],
                    "description": "Expert in all aspects of React development"
                },
                {
                    "suffix": "A",
                    "specialty": "React Native Specialist",
                    "focus": "Cross-platform mobile development",
                    "extra_skills": ["React Native", "Expo", "Native Modules", "Mobile Performance"],
                    "description": "Specializes in React Native mobile apps"
                },
                {
                    "suffix": "B",
                    "specialty": "React Performance Expert",
                    "focus": "React optimization and performance",
                    "extra_skills": ["React DevTools", "Profiling", "Code Splitting", "Lazy Loading"],
                    "description": "Expert in React performance optimization"
                },
                {
                    "suffix": "C",
                    "specialty": "React TypeScript Specialist",
                    "focus": "Type-safe React development",
                    "extra_skills": ["TypeScript", "Type Definitions", "Generic Components", "Type Guards"],
                    "description": "Specializes in React with TypeScript"
                },
                {
                    "suffix": "D",
                    "specialty": "React State Management Expert",
                    "focus": "Complex state management solutions",
                    "extra_skills": ["Redux", "MobX", "Recoil", "Zustand"],
                    "description": "Expert in React state management"
                },
                {
                    "suffix": "E",
                    "specialty": "React Testing Specialist",
                    "focus": "Comprehensive React testing",
                    "extra_skills": ["Jest", "React Testing Library", "Cypress", "E2E Testing"],
                    "description": "Focuses on React testing strategies"
                }
            ],
            "DataEngineer": [
                {
                    "suffix": "",
                    "specialty": "General Data Engineering",
                    "focus": "Data pipelines and infrastructure",
                    "extra_skills": ["ETL", "Data Warehousing", "Data Modeling"],
                    "description": "Expert in data engineering fundamentals"
                },
                {
                    "suffix": "A",
                    "specialty": "Big Data Specialist",
                    "focus": "Large-scale data processing",
                    "extra_skills": ["Apache Spark", "Hadoop", "Kafka", "Distributed Computing"],
                    "description": "Specializes in big data technologies"
                },
                {
                    "suffix": "B",
                    "specialty": "Real-time Data Expert",
                    "focus": "Streaming and real-time processing",
                    "extra_skills": ["Apache Flink", "Kafka Streams", "Storm", "Real-time Analytics"],
                    "description": "Expert in real-time data processing"
                },
                {
                    "suffix": "C",
                    "specialty": "Cloud Data Architect",
                    "focus": "Cloud-native data solutions",
                    "extra_skills": ["AWS Data Services", "Azure Data Factory", "GCP BigQuery", "Serverless"],
                    "description": "Specializes in cloud data architecture"
                },
                {
                    "suffix": "D",
                    "specialty": "DataOps Specialist",
                    "focus": "Data operations and automation",
                    "extra_skills": ["CI/CD for Data", "Data Quality", "Monitoring", "Orchestration"],
                    "description": "Expert in DataOps practices"
                },
                {
                    "suffix": "E",
                    "specialty": "Data Governance Expert",
                    "focus": "Data governance and compliance",
                    "extra_skills": ["Data Catalog", "Lineage Tracking", "GDPR", "Data Security"],
                    "description": "Focuses on data governance"
                }
            ],
            "DevOpsEngineer": [
                {
                    "suffix": "",
                    "specialty": "General DevOps",
                    "focus": "CI/CD and infrastructure automation",
                    "extra_skills": ["Jenkins", "GitLab CI", "Terraform", "Ansible"],
                    "description": "Expert in DevOps practices"
                },
                {
                    "suffix": "A",
                    "specialty": "Kubernetes Specialist",
                    "focus": "Container orchestration",
                    "extra_skills": ["Kubernetes", "Helm", "Istio", "Container Security"],
                    "description": "Specializes in Kubernetes"
                },
                {
                    "suffix": "B",
                    "specialty": "Cloud Infrastructure Expert",
                    "focus": "Multi-cloud infrastructure",
                    "extra_skills": ["AWS", "Azure", "GCP", "Cloud Architecture"],
                    "description": "Expert in cloud infrastructure"
                },
                {
                    "suffix": "C",
                    "specialty": "GitOps Specialist",
                    "focus": "GitOps workflows",
                    "extra_skills": ["ArgoCD", "Flux", "GitOps Patterns", "Progressive Delivery"],
                    "description": "Specializes in GitOps"
                },
                {
                    "suffix": "D",
                    "specialty": "SRE Expert",
                    "focus": "Site reliability engineering",
                    "extra_skills": ["SLOs/SLIs", "Error Budgets", "Chaos Engineering", "Observability"],
                    "description": "Expert in SRE practices"
                },
                {
                    "suffix": "E",
                    "specialty": "Security DevOps Specialist",
                    "focus": "DevSecOps practices",
                    "extra_skills": ["SAST/DAST", "Container Security", "Secret Management", "Compliance as Code"],
                    "description": "Focuses on DevSecOps"
                }
            ],
            "MLEngineer": [
                {
                    "suffix": "",
                    "specialty": "General ML Engineering",
                    "focus": "Machine learning systems",
                    "extra_skills": ["TensorFlow", "PyTorch", "Scikit-learn", "Model Training"],
                    "description": "Expert in ML engineering"
                },
                {
                    "suffix": "A",
                    "specialty": "Deep Learning Specialist",
                    "focus": "Neural networks and deep learning",
                    "extra_skills": ["CNNs", "RNNs", "Transformers", "GPU Optimization"],
                    "description": "Specializes in deep learning"
                },
                {
                    "suffix": "B",
                    "specialty": "MLOps Expert",
                    "focus": "ML operations and deployment",
                    "extra_skills": ["MLflow", "Kubeflow", "Model Monitoring", "A/B Testing"],
                    "description": "Expert in MLOps"
                },
                {
                    "suffix": "C",
                    "specialty": "NLP Specialist",
                    "focus": "Natural language processing",
                    "extra_skills": ["BERT", "GPT", "Sentiment Analysis", "Text Generation"],
                    "description": "Specializes in NLP"
                },
                {
                    "suffix": "D",
                    "specialty": "Computer Vision Expert",
                    "focus": "Image and video processing",
                    "extra_skills": ["Object Detection", "Image Segmentation", "Video Analysis", "OpenCV"],
                    "description": "Expert in computer vision"
                },
                {
                    "suffix": "E",
                    "specialty": "Edge ML Specialist",
                    "focus": "ML on edge devices",
                    "extra_skills": ["TensorFlow Lite", "ONNX", "Model Compression", "Edge Deployment"],
                    "description": "Focuses on edge ML"
                }
            ]
        }
    
    def find_duplicate_agents(self) -> Dict[str, List[Dict]]:
        """Find agents with letter suffixes (duplicates)"""
        duplicates = defaultdict(list)
        
        for agent in self.agents:
            name = agent.get('name', '')
            # Match pattern like OpenAISDK_Domain_Role_A
            match = re.match(r'(.+SDK_[^_]+_[^_]+)_([A-Z])$', name)
            if match:
                base_name = match.group(1)
                suffix = match.group(2)
                
                # Extract role from name
                parts = name.split('_')
                if len(parts) >= 3:
                    role = parts[2]
                    agent_info = {
                        'agent': agent,
                        'base_name': base_name,
                        'suffix': suffix,
                        'role': role,
                        'index': self.agents.index(agent)
                    }
                    duplicates[role].append(agent_info)
        
        return duplicates
    
    def differentiate_agent(self, agent: Dict, role: str, suffix: str) -> Dict:
        """Apply unique specialization to an agent"""
        
        if role not in self.specializations:
            return agent
        
        # Find matching specialization
        specialization = None
        for spec in self.specializations[role]:
            if spec['suffix'] == suffix:
                specialization = spec
                break
        
        if not specialization:
            # If no specific specialization for this suffix, use a generic one
            return agent
        
        # Update agent with specialization
        updated_agent = agent.copy()
        
        # Update display name
        display_parts = updated_agent.get('display_name', '').split(' (')
        if len(display_parts) > 0:
            base_display = display_parts[0].split()[0]  # Get role part
            domain = display_parts[1].rstrip(')') if len(display_parts) > 1 else 'General'
            updated_agent['display_name'] = f"{specialization['specialty']} ({domain})"
        
        # Update skills
        current_skills = updated_agent.get('skills', [])
        # Keep first 2 original skills, add specialization skills
        updated_skills = current_skills[:2] + specialization['extra_skills']
        # Remove duplicates while preserving order
        seen = set()
        updated_agent['skills'] = [s for s in updated_skills if not (s in seen or seen.add(s))][:8]
        
        # Update instructions
        original_instructions = updated_agent.get('instructions', '')
        # Find where the identity section starts
        identity_index = original_instructions.find('═══════════════════════════════════════════════════════════════')
        
        if identity_index > 0:
            base_instructions = original_instructions[:identity_index].strip()
            identity_section = original_instructions[identity_index:]
            
            # Add specialization to instructions
            specialized_instructions = f"""{base_instructions}

SPECIALIZATION: {specialization['specialty']}
FOCUS: {specialization['focus']}
{specialization['description']}

{identity_section}"""
            
            # Update the identity section with new role
            specialized_instructions = specialized_instructions.replace(
                f"Role: {agent.get('display_name', '')}", 
                f"Role: {specialization['specialty']} ({domain})"
            )
            
            updated_agent['instructions'] = specialized_instructions
        
        # Update enhanced metadata
        metadata = updated_agent.get('enhanced_metadata', {})
        metadata['specialization'] = {
            'type': specialization['specialty'],
            'focus': specialization['focus'],
            'description': specialization['description']
        }
        
        # Update capabilities
        capabilities = metadata.get('capabilities', {})
        capabilities['primary_expertise'] = updated_agent['skills'][:3]
        capabilities['secondary_expertise'] = updated_agent['skills'][3:6]
        capabilities['specialization_skills'] = specialization['extra_skills']
        metadata['capabilities'] = capabilities
        
        # Update discovery keywords
        discovery = metadata.get('discovery', {})
        keywords = discovery.get('keywords', [])
        # Add specialization keywords
        for skill in specialization['extra_skills']:
            keyword = skill.lower().replace(' ', '-')
            if keyword not in keywords:
                keywords.append(keyword)
        discovery['keywords'] = keywords
        metadata['discovery'] = discovery
        
        updated_agent['enhanced_metadata'] = metadata
        
        return updated_agent
    
    def process_all_duplicates(self, preview: bool = True):
        """Process all duplicate agents"""
        
        console.print(Panel.fit(
            "[bold cyan]Agent Differentiation Process[/bold cyan]\n"
            "Giving unique specializations to duplicate agents",
            border_style="cyan"
        ))
        
        # Find duplicates
        duplicates = self.find_duplicate_agents()
        
        if not duplicates:
            console.print("[yellow]No duplicate agents found with letter suffixes[/yellow]")
            return
        
        # Show summary
        table = Table(title="Duplicate Agents Found")
        table.add_column("Role", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Suffixes", style="yellow")
        
        for role, agents in duplicates.items():
            suffixes = sorted(set(a['suffix'] for a in agents))
            table.add_row(role, str(len(agents)), ', '.join(suffixes))
        
        console.print(table)
        
        # Process each duplicate
        changes_made = 0
        updated_agents = self.agents.copy()
        
        for role, agent_infos in duplicates.items():
            console.print(f"\n[yellow]Processing {role} variants...[/yellow]")
            
            for agent_info in track(agent_infos, description=f"Differentiating {role}"):
                agent = agent_info['agent']
                suffix = agent_info['suffix']
                index = agent_info['index']
                
                # Apply differentiation
                updated_agent = self.differentiate_agent(agent, role, suffix)
                updated_agents[index] = updated_agent
                changes_made += 1
        
        console.print(f"\n[green]✅ Differentiated {changes_made} agents[/green]")
        
        # Show examples
        self._show_examples(duplicates, updated_agents)
        
        if not preview:
            # Save changes
            self._save_changes(updated_agents)
        else:
            console.print("\n[yellow]⚠️  Preview mode - no changes saved[/yellow]")
            console.print("Run with --execute to apply changes")
    
    def _show_examples(self, duplicates: Dict, updated_agents: List[Dict]):
        """Show example transformations"""
        
        console.print("\n[bold]Example Transformations:[/bold]")
        
        examples_shown = 0
        for role, agent_infos in duplicates.items():
            if examples_shown >= 5:
                break
                
            for agent_info in agent_infos[:2]:  # Show first 2 of each role
                if examples_shown >= 5:
                    break
                    
                index = agent_info['index']
                original = self.agents[index]
                updated = updated_agents[index]
                
                console.print(f"\n[cyan]{original['name']}:[/cyan]")
                console.print(f"  Old: {original.get('display_name', 'Unknown')}")
                console.print(f"  New: [green]{updated.get('display_name', 'Unknown')}[/green]")
                
                # Show skill changes
                old_skills = original.get('skills', [])[:3]
                new_skills = updated.get('skills', [])[:3]
                if old_skills != new_skills:
                    console.print(f"  Skills: {', '.join(old_skills)} → [green]{', '.join(new_skills)}[/green]")
                
                examples_shown += 1
    
    def _save_changes(self, updated_agents: List[Dict]):
        """Save differentiated agents"""
        
        # Create backup
        import shutil
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.config_file}.backup_pre_differentiation_{timestamp}"
        shutil.copy(self.config_file, backup_file)
        console.print(f"\n[green]✅ Created backup: {backup_file}[/green]")
        
        # Save updated agents
        with open(self.config_file, 'w') as f:
            json.dump(updated_agents, f, indent=2)
        
        console.print(f"[green]✅ Saved differentiated agents to {self.config_file}[/green]")
    
    def analyze_current_state(self):
        """Analyze current state of duplicate agents"""
        
        duplicates = self.find_duplicate_agents()
        
        console.print(Panel.fit(
            "[bold cyan]Current Duplicate Agent Analysis[/bold cyan]",
            border_style="cyan"
        ))
        
        for role, agent_infos in duplicates.items():
            console.print(f"\n[bold yellow]{role} Variants:[/bold yellow]")
            
            # Check if they're already differentiated
            skills_by_suffix = {}
            for agent_info in agent_infos:
                agent = agent_info['agent']
                suffix = agent_info['suffix']
                skills = tuple(agent.get('skills', []))
                skills_by_suffix[suffix] = skills
            
            # Check if all have same skills
            unique_skill_sets = set(skills_by_suffix.values())
            if len(unique_skill_sets) == 1:
                console.print(f"  [red]❌ All {len(agent_infos)} variants have identical skills[/red]")
                console.print(f"  Skills: {', '.join(list(unique_skill_sets)[0][:3])}")
            else:
                console.print(f"  [green]✅ Variants have {len(unique_skill_sets)} different skill sets[/green]")
                for suffix, skills in sorted(skills_by_suffix.items()):
                    console.print(f"    {suffix}: {', '.join(skills[:3])}")

def main():
    """CLI for agent differentiation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Differentiate duplicate agents with unique specializations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze current state
  python differentiate_duplicate_agents.py analyze
  
  # Preview differentiation
  python differentiate_duplicate_agents.py differentiate
  
  # Execute differentiation
  python differentiate_duplicate_agents.py differentiate --execute
  
  # Show specialization definitions
  python differentiate_duplicate_agents.py show-specs
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze current duplicate agents')
    analyze_parser.add_argument('--config', default='src/config/agentverse_agents_1000.json',
                               help='Path to agent config file')
    
    # Differentiate command
    diff_parser = subparsers.add_parser('differentiate', help='Differentiate duplicate agents')
    diff_parser.add_argument('--execute', action='store_true',
                            help='Execute differentiation (default is preview)')
    diff_parser.add_argument('--config', default='src/config/agentverse_agents_1000.json',
                            help='Path to agent config file')
    
    # Show specs command
    show_parser = subparsers.add_parser('show-specs', help='Show specialization definitions')
    show_parser.add_argument('--role', help='Show specs for specific role')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        differentiator = AgentDifferentiator(args.config)
        differentiator.analyze_current_state()
    
    elif args.command == 'differentiate':
        differentiator = AgentDifferentiator(args.config)
        differentiator.process_all_duplicates(preview=not args.execute)
    
    elif args.command == 'show-specs':
        differentiator = AgentDifferentiator()
        
        if args.role:
            # Show specific role
            if args.role in differentiator.specializations:
                specs = differentiator.specializations[args.role]
                console.print(f"\n[bold cyan]Specializations for {args.role}:[/bold cyan]")
                for spec in specs:
                    suffix = spec['suffix'] or 'Base'
                    console.print(f"\n[yellow]{suffix}:[/yellow] {spec['specialty']}")
                    console.print(f"  Focus: {spec['focus']}")
                    console.print(f"  Skills: {', '.join(spec['extra_skills'])}")
            else:
                console.print(f"[red]No specializations defined for {args.role}[/red]")
        else:
            # Show all roles
            console.print("[bold cyan]All Role Specializations:[/bold cyan]")
            for role in differentiator.specializations:
                count = len(differentiator.specializations[role])
                console.print(f"\n{role}: {count} specializations defined")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Bulk Agent Transformer - Complete agent standardization
Transforms all 1000+ agents with proper naming, uniqueness, and enhanced metadata
"""

import json
import hashlib
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import shutil
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel
from rich import print as rprint

console = Console()

class BulkAgentTransformer:
    """Transform all agents with standardized naming and enhanced metadata"""
    
    def __init__(self, config_file: str = "src/config/agentverse_agents_1000.json"):
        self.config_file = config_file
        self.agents = []
        self.transformed_agents = []
        self.name_registry = {}  # Track unique names
        self.load_agents()
    
    def load_agents(self):
        """Load existing agents"""
        with open(self.config_file, 'r') as f:
            self.agents = json.load(f)
        console.print(f"[green]✅ Loaded {len(self.agents)} agents[/green]")
    
    def generate_unique_name(self, 
                           base_name: str, 
                           domain: str, 
                           specialty: str, 
                           skills: List[str],
                           sdk: str = "OpenAI",
                           existing_count: int = 0) -> Tuple[str, str]:
        """Generate unique, standardized agent name"""
        
        # Clean up specialty name
        specialty = specialty.replace('_', '').replace(' ', '')
        
        # Map domains to cleaner versions
        domain_map = {
            "engineering": "Engineering",
            "business_workflow": "Business",
            "data_analytics": "DataAnalytics",
            "security": "Security",
            "sre_devops": "DevOps",
            "servicenow": "ServiceNow",
            "customer_support": "Support",
            "project_management": "ProjectMgmt",
            "qa_testing": "QATesting"
        }
        
        domain_clean = domain_map.get(domain.lower(), domain.title())
        
        # Determine role based on specialty and skills
        role = self._determine_role(specialty, skills)
        
        # Generate base standardized name
        if existing_count == 0:
            # First agent of this type - no suffix
            standard_name = f"{sdk}SDK_{domain_clean}_{role}"
            display_name = f"{role} ({domain_clean})"
        else:
            # Add letter suffix for uniqueness (A, B, C, etc.)
            suffix = chr(65 + existing_count)  # A=65, B=66, etc.
            standard_name = f"{sdk}SDK_{domain_clean}_{role}_{suffix}"
            display_name = f"{role} {suffix} ({domain_clean})"
        
        # Ensure uniqueness
        if standard_name in self.name_registry:
            # Add hash suffix if needed
            hash_suffix = hashlib.md5(f"{standard_name}{datetime.now()}".encode()).hexdigest()[:4]
            standard_name = f"{standard_name}_{hash_suffix}"
        
        return standard_name, display_name
    
    def _determine_role(self, specialty: str, skills: List[str]) -> str:
        """Determine clean role name from specialty and skills"""
        
        # Clean up specialty first
        specialty = specialty.lower()
        # Remove numbered suffixes
        specialty = re.sub(r'_\d+$', '', specialty)
        # Remove common suffixes
        for suffix in ['agent', 'developer', 'engineer', 'specialist']:
            specialty = specialty.replace(suffix, '')
        
        # Common role mappings
        role_mappings = {
            # Backend
            "django": "DjangoExpert",
            "fastapi": "FastAPIExpert", 
            "flask": "FlaskExpert",
            "node": "NodeJSExpert",
            "nodejs": "NodeJSExpert",
            "java": "JavaExpert",
            "go": "GoExpert",
            "rust": "RustExpert",
            
            # Frontend  
            "react": "ReactExpert",
            "vue": "VueExpert", 
            "angular": "AngularExpert",
            "frontend": "FrontendExpert",
            "frontendarchitect": "FrontendArchitect",
            
            # Full Stack
            "fullstackdeveloper": "FullStackEngineer",
            "fullstackengineer": "FullStackEngineer",
            
            # Mobile
            "iosdeveloper": "iOSExpert",
            "androiddeveloper": "AndroidExpert",
            "reactnativedeveloper": "ReactNativeExpert",
            "flutterdeveloper": "FlutterExpert",
            
            # Data
            "dataengineer": "DataEngineer",
            "datascientist": "DataScientist",
            "mlengineer": "MLEngineer",
            "dataanalyst": "DataAnalyst",
            "etlengineer": "ETLExpert",
            
            # DevOps
            "devopsengineer": "DevOpsEngineer",
            "sreexpert": "SREExpert",
            "cloudarchitect": "CloudArchitect",
            "kubernetesexpert": "K8sExpert",
            
            # Security
            "security": "SecurityExpert",
            "securityanalyst": "SecurityAnalyst", 
            "pentester": "PenTester",
            "securityengineer": "SecurityEngineer",
            "appsec": "AppSecExpert",
            "threathunting": "ThreatHunter",
            
            # Business
            "salesagent": "SalesSpecialist",
            "marketingagent": "MarketingExpert",
            "financeanalyst": "FinanceAnalyst",
            "hragent": "HRSpecialist",
            "operationsmanager": "OperationsExpert",
            
            # Support
            "supportagent": "SupportSpecialist",
            "techsupport": "TechSupport",
            
            # Project Management
            "projectmanager": "ProjectManager",
            "scrummaster": "ScrumMaster",
            "productowner": "ProductOwner",
            
            # QA
            "qaengineer": "QAEngineer",
            "automationengineer": "AutomationExpert",
            "performancetester": "PerformanceTester"
        }
        
        # Try exact match first
        if specialty in role_mappings:
            return role_mappings[specialty]
        
        # Handle ServiceNow and other specific patterns
        if 'servicenow' in specialty:
            # Extract the service type
            if 'incident' in specialty:
                return "IncidentMgmt"
            elif 'change' in specialty:
                return "ChangeMgmt" 
            elif 'problem' in specialty:
                return "ProblemMgmt"
            elif 'catalog' in specialty:
                return "CatalogMgmt"
            else:
                return "ServiceNowExpert"
        
        # Handle support levels
        if 'supportl1' in specialty or 'l1support' in specialty:
            return "L1Support"
        elif 'supportl2' in specialty or 'l2support' in specialty:
            return "L2Support"
        elif 'supportl3' in specialty or 'l3support' in specialty:
            return "L3Support"
        
        # Handle data roles
        if 'etl' in specialty:
            return "ETLExpert"
        elif 'dataanalyst' in specialty or 'data_analyst' in specialty:
            return "DataAnalyst"
        elif 'datascientist' in specialty or 'data_scientist' in specialty:
            return "DataScientist"
        elif 'ml' in specialty and 'engineer' in specialty:
            return "MLEngineer"
        
        # Try to infer from skills
        if skills:
            primary_skill = skills[0]
            if "Django" in primary_skill:
                return "DjangoExpert"
            elif "React" in primary_skill:
                return "ReactExpert"
            elif "Node" in primary_skill:
                return "NodeJSExpert"
            elif "Python" in primary_skill:
                return "PythonExpert"
            elif "Java" in primary_skill:
                return "JavaExpert"
            elif "Data" in primary_skill:
                return "DataExpert"
            elif "Security" in primary_skill:
                return "SecurityExpert"
            elif "DevOps" in primary_skill:
                return "DevOpsExpert"
        
        # Default: clean up specialty
        role = specialty.replace('Developer', 'Expert').replace('Agent', 'Specialist')
        if not role.endswith(('Expert', 'Engineer', 'Specialist', 'Analyst', 'Architect')):
            role += 'Expert'
        
        return role
    
    def transform_agent(self, agent: Dict, index: int, sdk: str = "OpenAI") -> Dict:
        """Transform single agent with new naming and metadata"""
        
        # Extract current metadata
        metadata = agent.get('enhanced_metadata', {})
        canonical = metadata.get('canonical_name', '')
        
        # Parse domain and specialty
        parts = canonical.split('.')
        domain = parts[1] if len(parts) > 1 else 'general'
        specialty = parts[3] if len(parts) > 3 else agent.get('name', 'Agent')
        
        # Get skills
        skills = agent.get('skills', [])
        
        # Count existing agents of this type
        type_key = f"{domain}_{specialty}"
        existing_count = self.name_registry.get(type_key, 0)
        
        # Generate unique names
        standard_name, display_name = self.generate_unique_name(
            agent.get('name', ''),
            domain,
            specialty,
            skills,
            sdk,
            existing_count
        )
        
        # Update registry
        self.name_registry[standard_name] = True
        self.name_registry[type_key] = existing_count + 1
        
        # Create canonical ID
        canonical_id = f"agent.{sdk.lower()}.{domain}.{specialty.lower()}.{metadata.get('agent_uuid', '')[:8]}"
        
        # Enhanced instructions with proper formatting
        original_instructions = agent.get('instructions', '')
        enhanced_instructions = f"""{original_instructions}

═══════════════════════════════════════════════════════════════
🤖 AGENT IDENTITY
═══════════════════════════════════════════════════════════════
Name: {standard_name}
Role: {display_name}
ID: {canonical_id}
Domain: {domain.title()}
Version: 2.0.0

═══════════════════════════════════════════════════════════════
🎯 CORE COMPETENCIES
═══════════════════════════════════════════════════════════════
Primary Skills: {', '.join(skills[:3])}
Secondary Skills: {', '.join(skills[3:6]) if len(skills) > 3 else 'Adaptive Learning'}
Tools: {', '.join(agent.get('tools', ['analysis', 'planning', 'execution']))}

═══════════════════════════════════════════════════════════════
🤝 COLLABORATION PROTOCOL
═══════════════════════════════════════════════════════════════
Style: Collaborative, Proactive, Solution-Oriented
Communication: Clear, Concise, Professional
Approach: User-Centric, Goal-Focused

Remember: You are {display_name}, an expert in your domain. Always introduce yourself properly and maintain your professional identity."""
        
        # Update agent
        agent['name'] = standard_name
        agent['display_name'] = display_name
        agent['instructions'] = enhanced_instructions
        agent['model'] = 'gpt-4o-mini'  # Standardize model
        
        # Update metadata
        metadata['agent_uuid'] = metadata.get('agent_uuid', hashlib.md5(standard_name.encode()).hexdigest()[:16])
        metadata['canonical_name'] = canonical_id
        metadata['canonical_id'] = canonical_id
        metadata['display_name'] = display_name
        metadata['standard_name'] = standard_name
        metadata['version'] = '2.0.0'
        metadata['naming_version'] = '2.0'
        metadata['updated_at'] = datetime.now().isoformat()
        metadata['legacy_name'] = agent.get('name', 'Unknown')
        metadata['sdk'] = sdk
        
        # Enhance capabilities
        capabilities = metadata.get('capabilities', {})
        capabilities['primary_expertise'] = skills[:3] if skills else ['General']
        capabilities['secondary_expertise'] = skills[3:6] if len(skills) > 3 else []
        capabilities['adaptive_skills'] = ['Learning', 'Problem Solving', 'Communication']
        
        # Enhance collaboration
        collaboration = metadata.get('collaboration', {})
        collaboration['style'] = ['mentor', 'peer', 'learner']
        collaboration['communication_preferences'] = ['structured', 'conversational']
        collaboration['response_format'] = ['detailed', 'concise', 'visual']
        
        metadata['capabilities'] = capabilities
        metadata['collaboration'] = collaboration
        
        # Add discovery tags
        metadata['discovery_tags'] = [
            sdk.lower(),
            domain,
            specialty.lower(),
            'agentverse',
            'ai-agent'
        ] + [skill.lower().replace(' ', '-') for skill in skills[:3]]
        
        # Add search keywords
        metadata['search_keywords'] = [
            standard_name.lower(),
            display_name.lower(),
            domain,
            specialty.lower()
        ] + skills
        
        agent['enhanced_metadata'] = metadata
        
        return agent
    
    def transform_all_agents(self, sdk: str = "OpenAI", preview: bool = True):
        """Transform all agents with progress tracking"""
        
        console.print(f"\n[bold cyan]🚀 Bulk Agent Transformation[/bold cyan]")
        console.print(f"SDK: {sdk}")
        console.print(f"Mode: {'Preview' if preview else 'Execute'}")
        console.print("-" * 60)
        
        # Group agents by type for better organization
        agent_groups = defaultdict(list)
        for agent in self.agents:
            canonical = agent.get('enhanced_metadata', {}).get('canonical_name', '')
            domain = canonical.split('.')[1] if '.' in canonical else 'general'
            agent_groups[domain].append(agent)
        
        # Transform agents
        self.transformed_agents = []
        total_transformed = 0
        
        for domain, domain_agents in agent_groups.items():
            console.print(f"\n[yellow]Processing {domain} ({len(domain_agents)} agents)...[/yellow]")
            
            for i, agent in enumerate(track(domain_agents, description=f"Transforming {domain}")):
                transformed = self.transform_agent(agent.copy(), total_transformed, sdk)
                self.transformed_agents.append(transformed)
                total_transformed += 1
        
        # Generate summary
        self._generate_summary()
        
        if not preview:
            self.save_transformed_agents()
        else:
            console.print("\n[yellow]⚠️  Preview mode - no changes saved[/yellow]")
            console.print("Run with --execute to apply transformations")
    
    def _generate_summary(self):
        """Generate transformation summary"""
        
        # Create summary table
        table = Table(title="Transformation Summary")
        table.add_column("Domain", style="cyan")
        table.add_column("Count", style="green")
        table.add_column("Sample Names", style="yellow")
        
        # Group by domain
        by_domain = defaultdict(list)
        for agent in self.transformed_agents:
            domain = agent.get('enhanced_metadata', {}).get('sdk', 'Unknown')
            domain_name = agent['name'].split('_')[1] if '_' in agent['name'] else 'Unknown'
            by_domain[domain_name].append(agent['name'])
        
        for domain, names in by_domain.items():
            sample_names = ', '.join(names[:3])
            if len(names) > 3:
                sample_names += f" ... +{len(names)-3} more"
            table.add_row(domain, str(len(names)), sample_names)
        
        console.print(table)
        
        # Show sample transformations
        console.print("\n[bold]Sample Transformations:[/bold]")
        for i, agent in enumerate(self.transformed_agents[:5]):
            # Get the original agent name
            if i < len(self.agents):
                old_name = self.agents[i].get('name', 'Unknown')
            else:
                old_name = agent.get('enhanced_metadata', {}).get('legacy_name', 'Unknown')
            new_name = agent['name']
            display = agent.get('display_name', 'Unknown')
            console.print(f"  {old_name} → [green]{new_name}[/green] ({display})")
    
    def save_transformed_agents(self):
        """Save transformed agents with backup"""
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.config_file}.backup_pre_transform_{timestamp}"
        shutil.copy(self.config_file, backup_file)
        console.print(f"\n[green]✅ Created backup: {backup_file}[/green]")
        
        # Save transformed agents
        with open(self.config_file, 'w') as f:
            json.dump(self.transformed_agents, f, indent=2)
        
        console.print(f"[green]✅ Saved {len(self.transformed_agents)} transformed agents[/green]")
    
    def validate_transformations(self):
        """Validate all transformations"""
        
        issues = []
        name_counts = defaultdict(int)
        
        for agent in self.transformed_agents:
            name = agent.get('name', '')
            name_counts[name] += 1
            
            # Check for duplicates
            if name_counts[name] > 1:
                issues.append(f"Duplicate name: {name}")
            
            # Check required fields
            if not agent.get('instructions'):
                issues.append(f"Missing instructions: {name}")
            
            if not agent.get('enhanced_metadata', {}).get('canonical_id'):
                issues.append(f"Missing canonical_id: {name}")
        
        if issues:
            console.print(f"\n[red]❌ Found {len(issues)} issues:[/red]")
            for issue in issues[:10]:
                console.print(f"  - {issue}")
        else:
            console.print("\n[green]✅ All transformations valid![/green]")

def main():
    """CLI for bulk agent transformation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Bulk Agent Transformer - Standardize all agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview transformation
  python bulk_agent_transformer.py transform
  
  # Execute transformation with OpenAI SDK
  python bulk_agent_transformer.py transform --execute --sdk OpenAI
  
  # Transform with different SDK
  python bulk_agent_transformer.py transform --execute --sdk Anthropic
  
  # Validate after transformation
  python bulk_agent_transformer.py validate
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Transform command
    transform_parser = subparsers.add_parser('transform', help='Transform all agents')
    transform_parser.add_argument('--sdk', default='OpenAI', 
                                 choices=['OpenAI', 'Anthropic', 'Google', 'Ollama', 'AgentVerse'],
                                 help='SDK prefix to use')
    transform_parser.add_argument('--execute', action='store_true', 
                                 help='Execute transformation (default is preview)')
    transform_parser.add_argument('--config', default='src/config/agentverse_agents_1000.json',
                                 help='Path to agent config file')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate transformations')
    validate_parser.add_argument('--config', default='src/config/agentverse_agents_1000.json',
                                help='Path to agent config file')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show transformation examples')
    show_parser.add_argument('--count', type=int, default=10, help='Number of examples to show')
    
    args = parser.parse_args()
    
    if args.command == 'transform':
        transformer = BulkAgentTransformer(args.config)
        transformer.transform_all_agents(
            sdk=args.sdk,
            preview=not args.execute
        )
        
        if args.execute:
            transformer.validate_transformations()
    
    elif args.command == 'validate':
        transformer = BulkAgentTransformer(args.config)
        # Load and validate without transforming
        transformer.transformed_agents = transformer.agents
        transformer.validate_transformations()
    
    elif args.command == 'show':
        console.print("[bold cyan]Agent Name Transformation Examples[/bold cyan]\n")
        
        examples = [
            ("DjangoDeveloper_1", "OpenAISDK_Engineering_DjangoExpert"),
            ("ReactDeveloper_2", "OpenAISDK_Engineering_ReactExpert_A"),
            ("DataEngineer_1", "OpenAISDK_DataAnalytics_DataEngineer"),
            ("SalesAgent_3", "OpenAISDK_Business_SalesSpecialist_B"),
            ("SecurityAnalyst_1", "OpenAISDK_Security_SecurityAnalyst"),
            ("MLEngineer_2", "OpenAISDK_DataAnalytics_MLEngineer_A"),
            ("DevOpsEngineer_4", "OpenAISDK_DevOps_DevOpsEngineer_C"),
            ("ProjectManager_1", "OpenAISDK_ProjectMgmt_ProjectManager"),
        ]
        
        for old, new in examples[:args.count]:
            console.print(f"  {old} → [green]{new}[/green]")
        
        console.print("\n[yellow]Naming Pattern:[/yellow]")
        console.print("  {SDK}SDK_{Domain}_{Role}[_{Suffix}]")
        console.print("\n[yellow]Benefits:[/yellow]")
        console.print("  ✓ Platform discoverable (Google A2A/ADK compatible)")
        console.print("  ✓ Self-documenting names")
        console.print("  ✓ No numeric suffixes")
        console.print("  ✓ Clear role identification")
        console.print("  ✓ SDK/Platform clarity")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
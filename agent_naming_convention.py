#!/usr/bin/env python3
"""
AgentVerse Naming Convention System
Implements standardized naming for agent discoverability
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import hashlib

class AgentNamingConvention:
    """
    Standard naming format: {SDK}_{Domain}_{Specialty}_{Variant}
    
    Examples:
    - OpenAISDK_Engineering_DjangoDeveloper_v1
    - OllamaSDK_DataAnalytics_MLEngineer_v2
    - AgentVerseSDK_Security_PenTester_v1
    """
    
    # SDK Prefixes
    SDK_PREFIXES = {
        "openai": "OpenAISDK",
        "ollama": "OllamaSDK",
        "anthropic": "AnthropicSDK",
        "google": "GoogleSDK",
        "agentverse": "AgentVerseSDK",
        "custom": "CustomSDK"
    }
    
    # Domain Mappings
    DOMAIN_MAPPINGS = {
        "engineering": "Engineering",
        "business_workflow": "Business",
        "data_analytics": "DataAnalytics",
        "security": "Security",
        "sre_devops": "SREDevOps",
        "servicenow": "ServiceNow",
        "customer_support": "Support",
        "project_management": "ProjectMgmt",
        "qa_testing": "QATesting"
    }
    
    # Specialty Normalization
    SPECIALTY_MAPPINGS = {
        # Engineering
        "backend_development": "Backend",
        "frontend_development": "Frontend",
        "full_stack": "FullStack",
        "mobile_development": "Mobile",
        "devops": "DevOps",
        
        # Specific Technologies
        "django": "Django",
        "react": "React",
        "node": "NodeJS",
        "python": "Python",
        "java": "Java",
        "kubernetes": "K8s",
        "docker": "Docker",
        
        # Data
        "data_engineering": "DataEng",
        "data_science": "DataSci",
        "ml_engineering": "MLEng",
        "analytics": "Analytics",
        
        # Business
        "sales": "Sales",
        "marketing": "Marketing",
        "finance": "Finance",
        "hr": "HR",
        "operations": "Operations"
    }
    
    @staticmethod
    def generate_standard_name(
        agent_config: Dict,
        sdk: str = "agentverse",
        include_version: bool = True,
        include_uuid_suffix: bool = False
    ) -> str:
        """Generate standardized agent name"""
        
        metadata = agent_config.get('enhanced_metadata', {})
        canonical = metadata.get('canonical_name', '')
        
        # Extract components from canonical name
        parts = canonical.split('.')
        
        # Get SDK prefix
        sdk_prefix = AgentNamingConvention.SDK_PREFIXES.get(sdk.lower(), "AgentVerseSDK")
        
        # Get domain
        domain = "Unknown"
        for part in parts:
            if part in AgentNamingConvention.DOMAIN_MAPPINGS:
                domain = AgentNamingConvention.DOMAIN_MAPPINGS[part]
                break
        
        # Get specialty
        specialty = "Agent"
        display_name = metadata.get('display_name', '')
        
        # Try to extract specialty from display name
        if 'Django' in display_name:
            specialty = "DjangoDeveloper"
        elif 'React' in display_name:
            specialty = "ReactDeveloper"
        elif 'Node' in display_name:
            specialty = "NodeDeveloper"
        elif 'Python' in display_name:
            specialty = "PythonDeveloper"
        elif 'Data' in display_name and 'Engineer' in display_name:
            specialty = "DataEngineer"
        elif 'Data' in display_name and 'Scientist' in display_name:
            specialty = "DataScientist"
        elif 'ML' in display_name:
            specialty = "MLEngineer"
        elif 'DevOps' in display_name:
            specialty = "DevOpsEngineer"
        elif 'Security' in display_name:
            specialty = "SecurityExpert"
        elif 'Sales' in display_name:
            specialty = "SalesAgent"
        elif 'Marketing' in display_name:
            specialty = "MarketingAgent"
        else:
            # Extract from skills
            skills = agent_config.get('skills', [])
            if skills:
                primary_skill = skills[0].replace(' ', '')
                specialty = f"{primary_skill}Expert"
        
        # Build name components
        name_parts = [sdk_prefix, domain, specialty]
        
        # Add version
        if include_version:
            version = metadata.get('version', '1.0.0').replace('.', '')
            name_parts.append(f"v{version[0]}")
        
        # Add UUID suffix for uniqueness
        if include_uuid_suffix:
            uuid = metadata.get('agent_uuid', '')[:4]
            name_parts.append(uuid)
        
        return '_'.join(name_parts)
    
    @staticmethod
    def generate_canonical_id(standard_name: str) -> str:
        """Generate a canonical ID for agent discovery"""
        # Format: agentverse.{sdk}.{domain}.{specialty}.{hash}
        
        parts = standard_name.split('_')
        sdk = parts[0].replace('SDK', '').lower()
        domain = parts[1].lower() if len(parts) > 1 else 'general'
        specialty = parts[2].lower() if len(parts) > 2 else 'agent'
        
        # Generate short hash for uniqueness
        hash_input = f"{standard_name}{datetime.now().isoformat()}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        
        return f"agentverse.{sdk}.{domain}.{specialty}.{short_hash}"
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, List[str]]:
        """Validate agent name against naming convention"""
        issues = []
        
        # Check format
        parts = name.split('_')
        
        if len(parts) < 3:
            issues.append("Name must have at least 3 parts: SDK_Domain_Specialty")
        
        # Check SDK prefix
        if parts[0] not in AgentNamingConvention.SDK_PREFIXES.values():
            issues.append(f"Invalid SDK prefix: {parts[0]}")
        
        # Check domain
        if len(parts) > 1 and parts[1] not in AgentNamingConvention.DOMAIN_MAPPINGS.values():
            issues.append(f"Unknown domain: {parts[1]}")
        
        # Check for special characters
        if not re.match(r'^[A-Za-z0-9_]+$', name):
            issues.append("Name contains invalid characters")
        
        # Check length
        if len(name) > 100:
            issues.append("Name too long (max 100 characters)")
        
        return len(issues) == 0, issues
    
    @staticmethod
    def parse_name(name: str) -> Dict[str, str]:
        """Parse standardized name into components"""
        parts = name.split('_')
        
        result = {
            "full_name": name,
            "sdk": parts[0] if len(parts) > 0 else None,
            "domain": parts[1] if len(parts) > 1 else None,
            "specialty": parts[2] if len(parts) > 2 else None,
            "version": parts[3] if len(parts) > 3 else None,
            "suffix": parts[4] if len(parts) > 4 else None
        }
        
        return result

class AgentNamingMigrator:
    """Migrate existing agents to new naming convention"""
    
    def __init__(self, config_file: str = "src/config/agentverse_agents_1000.json"):
        self.config_file = config_file
        self.agents = []
        self.naming_convention = AgentNamingConvention()
        self.load_agents()
    
    def load_agents(self):
        """Load agents from config"""
        with open(self.config_file, 'r') as f:
            self.agents = json.load(f)
    
    def migrate_all_agents(self, sdk: str = "agentverse", dry_run: bool = True):
        """Migrate all agents to new naming convention"""
        migrations = []
        
        for i, agent in enumerate(self.agents):
            old_name = agent.get('name', '')
            metadata = agent.get('enhanced_metadata', {})
            
            # Generate new standardized name
            new_name = self.naming_convention.generate_standard_name(
                agent, 
                sdk=sdk,
                include_version=True,
                include_uuid_suffix=False
            )
            
            # Generate canonical ID
            canonical_id = self.naming_convention.generate_canonical_id(new_name)
            
            # Validate new name
            is_valid, issues = self.naming_convention.validate_name(new_name)
            
            migration = {
                "index": i,
                "old_name": old_name,
                "new_name": new_name,
                "canonical_id": canonical_id,
                "is_valid": is_valid,
                "issues": issues,
                "agent_uuid": metadata.get('agent_uuid', '')
            }
            
            migrations.append(migration)
            
            if not dry_run and is_valid:
                # Update agent
                agent['name'] = new_name
                agent['standardized_name'] = new_name
                metadata['canonical_id'] = canonical_id
                metadata['naming_version'] = "2.0"
                metadata['legacy_name'] = old_name
        
        if not dry_run:
            self.save_agents()
        
        return migrations
    
    def save_agents(self):
        """Save updated agents"""
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{self.config_file}.pre_naming_{timestamp}"
        
        import shutil
        shutil.copy(self.config_file, backup_file)
        
        # Save updated agents
        with open(self.config_file, 'w') as f:
            json.dump(self.agents, f, indent=2)
        
        print(f"✅ Saved updated agents (backup: {backup_file})")
    
    def generate_migration_report(self, migrations: List[Dict]) -> str:
        """Generate detailed migration report"""
        report = []
        report.append("=== Agent Naming Migration Report ===\n")
        report.append(f"Total agents: {len(migrations)}")
        
        valid_count = sum(1 for m in migrations if m['is_valid'])
        report.append(f"Valid names: {valid_count}")
        report.append(f"Issues found: {len(migrations) - valid_count}\n")
        
        # Group by domain
        by_domain = {}
        for m in migrations:
            parsed = self.naming_convention.parse_name(m['new_name'])
            domain = parsed.get('domain', 'Unknown')
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(m)
        
        report.append("By Domain:")
        for domain, agents in by_domain.items():
            report.append(f"  {domain}: {len(agents)} agents")
        
        report.append("\nSample Migrations:")
        for m in migrations[:10]:
            report.append(f"\n  Old: {m['old_name']}")
            report.append(f"  New: {m['new_name']}")
            report.append(f"  ID:  {m['canonical_id']}")
            if not m['is_valid']:
                report.append(f"  Issues: {', '.join(m['issues'])}")
        
        return '\n'.join(report)

def main():
    """CLI for naming convention tools"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Naming Convention Tools")
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Test naming
    test_parser = subparsers.add_parser('test', help='Test naming for specific agent')
    test_parser.add_argument('agent_name', help='Current agent name')
    test_parser.add_argument('--sdk', default='agentverse', help='SDK to use')
    
    # Migrate command
    migrate_parser = subparsers.add_parser('migrate', help='Migrate all agents')
    migrate_parser.add_argument('--sdk', default='agentverse', help='SDK to use')
    migrate_parser.add_argument('--execute', action='store_true', help='Execute migration (not dry run)')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate agent name')
    validate_parser.add_argument('name', help='Name to validate')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Generate naming report')
    
    args = parser.parse_args()
    
    if args.command == 'test':
        # Test naming for a specific agent
        # This is a simplified test - in real use, load the actual agent
        test_agent = {
            "name": args.agent_name,
            "enhanced_metadata": {
                "agent_uuid": "test123",
                "canonical_name": "agentverse.engineering.backend.django",
                "display_name": args.agent_name,
                "version": "1.0.0"
            },
            "skills": ["Django", "Python", "API"]
        }
        
        convention = AgentNamingConvention()
        new_name = convention.generate_standard_name(test_agent, sdk=args.sdk)
        canonical_id = convention.generate_canonical_id(new_name)
        
        print(f"Original: {args.agent_name}")
        print(f"New Name: {new_name}")
        print(f"Canonical ID: {canonical_id}")
        
        is_valid, issues = convention.validate_name(new_name)
        if is_valid:
            print("✅ Valid name")
        else:
            print("❌ Issues:", ', '.join(issues))
    
    elif args.command == 'migrate':
        migrator = AgentNamingMigrator()
        migrations = migrator.migrate_all_agents(
            sdk=args.sdk, 
            dry_run=not args.execute
        )
        
        report = migrator.generate_migration_report(migrations)
        print(report)
        
        if not args.execute:
            print("\n⚠️  This was a dry run. Use --execute to apply changes.")
    
    elif args.command == 'validate':
        convention = AgentNamingConvention()
        is_valid, issues = convention.validate_name(args.name)
        
        print(f"Name: {args.name}")
        if is_valid:
            print("✅ Valid")
            parsed = convention.parse_name(args.name)
            print("Components:")
            for key, value in parsed.items():
                if value:
                    print(f"  {key}: {value}")
        else:
            print("❌ Invalid")
            for issue in issues:
                print(f"  - {issue}")
    
    elif args.command == 'report':
        migrator = AgentNamingMigrator()
        
        # Analyze current naming
        print("=== Current Agent Naming Analysis ===\n")
        
        name_patterns = {}
        for agent in migrator.agents:
            name = agent.get('name', '')
            pattern = "Unknown"
            
            if '_' in name:
                parts = len(name.split('_'))
                pattern = f"{parts}_parts"
            elif name.endswith(('_1', '_2', '_3')):
                pattern = "numbered_suffix"
            else:
                pattern = "other"
            
            if pattern not in name_patterns:
                name_patterns[pattern] = 0
            name_patterns[pattern] += 1
        
        print("Current naming patterns:")
        for pattern, count in name_patterns.items():
            print(f"  {pattern}: {count} agents")
        
        # Show what migration would do
        print("\n=== Proposed Standardization ===")
        migrations = migrator.migrate_all_agents(dry_run=True)
        print(migrator.generate_migration_report(migrations))
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
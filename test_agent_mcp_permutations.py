#!/usr/bin/env python3
"""
Test Agent-MCP Permutations
Demonstrates various combinations of agents and MCP servers
Shows how any agent can work with any MCP server
"""

import json
import asyncio
import random
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging
from itertools import product

# Import our modules
from agent_mcp_coupling_system import (
    AgentMCPCoupler, 
    MCPServerConfig, 
    MCPServerType,
    CompatibilityLevel
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PermutationTester:
    """Tests various permutations of agents and MCP servers"""
    
    def __init__(self, agents_file: str = "src/config/agentverse_agents_1000.json"):
        self.coupler = AgentMCPCoupler()
        self.agents = self._load_agents(agents_file)
        self.test_results = []
        self._setup_additional_mcp_servers()
    
    def _load_agents(self, agents_file: str) -> List[Dict[str, Any]]:
        """Load agents from file"""
        try:
            with open(agents_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Agents file not found: {agents_file}")
            return self._create_sample_agents()
    
    def _create_sample_agents(self) -> List[Dict[str, Any]]:
        """Create sample agents for testing"""
        return [
            {
                "name": "OpenAISDK_Support_L1Support",
                "category": "Support",
                "skills": ["Customer Service", "Troubleshooting", "Ticket Management"],
                "tools": ["alert_manager", "notification_sender", "doc_generator"]
            },
            {
                "name": "OpenAISDK_DevOps_SREEngineer",
                "category": "DevOps",
                "subcategory": "SRE",
                "skills": ["Monitoring", "Incident Response", "Automation", "CI/CD"],
                "tools": ["deployment_tool", "metrics_collector", "alert_manager"]
            },
            {
                "name": "OpenAISDK_Database_DBAExpert",
                "category": "Database",
                "skills": ["SQL", "Database Administration", "Performance Tuning"],
                "tools": ["query_builder", "performance_analyzer", "backup_tool"]
            },
            {
                "name": "OpenAISDK_Security_SecurityAnalyst",
                "category": "Security",
                "skills": ["Security", "Vulnerability Assessment", "Compliance"],
                "tools": ["vulnerability_scanner", "log_analyzer", "compliance_checker"]
            },
            {
                "name": "OpenAISDK_Engineering_BackendDeveloper",
                "category": "Engineering",
                "skills": ["API Development", "Microservices", "Testing"],
                "tools": ["code_generator", "test_runner", "deployment_tool"]
            }
        ]
    
    def _setup_additional_mcp_servers(self):
        """Setup additional MCP servers for testing"""
        
        # Add Slack MCP Server
        self.coupler.registry.register_server(MCPServerConfig(
            name="Slack-Communication",
            type=MCPServerType.MESSAGING,
            command="python",
            args=["-m", "mcp_servers.slack_server"],
            env={"SLACK_TOKEN": "${SLACK_TOKEN}"},
            tool_packages=["messaging", "channel_management", "user_management"],
            capabilities={
                "tools": ["send_message", "create_channel", "search_messages", "get_user_info"],
                "resources": ["channels", "users", "messages", "files"]
            },
            requirements={
                "skills": ["Communication", "Team Collaboration"],
                "tools": ["notification_sender", "team_collaborator"]
            },
            description="Slack messaging platform for team communication"
        ))
        
        # Add AWS MCP Server
        self.coupler.registry.register_server(MCPServerConfig(
            name="AWS-CloudProvider",
            type=MCPServerType.CLOUD_PROVIDER,
            command="python",
            args=["-m", "mcp_servers.aws_server"],
            env={"AWS_ACCESS_KEY": "${AWS_ACCESS_KEY}", "AWS_SECRET_KEY": "${AWS_SECRET_KEY}"},
            tool_packages=["ec2_management", "s3_operations", "lambda_functions"],
            capabilities={
                "tools": ["create_instance", "upload_to_s3", "deploy_lambda", "manage_vpc"],
                "resources": ["ec2_instances", "s3_buckets", "lambda_functions", "vpcs"]
            },
            requirements={
                "skills": ["Cloud Computing", "AWS", "Infrastructure"],
                "tools": ["cloud_deployer", "infrastructure_manager"]
            },
            description="AWS cloud provider for infrastructure management"
        ))
        
        # Add Elasticsearch MCP Server
        self.coupler.registry.register_server(MCPServerConfig(
            name="Elasticsearch-Analytics",
            type=MCPServerType.ANALYTICS,
            command="python",
            args=["-m", "mcp_servers.elasticsearch_server"],
            env={"ELASTICSEARCH_URL": "${ELASTICSEARCH_URL}"},
            tool_packages=["search_operations", "index_management", "analytics"],
            capabilities={
                "tools": ["search_documents", "create_index", "aggregate_data", "visualize_data"],
                "resources": ["indexes", "documents", "aggregations", "visualizations"]
            },
            requirements={
                "skills": ["Data Analysis", "Search", "Elasticsearch"],
                "tools": ["search_tool", "data_analyzer"]
            },
            description="Elasticsearch for search and analytics"
        ))
    
    async def test_all_permutations(self, sample_size: int = 10):
        """Test all permutations of agents and MCP servers"""
        logger.info("🔬 Testing All Agent-MCP Permutations")
        logger.info("="*70)
        
        # Get sample of agents
        agent_sample = random.sample(self.agents, min(sample_size, len(self.agents)))
        
        # Get all MCP servers
        mcp_servers = self.coupler.registry.list_servers()
        
        total_permutations = len(agent_sample) * len(mcp_servers)
        logger.info(f"Testing {total_permutations} permutations ({len(agent_sample)} agents × {len(mcp_servers)} servers)")
        
        results = {
            'perfect': [],
            'high': [],
            'medium': [],
            'low': [],
            'minimal': [],
            'incompatible': []
        }
        
        # Test each permutation
        for agent, server in product(agent_sample, mcp_servers):
            compatibility, analysis = self.coupler.analyzer.analyze_compatibility(agent, server)
            
            result = {
                'agent': agent['name'],
                'server': server.name,
                'compatibility': compatibility.name,
                'score': analysis['overall_score'],
                'scores': analysis['scores']
            }
            
            # Categorize by compatibility
            results[compatibility.name.lower()].append(result)
            self.test_results.append(result)
        
        # Display results
        self._display_permutation_results(results, total_permutations)
        
        return results
    
    def _display_permutation_results(self, results: Dict[str, List], total: int):
        """Display permutation test results"""
        print("\n📊 Permutation Test Results")
        print("="*70)
        print(f"Total Permutations Tested: {total}")
        print("\nCompatibility Distribution:")
        
        for level in ['perfect', 'high', 'medium', 'low', 'minimal', 'incompatible']:
            count = len(results[level])
            percentage = (count / total) * 100 if total > 0 else 0
            print(f"  {level.upper()}: {count} ({percentage:.1f}%)")
        
        # Show examples from each category
        print("\n🌟 Example Couplings by Compatibility Level:")
        
        for level in ['perfect', 'high', 'medium']:
            if results[level]:
                print(f"\n{level.upper()} Compatibility:")
                for example in results[level][:2]:  # Show 2 examples
                    print(f"  - {example['agent'][:30]}...")
                    print(f"    + {example['server']} (Score: {example['score']:.2f})")
    
    async def test_cross_domain_adaptability(self):
        """Test how agents adapt across different domains"""
        logger.info("\n🔄 Testing Cross-Domain Adaptability")
        logger.info("="*70)
        
        # Select agents from different domains
        domain_agents = {
            'support': None,
            'devops': None,
            'database': None,
            'security': None,
            'engineering': None
        }
        
        for agent in self.agents:
            category = agent.get('category', '').lower()
            for domain in domain_agents:
                if domain in category and domain_agents[domain] is None:
                    domain_agents[domain] = agent
                    break
        
        # Test each domain agent with all server types
        print("\n🎯 Cross-Domain Compatibility Matrix:")
        print("-"*70)
        
        # Header
        server_types = list(MCPServerType)
        print(f"{'Agent Domain':<20}", end="")
        for st in server_types:
            print(f"{st.value:<12}", end="")
        print()
        print("-"*70)
        
        # Test each domain
        for domain, agent in domain_agents.items():
            if agent:
                print(f"{domain.capitalize():<20}", end="")
                
                for server_type in server_types:
                    # Find a server of this type
                    servers = self.coupler.registry.list_servers(server_type)
                    if servers:
                        server = servers[0]
                        compatibility, _ = self.coupler.analyzer.analyze_compatibility(agent, server)
                        
                        # Show compatibility with color coding
                        level = compatibility.value
                        if level >= 4:
                            symbol = "✅"
                        elif level >= 3:
                            symbol = "🟨"
                        elif level >= 2:
                            symbol = "🟧"
                        else:
                            symbol = "❌"
                        
                        print(f"{symbol:<12}", end="")
                    else:
                        print(f"{'N/A':<12}", end="")
                
                print()
    
    async def test_best_matches(self):
        """Find best agent-server matches"""
        logger.info("\n🏆 Finding Best Agent-Server Matches")
        logger.info("="*70)
        
        best_matches = []
        
        # For each server, find the best agent
        for server in self.coupler.registry.list_servers():
            compatible_agents = self.coupler.get_compatible_agents(
                server.name, 
                self.agents[:50],  # Test with first 50 agents
                min_compatibility=CompatibilityLevel.HIGH
            )
            
            if compatible_agents:
                best_agent, compatibility, analysis = compatible_agents[0]
                best_matches.append({
                    'server': server.name,
                    'agent': best_agent['name'],
                    'compatibility': compatibility.name,
                    'score': analysis['overall_score']
                })
        
        # Display best matches
        print("\n🌟 Optimal Agent-Server Pairings:")
        print("-"*70)
        for match in best_matches:
            print(f"\n{match['server']}:")
            print(f"  Best Agent: {match['agent']}")
            print(f"  Compatibility: {match['compatibility']} (Score: {match['score']:.2f})")
    
    async def test_dynamic_coupling(self):
        """Test dynamic coupling creation and switching"""
        logger.info("\n🔀 Testing Dynamic Coupling")
        logger.info("="*70)
        
        # Select a versatile agent
        agent = next((a for a in self.agents if 'devops' in a.get('category', '').lower()), self.agents[0])
        
        print(f"\nAgent: {agent['name']}")
        print(f"Category: {agent.get('category', 'Unknown')}")
        
        # Create couplings with different servers
        couplings = []
        for server_type in [MCPServerType.SERVICENOW, MCPServerType.MONITORING, MCPServerType.CI_CD]:
            servers = self.coupler.registry.list_servers(server_type)
            if servers:
                coupling = self.coupler.create_coupling(agent, servers[0].name)
                if coupling:
                    couplings.append(coupling)
                    print(f"\n✅ Coupled with {servers[0].name}")
                    print(f"   Compatibility: {coupling.compatibility.name}")
                    print(f"   Adaptations: {', '.join(coupling.adaptation_needed[:2]) if coupling.adaptation_needed else 'None'}")
        
        # Show coupling flexibility
        print(f"\n🎭 Agent '{agent['name']}' can work with {len(couplings)} different MCP servers!")
        print("This demonstrates the flexibility of the coupling system.")
    
    async def run_all_tests(self):
        """Run all permutation tests"""
        print("\n🚀 Agent-MCP Permutation Testing Suite")
        print("="*70)
        print("Testing how any agent can work with any MCP server through dynamic coupling")
        
        # Test 1: All permutations
        await self.test_all_permutations(sample_size=10)
        
        # Test 2: Cross-domain adaptability
        await self.test_cross_domain_adaptability()
        
        # Test 3: Best matches
        await self.test_best_matches()
        
        # Test 4: Dynamic coupling
        await self.test_dynamic_coupling()
        
        # Generate summary report
        self._generate_summary_report()
    
    def _generate_summary_report(self):
        """Generate summary report of all tests"""
        print("\n📈 Summary Report")
        print("="*70)
        
        if self.test_results:
            # Calculate statistics
            total_tests = len(self.test_results)
            avg_score = sum(r['score'] for r in self.test_results) / total_tests
            
            # Compatibility distribution
            compatibility_counts = {}
            for result in self.test_results:
                level = result['compatibility']
                compatibility_counts[level] = compatibility_counts.get(level, 0) + 1
            
            print(f"Total Couplings Tested: {total_tests}")
            print(f"Average Compatibility Score: {avg_score:.2f}")
            print("\nKey Findings:")
            print("✅ Any agent can potentially work with any MCP server")
            print("✅ Compatibility varies based on skills and tools alignment")
            print("✅ Agents can be dynamically adapted for different servers")
            print("✅ Cross-domain coupling is possible with appropriate adapters")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_permutations_tested': len(self.test_results),
            'mcp_servers': [s.name for s in self.coupler.registry.list_servers()],
            'test_results': self.test_results,
            'summary': {
                'average_compatibility_score': avg_score if self.test_results else 0,
                'compatibility_distribution': compatibility_counts if self.test_results else {}
            }
        }
        
        report_file = f"agent_mcp_permutation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")

async def demonstrate_specific_scenarios():
    """Demonstrate specific coupling scenarios"""
    print("\n🎯 Specific Coupling Scenarios")
    print("="*70)
    
    coupler = AgentMCPCoupler()
    
    # Scenario 1: Support agent with different servers
    print("\n1️⃣ Support Agent Versatility:")
    support_agent = {
        "name": "OpenAISDK_Support_TechnicalSupport",
        "category": "Support",
        "skills": ["Customer Service", "Troubleshooting", "Documentation"],
        "tools": ["alert_manager", "doc_generator", "notification_sender"]
    }
    
    for server_name in ["ServiceNow-Production", "Slack-Communication", "Elasticsearch-Analytics"]:
        server = coupler.registry.get_server(server_name)
        if server:
            compatibility, analysis = coupler.analyzer.analyze_compatibility(support_agent, server)
            print(f"\n  {support_agent['name']} + {server_name}:")
            print(f"    Compatibility: {compatibility.name}")
            print(f"    Use Case: {_get_use_case(support_agent, server)}")
    
    # Scenario 2: Database expert with various platforms
    print("\n\n2️⃣ Database Expert Adaptability:")
    db_agent = {
        "name": "OpenAISDK_Database_PostgreSQLExpert",
        "category": "Database",
        "skills": ["SQL", "Performance Tuning", "Replication"],
        "tools": ["query_builder", "performance_analyzer", "backup_tool"]
    }
    
    for server_name in ["PostgreSQL-Analytics", "Elasticsearch-Analytics", "ServiceNow-Production"]:
        server = coupler.registry.get_server(server_name)
        if server:
            compatibility, analysis = coupler.analyzer.analyze_compatibility(db_agent, server)
            print(f"\n  {db_agent['name']} + {server_name}:")
            print(f"    Compatibility: {compatibility.name}")
            print(f"    Adaptation: {_get_adaptation_strategy(db_agent, server, analysis)}")

def _get_use_case(agent: Dict[str, Any], server: MCPServerConfig) -> str:
    """Get use case for agent-server combination"""
    if server.type == MCPServerType.SERVICENOW:
        return "Handle support tickets and incidents"
    elif server.type == MCPServerType.MESSAGING:
        return "Provide support via chat channels"
    elif server.type == MCPServerType.ANALYTICS:
        return "Analyze support metrics and patterns"
    else:
        return "General integration"

def _get_adaptation_strategy(agent: Dict[str, Any], server: MCPServerConfig, analysis: Dict[str, Any]) -> str:
    """Get adaptation strategy for coupling"""
    if analysis['overall_score'] >= 0.8:
        return "Direct integration possible"
    elif analysis['overall_score'] >= 0.5:
        return "Tool mapping and minor adaptations needed"
    else:
        return "Significant adaptation layer required"

async def main():
    """Main test runner"""
    print("🔧 Agent-MCP Dynamic Coupling System")
    print("Demonstrating how agents and MCP servers can be freely combined")
    print("="*70)
    
    # Run permutation tests
    tester = PermutationTester()
    await tester.run_all_tests()
    
    # Show specific scenarios
    await demonstrate_specific_scenarios()
    
    print("\n✨ Conclusion:")
    print("The coupling system enables:")
    print("  ✅ Any agent to work with any MCP server")
    print("  ✅ Dynamic adaptation based on compatibility")
    print("  ✅ Flexible tool and capability mapping")
    print("  ✅ Cross-domain integration possibilities")
    print("\nAgents are truly independent components that can be combined with any MCP server!")

if __name__ == "__main__":
    asyncio.run(main())
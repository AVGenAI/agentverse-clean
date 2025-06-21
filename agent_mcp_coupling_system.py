#!/usr/bin/env python3
"""
Agent-MCP Coupling System
Allows dynamic pairing of any AgentVerse agent with any MCP server
Enables permutations and combinations of agents and MCP servers
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
from abc import ABC, abstractmethod

# MCP imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.server.fastmcp import FastMCP

# Import our modules
from mcp_agent_client import AgentMCPClient
from servicenow_agent_adapter import ServiceNowAgentAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPServerType(Enum):
    """Types of MCP servers"""
    SERVICENOW = "servicenow"
    DATABASE = "database"
    MONITORING = "monitoring"
    CLOUD_PROVIDER = "cloud_provider"
    CI_CD = "ci_cd"
    MESSAGING = "messaging"
    ANALYTICS = "analytics"
    SECURITY = "security"
    CUSTOM = "custom"

class CompatibilityLevel(Enum):
    """Agent-MCP compatibility levels"""
    PERFECT = 5      # Agent designed for this MCP server
    HIGH = 4         # Agent has most required capabilities
    MEDIUM = 3       # Agent has some relevant capabilities
    LOW = 2          # Agent can adapt with limitations
    MINIMAL = 1      # Basic compatibility only
    INCOMPATIBLE = 0 # Not compatible

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    type: MCPServerType
    command: str
    args: List[str]
    env: Dict[str, str] = field(default_factory=dict)
    tool_packages: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    connection_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AgentMCPCoupling:
    """Represents a coupling between an agent and MCP server"""
    agent_id: str
    agent_name: str
    mcp_server: MCPServerConfig
    compatibility: CompatibilityLevel
    capability_mapping: Dict[str, str]
    adaptation_needed: List[str]
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    active: bool = False
    session: Optional[ClientSession] = None
    created_at: datetime = field(default_factory=datetime.now)

class AgentAdapter(ABC):
    """Abstract base for agent adapters"""
    
    @abstractmethod
    def adapt_agent_for_mcp(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> Dict[str, Any]:
        """Adapt agent configuration for specific MCP server"""
        pass
    
    @abstractmethod
    def translate_request(self, agent_request: Dict[str, Any], mcp_format: str) -> Dict[str, Any]:
        """Translate agent request to MCP server format"""
        pass
    
    @abstractmethod
    def translate_response(self, mcp_response: Dict[str, Any], agent_format: str) -> Dict[str, Any]:
        """Translate MCP response back to agent format"""
        pass

class UniversalAgentAdapter(AgentAdapter):
    """Universal adapter that can adapt any agent to any MCP server"""
    
    def __init__(self):
        self.adapters = {
            MCPServerType.SERVICENOW: ServiceNowAgentAdapter(),
            # Add more specific adapters as needed
        }
    
    def adapt_agent_for_mcp(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> Dict[str, Any]:
        """Adapt agent configuration for specific MCP server"""
        # Use specific adapter if available
        if mcp_server.type in self.adapters:
            return self.adapters[mcp_server.type].adapt_agent_for_servicenow(agent_config)
        
        # Generic adaptation
        adapted = agent_config.copy()
        adapted['mcp_metadata'] = {
            'server_type': mcp_server.type.value,
            'server_name': mcp_server.name,
            'adapted_at': datetime.now().isoformat(),
            'tool_mapping': self._create_tool_mapping(agent_config, mcp_server),
            'capability_alignment': self._align_capabilities(agent_config, mcp_server)
        }
        
        return adapted
    
    def translate_request(self, agent_request: Dict[str, Any], mcp_format: str) -> Dict[str, Any]:
        """Translate agent request to MCP server format"""
        # Generic translation
        return {
            'tool': agent_request.get('tool', 'unknown'),
            'parameters': agent_request.get('params', {}),
            'metadata': {
                'source': 'agentverse',
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def translate_response(self, mcp_response: Dict[str, Any], agent_format: str) -> Dict[str, Any]:
        """Translate MCP response back to agent format"""
        # Generic translation
        return {
            'success': True,
            'data': mcp_response,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_tool_mapping(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> Dict[str, str]:
        """Create mapping between agent tools and MCP server tools"""
        mapping = {}
        agent_tools = agent_config.get('tools', [])
        
        # Simple heuristic mapping
        for agent_tool in agent_tools:
            # Try to find similar MCP tool
            for mcp_tool in mcp_server.capabilities.get('tools', []):
                if self._tools_are_similar(agent_tool, mcp_tool):
                    mapping[agent_tool] = mcp_tool
                    break
        
        return mapping
    
    def _align_capabilities(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> Dict[str, Any]:
        """Align agent capabilities with MCP server capabilities"""
        alignment = {
            'matched': [],
            'missing': [],
            'extra': []
        }
        
        agent_skills = set(agent_config.get('skills', []))
        mcp_requirements = set(mcp_server.requirements.get('skills', []))
        
        alignment['matched'] = list(agent_skills & mcp_requirements)
        alignment['missing'] = list(mcp_requirements - agent_skills)
        alignment['extra'] = list(agent_skills - mcp_requirements)
        
        return alignment
    
    def _tools_are_similar(self, tool1: str, tool2: str) -> bool:
        """Check if two tools are similar based on name"""
        # Simple similarity check - can be enhanced
        tool1_parts = set(tool1.lower().split('_'))
        tool2_parts = set(tool2.lower().split('_'))
        
        return len(tool1_parts & tool2_parts) > 0

class MCPServerRegistry:
    """Registry of available MCP servers"""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self._initialize_default_servers()
    
    def _initialize_default_servers(self):
        """Initialize with default MCP servers"""
        
        # ServiceNow MCP Server
        self.register_server(MCPServerConfig(
            name="ServiceNow-Production",
            type=MCPServerType.SERVICENOW,
            command="python",
            args=["-m", "src.servicenow_mcp_server.server"],
            env={
                "SERVICENOW_INSTANCE_URL": "${SERVICENOW_INSTANCE_URL}",
                "SERVICENOW_USERNAME": "${SERVICENOW_USERNAME}",
                "SERVICENOW_PASSWORD": "${SERVICENOW_PASSWORD}"
            },
            tool_packages=["incident_management", "change_management", "service_catalog"],
            capabilities={
                "tools": ["create_incident", "update_incident", "search_incidents", 
                         "create_change_request", "create_knowledge_article"],
                "resources": ["incidents", "changes", "problems", "knowledge"],
                "workflows": ["incident_resolution", "change_implementation"]
            },
            requirements={
                "skills": ["ITIL", "ServiceNow Platform", "Incident Management"],
                "tools": ["alert_manager", "workflow_orchestrator"]
            },
            description="ServiceNow ITSM platform for IT service management"
        ))
        
        # Database MCP Server (hypothetical)
        self.register_server(MCPServerConfig(
            name="PostgreSQL-Analytics",
            type=MCPServerType.DATABASE,
            command="python",
            args=["-m", "mcp_servers.postgres_server"],
            env={"DATABASE_URL": "${DATABASE_URL}"},
            tool_packages=["query_execution", "schema_management", "performance_monitoring"],
            capabilities={
                "tools": ["execute_query", "analyze_query", "optimize_table", "backup_database"],
                "resources": ["tables", "views", "indexes", "statistics"]
            },
            requirements={
                "skills": ["SQL", "Database Administration", "Performance Tuning"],
                "tools": ["query_builder", "performance_analyzer"]
            },
            description="PostgreSQL database server with analytics capabilities"
        ))
        
        # Monitoring MCP Server (hypothetical)
        self.register_server(MCPServerConfig(
            name="Prometheus-Monitoring",
            type=MCPServerType.MONITORING,
            command="python",
            args=["-m", "mcp_servers.prometheus_server"],
            env={"PROMETHEUS_URL": "${PROMETHEUS_URL}"},
            tool_packages=["metrics_query", "alert_management", "dashboard_creation"],
            capabilities={
                "tools": ["query_metrics", "create_alert", "update_dashboard", "analyze_trends"],
                "resources": ["metrics", "alerts", "dashboards", "targets"]
            },
            requirements={
                "skills": ["Monitoring", "PromQL", "SRE"],
                "tools": ["metrics_collector", "alert_manager"]
            },
            description="Prometheus monitoring system with alerting"
        ))
        
        # CI/CD MCP Server (hypothetical)
        self.register_server(MCPServerConfig(
            name="Jenkins-CICD",
            type=MCPServerType.CI_CD,
            command="python",
            args=["-m", "mcp_servers.jenkins_server"],
            env={"JENKINS_URL": "${JENKINS_URL}", "JENKINS_TOKEN": "${JENKINS_TOKEN}"},
            tool_packages=["job_management", "pipeline_execution", "artifact_handling"],
            capabilities={
                "tools": ["trigger_job", "get_build_status", "deploy_artifact", "run_tests"],
                "resources": ["jobs", "pipelines", "artifacts", "nodes"]
            },
            requirements={
                "skills": ["CI/CD", "DevOps", "Jenkins"],
                "tools": ["deployment_tool", "test_runner"]
            },
            description="Jenkins CI/CD server for continuous integration and deployment"
        ))
    
    def register_server(self, server: MCPServerConfig):
        """Register a new MCP server"""
        self.servers[server.name] = server
        logger.info(f"Registered MCP server: {server.name} ({server.type.value})")
    
    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """Get server by name"""
        return self.servers.get(name)
    
    def list_servers(self, server_type: Optional[MCPServerType] = None) -> List[MCPServerConfig]:
        """List all servers or filter by type"""
        servers = list(self.servers.values())
        if server_type:
            servers = [s for s in servers if s.type == server_type]
        return servers

class CompatibilityAnalyzer:
    """Analyzes compatibility between agents and MCP servers"""
    
    def __init__(self):
        self.skill_weights = {
            'exact_match': 1.0,
            'partial_match': 0.5,
            'related_match': 0.3
        }
    
    def analyze_compatibility(
        self, 
        agent_config: Dict[str, Any], 
        mcp_server: MCPServerConfig
    ) -> Tuple[CompatibilityLevel, Dict[str, Any]]:
        """Analyze compatibility between agent and MCP server"""
        
        scores = {
            'skill_score': self._calculate_skill_score(agent_config, mcp_server),
            'tool_score': self._calculate_tool_score(agent_config, mcp_server),
            'domain_score': self._calculate_domain_score(agent_config, mcp_server),
            'capability_score': self._calculate_capability_score(agent_config, mcp_server)
        }
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Determine compatibility level
        if overall_score >= 0.8:
            level = CompatibilityLevel.PERFECT
        elif overall_score >= 0.6:
            level = CompatibilityLevel.HIGH
        elif overall_score >= 0.4:
            level = CompatibilityLevel.MEDIUM
        elif overall_score >= 0.2:
            level = CompatibilityLevel.LOW
        elif overall_score > 0:
            level = CompatibilityLevel.MINIMAL
        else:
            level = CompatibilityLevel.INCOMPATIBLE
        
        analysis = {
            'scores': scores,
            'overall_score': overall_score,
            'level': level,
            'recommendations': self._generate_recommendations(agent_config, mcp_server, scores)
        }
        
        return level, analysis
    
    def _calculate_skill_score(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> float:
        """Calculate skill compatibility score"""
        agent_skills = set(skill.lower() for skill in agent_config.get('skills', []))
        required_skills = set(skill.lower() for skill in mcp_server.requirements.get('skills', []))
        
        if not required_skills:
            return 1.0  # No specific skills required
        
        exact_matches = len(agent_skills & required_skills)
        score = exact_matches / len(required_skills)
        
        return min(score, 1.0)
    
    def _calculate_tool_score(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> float:
        """Calculate tool compatibility score"""
        agent_tools = set(agent_config.get('tools', []))
        required_tools = set(mcp_server.requirements.get('tools', []))
        
        if not required_tools:
            return 1.0  # No specific tools required
        
        matches = len(agent_tools & required_tools)
        score = matches / len(required_tools)
        
        return min(score, 1.0)
    
    def _calculate_domain_score(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> float:
        """Calculate domain compatibility score"""
        agent_category = agent_config.get('category', '').lower()
        agent_subcategory = agent_config.get('subcategory', '').lower()
        
        # Domain mapping
        domain_map = {
            MCPServerType.SERVICENOW: ['support', 'devops', 'sre', 'incident'],
            MCPServerType.DATABASE: ['database', 'data', 'analytics', 'dba'],
            MCPServerType.MONITORING: ['monitoring', 'sre', 'devops', 'observability'],
            MCPServerType.CI_CD: ['devops', 'engineering', 'deployment', 'ci/cd'],
            MCPServerType.SECURITY: ['security', 'compliance', 'audit']
        }
        
        relevant_domains = domain_map.get(mcp_server.type, [])
        
        score = 0.0
        for domain in relevant_domains:
            if domain in agent_category or domain in agent_subcategory:
                score = 1.0
                break
            elif any(word in domain for word in agent_category.split()):
                score = max(score, 0.5)
        
        return score
    
    def _calculate_capability_score(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> float:
        """Calculate capability alignment score"""
        agent_capabilities = agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {})
        mcp_capabilities = mcp_server.capabilities
        
        if not mcp_capabilities:
            return 1.0
        
        score = 0.0
        capability_count = 0
        
        # Check workflow capabilities
        if 'workflows' in mcp_capabilities:
            agent_workflows = agent_capabilities.get('workflows', {})
            if agent_workflows:
                capability_count += 1
                score += 0.5  # Partial score for having workflows
        
        # Check resource handling
        if 'resources' in mcp_capabilities:
            capability_count += 1
            if agent_capabilities.get('can_handle_resources'):
                score += 1.0
        
        return score / capability_count if capability_count > 0 else 0.5
    
    def _generate_recommendations(
        self, 
        agent_config: Dict[str, Any], 
        mcp_server: MCPServerConfig,
        scores: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for improving compatibility"""
        recommendations = []
        
        if scores['skill_score'] < 0.5:
            missing_skills = set(mcp_server.requirements.get('skills', [])) - set(agent_config.get('skills', []))
            if missing_skills:
                recommendations.append(f"Consider adding skills: {', '.join(missing_skills)}")
        
        if scores['tool_score'] < 0.5:
            recommendations.append("Agent lacks required tools for optimal MCP server interaction")
        
        if scores['domain_score'] < 0.5:
            recommendations.append(f"Agent's domain ({agent_config.get('category', 'Unknown')}) may not align well with {mcp_server.type.value}")
        
        return recommendations

class AgentMCPCoupler:
    """Main class for coupling agents with MCP servers"""
    
    def __init__(self):
        self.registry = MCPServerRegistry()
        self.adapter = UniversalAgentAdapter()
        self.analyzer = CompatibilityAnalyzer()
        self.active_couplings: Dict[str, AgentMCPCoupling] = {}
    
    def create_coupling(
        self, 
        agent_config: Dict[str, Any], 
        mcp_server_name: str
    ) -> Optional[AgentMCPCoupling]:
        """Create a coupling between an agent and MCP server"""
        
        # Get MCP server
        mcp_server = self.registry.get_server(mcp_server_name)
        if not mcp_server:
            logger.error(f"MCP server '{mcp_server_name}' not found")
            return None
        
        # Analyze compatibility
        compatibility, analysis = self.analyzer.analyze_compatibility(agent_config, mcp_server)
        
        # Create capability mapping
        capability_mapping = self._create_capability_mapping(agent_config, mcp_server)
        
        # Determine adaptations needed
        adaptations = self._determine_adaptations(agent_config, mcp_server, analysis)
        
        # Create coupling
        coupling = AgentMCPCoupling(
            agent_id=agent_config.get('enhanced_metadata', {}).get('agent_uuid', 'unknown'),
            agent_name=agent_config.get('name', 'Unknown'),
            mcp_server=mcp_server,
            compatibility=compatibility,
            capability_mapping=capability_mapping,
            adaptation_needed=adaptations,
            performance_metrics={
                'compatibility_analysis': analysis,
                'created_at': datetime.now().isoformat()
            }
        )
        
        # Store coupling
        coupling_id = f"{coupling.agent_id}_{mcp_server.name}"
        self.active_couplings[coupling_id] = coupling
        
        logger.info(f"Created coupling: {coupling.agent_name} <-> {mcp_server.name} (Compatibility: {compatibility.name})")
        
        return coupling
    
    def _create_capability_mapping(
        self, 
        agent_config: Dict[str, Any], 
        mcp_server: MCPServerConfig
    ) -> Dict[str, str]:
        """Create mapping between agent and MCP capabilities"""
        mapping = {}
        
        # Tool mapping
        agent_tools = agent_config.get('tools', [])
        mcp_tools = mcp_server.capabilities.get('tools', [])
        
        for agent_tool in agent_tools:
            best_match = None
            best_score = 0
            
            for mcp_tool in mcp_tools:
                score = self._calculate_similarity(agent_tool, mcp_tool)
                if score > best_score:
                    best_score = score
                    best_match = mcp_tool
            
            if best_match and best_score > 0.3:  # Threshold for mapping
                mapping[agent_tool] = best_match
        
        return mapping
    
    def _determine_adaptations(
        self,
        agent_config: Dict[str, Any],
        mcp_server: MCPServerConfig,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Determine what adaptations are needed"""
        adaptations = []
        
        if analysis['scores']['skill_score'] < 1.0:
            adaptations.append("Skill enhancement required")
        
        if analysis['scores']['tool_score'] < 1.0:
            adaptations.append("Tool mapping and translation needed")
        
        if analysis['scores']['domain_score'] < 0.5:
            adaptations.append("Domain-specific training recommended")
        
        if not self._has_required_tools(agent_config, mcp_server):
            adaptations.append("Tool adapters required for missing capabilities")
        
        return adaptations
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        # Simple word overlap similarity
        words1 = set(str1.lower().replace('_', ' ').split())
        words2 = set(str2.lower().replace('_', ' ').split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _has_required_tools(self, agent_config: Dict[str, Any], mcp_server: MCPServerConfig) -> bool:
        """Check if agent has required tools"""
        agent_tools = set(agent_config.get('tools', []))
        required_tools = set(mcp_server.requirements.get('tools', []))
        
        return len(agent_tools & required_tools) >= len(required_tools) * 0.5
    
    async def activate_coupling(self, coupling_id: str) -> bool:
        """Activate a coupling and establish connection"""
        coupling = self.active_couplings.get(coupling_id)
        if not coupling:
            logger.error(f"Coupling '{coupling_id}' not found")
            return False
        
        try:
            # Create MCP client
            client = AgentMCPClient(coupling.agent_name, coupling.agent_id)
            
            # Setup server parameters
            server_params = StdioServerParameters(
                command=coupling.mcp_server.command,
                args=coupling.mcp_server.args,
                env=coupling.mcp_server.env
            )
            
            # Establish connection
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    coupling.session = session
                    coupling.active = True
                    
                    logger.info(f"Activated coupling: {coupling.agent_name} <-> {coupling.mcp_server.name}")
                    
                    # Test connection
                    tools = await session.list_tools()
                    logger.info(f"Available tools: {len(tools.tools)}")
                    
                    return True
                    
        except Exception as e:
            logger.error(f"Failed to activate coupling: {e}")
            coupling.active = False
            return False
    
    def get_compatible_servers(
        self, 
        agent_config: Dict[str, Any],
        min_compatibility: CompatibilityLevel = CompatibilityLevel.LOW
    ) -> List[Tuple[MCPServerConfig, CompatibilityLevel, Dict[str, Any]]]:
        """Get all compatible MCP servers for an agent"""
        compatible_servers = []
        
        for server in self.registry.list_servers():
            compatibility, analysis = self.analyzer.analyze_compatibility(agent_config, server)
            
            if compatibility.value >= min_compatibility.value:
                compatible_servers.append((server, compatibility, analysis))
        
        # Sort by compatibility level
        compatible_servers.sort(key=lambda x: x[1].value, reverse=True)
        
        return compatible_servers
    
    def get_compatible_agents(
        self,
        mcp_server_name: str,
        agents: List[Dict[str, Any]],
        min_compatibility: CompatibilityLevel = CompatibilityLevel.LOW
    ) -> List[Tuple[Dict[str, Any], CompatibilityLevel, Dict[str, Any]]]:
        """Get all compatible agents for an MCP server"""
        server = self.registry.get_server(mcp_server_name)
        if not server:
            return []
        
        compatible_agents = []
        
        for agent in agents:
            compatibility, analysis = self.analyzer.analyze_compatibility(agent, server)
            
            if compatibility.value >= min_compatibility.value:
                compatible_agents.append((agent, compatibility, analysis))
        
        # Sort by compatibility level
        compatible_agents.sort(key=lambda x: x[1].value, reverse=True)
        
        return compatible_agents
    
    def create_optimal_couplings(
        self,
        agents: List[Dict[str, Any]],
        servers: Optional[List[str]] = None
    ) -> List[AgentMCPCoupling]:
        """Create optimal couplings between agents and servers"""
        if servers is None:
            servers = list(self.registry.servers.keys())
        
        couplings = []
        
        for agent in agents:
            best_server = None
            best_compatibility = CompatibilityLevel.INCOMPATIBLE
            
            for server_name in servers:
                server = self.registry.get_server(server_name)
                if server:
                    compatibility, _ = self.analyzer.analyze_compatibility(agent, server)
                    
                    if compatibility.value > best_compatibility.value:
                        best_compatibility = compatibility
                        best_server = server_name
            
            if best_server and best_compatibility.value >= CompatibilityLevel.LOW.value:
                coupling = self.create_coupling(agent, best_server)
                if coupling:
                    couplings.append(coupling)
        
        return couplings
    
    def generate_coupling_report(self) -> Dict[str, Any]:
        """Generate report on all active couplings"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_couplings': len(self.active_couplings),
            'active_couplings': sum(1 for c in self.active_couplings.values() if c.active),
            'compatibility_distribution': {},
            'server_usage': {},
            'couplings': []
        }
        
        # Analyze couplings
        for coupling_id, coupling in self.active_couplings.items():
            # Update compatibility distribution
            level = coupling.compatibility.name
            report['compatibility_distribution'][level] = report['compatibility_distribution'].get(level, 0) + 1
            
            # Update server usage
            server_name = coupling.mcp_server.name
            report['server_usage'][server_name] = report['server_usage'].get(server_name, 0) + 1
            
            # Add coupling details
            report['couplings'].append({
                'id': coupling_id,
                'agent': coupling.agent_name,
                'server': coupling.mcp_server.name,
                'compatibility': coupling.compatibility.name,
                'active': coupling.active,
                'adaptations': coupling.adaptation_needed
            })
        
        return report

# Example usage functions
async def demonstrate_coupling_system():
    """Demonstrate the agent-MCP coupling system"""
    
    # Create coupler
    coupler = AgentMCPCoupler()
    
    print("🔧 Agent-MCP Coupling System Demo")
    print("="*60)
    
    # Load sample agents
    with open("src/config/agentverse_agents_1000.json", 'r') as f:
        agents = json.load(f)[:5]  # Use first 5 agents for demo
    
    # Show available MCP servers
    print("\n📡 Available MCP Servers:")
    for server in coupler.registry.list_servers():
        print(f"  - {server.name} ({server.type.value})")
        print(f"    Tools: {len(server.capabilities.get('tools', []))}")
        print(f"    Description: {server.description}")
    
    # Test compatibility for each agent
    print("\n🔍 Testing Agent Compatibility:")
    print("-"*60)
    
    for agent in agents:
        print(f"\nAgent: {agent['name']}")
        print(f"Category: {agent.get('category', 'Unknown')}")
        
        # Get compatible servers
        compatible_servers = coupler.get_compatible_servers(agent)
        
        if compatible_servers:
            print("Compatible MCP Servers:")
            for server, compatibility, analysis in compatible_servers[:3]:
                print(f"  - {server.name}: {compatibility.name}")
                print(f"    Overall Score: {analysis['overall_score']:.2f}")
                if analysis['recommendations']:
                    print(f"    Recommendations: {analysis['recommendations'][0]}")
        else:
            print("  No compatible servers found")
    
    # Create optimal couplings
    print("\n🔗 Creating Optimal Couplings:")
    print("-"*60)
    
    couplings = coupler.create_optimal_couplings(agents)
    
    for coupling in couplings:
        print(f"\n✅ Coupled: {coupling.agent_name} <-> {coupling.mcp_server.name}")
        print(f"   Compatibility: {coupling.compatibility.name}")
        print(f"   Tool Mappings: {len(coupling.capability_mapping)}")
        print(f"   Adaptations Needed: {', '.join(coupling.adaptation_needed) if coupling.adaptation_needed else 'None'}")
    
    # Generate report
    report = coupler.generate_coupling_report()
    
    print("\n📊 Coupling Summary Report:")
    print("-"*60)
    print(f"Total Couplings: {report['total_couplings']}")
    print(f"Active Couplings: {report['active_couplings']}")
    print("\nCompatibility Distribution:")
    for level, count in report['compatibility_distribution'].items():
        print(f"  {level}: {count}")
    print("\nServer Usage:")
    for server, count in report['server_usage'].items():
        print(f"  {server}: {count} agents")
    
    # Test activation (if ServiceNow is available)
    if couplings:
        print("\n🚀 Testing Coupling Activation:")
        coupling_id = f"{couplings[0].agent_id}_{couplings[0].mcp_server.name}"
        
        try:
            # Note: This will fail if the MCP server isn't actually running
            success = await coupler.activate_coupling(coupling_id)
            if success:
                print(f"✅ Successfully activated coupling!")
            else:
                print(f"❌ Failed to activate coupling (server may not be running)")
        except Exception as e:
            print(f"⚠️  Activation test skipped: {e}")
    
    print("\n✨ Agent-MCP Coupling System Ready!")
    print("   - Agents can be dynamically paired with any MCP server")
    print("   - Compatibility is automatically analyzed")
    print("   - Adaptations are suggested for better integration")

if __name__ == "__main__":
    asyncio.run(demonstrate_coupling_system())
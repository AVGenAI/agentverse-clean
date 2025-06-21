#!/usr/bin/env python3
"""
ServiceNow Agent Adapter
Adapts AgentVerse agents to work seamlessly with ServiceNow MCP server
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceNowToolMapping:
    """Maps agent capabilities to ServiceNow tools"""
    agent_tool: str
    servicenow_tool: str
    parameter_mapping: Dict[str, str]
    category: str

class ServiceNowAgentAdapter:
    """Adapts AgentVerse agents for ServiceNow integration"""
    
    def __init__(self):
        self.tool_mappings = self._initialize_tool_mappings()
        self.skill_mappings = self._initialize_skill_mappings()
    
    def _initialize_tool_mappings(self) -> Dict[str, ServiceNowToolMapping]:
        """Initialize mappings between agent tools and ServiceNow tools"""
        return {
            # Incident Management
            "alert_manager": ServiceNowToolMapping(
                agent_tool="alert_manager",
                servicenow_tool="create_incident",
                parameter_mapping={
                    "alert_title": "short_description",
                    "alert_description": "description",
                    "severity": "urgency",
                    "alert_source": "category"
                },
                category="incident_management"
            ),
            
            # Change Management
            "deployment_tool": ServiceNowToolMapping(
                agent_tool="deployment_tool",
                servicenow_tool="create_change_request",
                parameter_mapping={
                    "deployment_name": "short_description",
                    "deployment_description": "description",
                    "environment": "category",
                    "risk_level": "risk"
                },
                category="change_management"
            ),
            
            # Service Catalog
            "workflow_orchestrator": ServiceNowToolMapping(
                agent_tool="workflow_orchestrator",
                servicenow_tool="create_request",
                parameter_mapping={
                    "workflow_name": "short_description",
                    "workflow_params": "description",
                    "priority": "urgency"
                },
                category="service_catalog"
            ),
            
            # Knowledge Management
            "doc_generator": ServiceNowToolMapping(
                agent_tool="doc_generator",
                servicenow_tool="create_knowledge_article",
                parameter_mapping={
                    "doc_title": "short_description",
                    "doc_content": "text",
                    "doc_category": "category"
                },
                category="knowledge_management"
            ),
            
            # User Management
            "team_collaborator": ServiceNowToolMapping(
                agent_tool="team_collaborator",
                servicenow_tool="get_user",
                parameter_mapping={
                    "user_id": "user_name",
                    "user_email": "email"
                },
                category="user_management"
            )
        }
    
    def _initialize_skill_mappings(self) -> Dict[str, List[str]]:
        """Map agent skills to ServiceNow capabilities"""
        return {
            # Technical Skills to ServiceNow Roles
            "Incident Response": ["incident_management", "problem_management"],
            "Security": ["security_operations", "vulnerability_management"],
            "DevOps": ["change_management", "release_management"],
            "Monitoring": ["event_management", "service_mapping"],
            "Documentation": ["knowledge_management"],
            "Project Management": ["project_portfolio_management"],
            "Customer Service": ["service_desk", "request_fulfillment"],
            
            # Platform Skills
            "API Design": ["integration_hub", "flow_designer"],
            "Automation": ["orchestration", "workflow_automation"],
            "Testing": ["test_management", "automated_testing"],
            "Compliance": ["compliance_management", "audit_management"]
        }
    
    def adapt_agent_for_servicenow(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt an agent configuration for ServiceNow integration
        
        Args:
            agent_config: Original agent configuration
            
        Returns:
            ServiceNow-adapted configuration
        """
        adapted = agent_config.copy()
        
        # Add ServiceNow metadata
        adapted['servicenow_metadata'] = {
            'adapted_at': datetime.now().isoformat(),
            'tool_packages': self._determine_tool_packages(agent_config),
            'servicenow_roles': self._map_skills_to_roles(agent_config.get('skills', [])),
            'integration_capabilities': self._get_integration_capabilities(agent_config)
        }
        
        # Enhance instructions for ServiceNow context
        adapted['instructions'] = self._enhance_instructions_for_servicenow(
            agent_config.get('instructions', ''),
            agent_config
        )
        
        # Add ServiceNow-specific tools
        adapted['servicenow_tools'] = self._get_servicenow_tools(agent_config)
        
        return adapted
    
    def _determine_tool_packages(self, agent_config: Dict[str, Any]) -> List[str]:
        """Determine appropriate ServiceNow tool packages for agent"""
        packages = set()
        
        # Based on category
        category = agent_config.get('category', '').lower()
        category_mappings = {
            'support': ['service_desk', 'incident_management'],
            'engineering': ['developer', 'catalog_builder'],
            'devops': ['change_coordinator', 'deployment_management'],
            'security': ['security_operations', 'vulnerability_management'],
            'business': ['business_analyst', 'project_manager']
        }
        
        for key, pkgs in category_mappings.items():
            if key in category:
                packages.update(pkgs)
        
        # Based on skills
        for skill in agent_config.get('skills', []):
            if 'incident' in skill.lower():
                packages.add('incident_management')
            elif 'change' in skill.lower():
                packages.add('change_management')
            elif 'catalog' in skill.lower():
                packages.add('service_catalog')
            elif 'knowledge' in skill.lower():
                packages.add('knowledge_management')
        
        return list(packages)
    
    def _map_skills_to_roles(self, skills: List[str]) -> List[str]:
        """Map agent skills to ServiceNow roles"""
        roles = set()
        
        for skill in skills:
            # Direct mappings
            if skill in self.skill_mappings:
                roles.update(self.skill_mappings[skill])
            
            # Pattern-based mappings
            skill_lower = skill.lower()
            if 'security' in skill_lower:
                roles.add('security_operations')
            elif 'database' in skill_lower:
                roles.add('cmdb_management')
            elif 'api' in skill_lower:
                roles.add('integration_hub')
            elif 'test' in skill_lower:
                roles.add('test_management')
        
        return list(roles)
    
    def _get_integration_capabilities(self, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Determine integration capabilities with ServiceNow"""
        tools = agent_config.get('tools', [])
        capabilities = agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {})
        
        return {
            'can_create_incidents': any(tool in ['alert_manager', 'monitoring_tool'] for tool in tools),
            'can_manage_changes': any(tool in ['deployment_tool', 'k8s_deployer'] for tool in tools),
            'can_update_cmdb': 'dependency_analyzer' in tools,
            'can_create_knowledge': 'doc_generator' in tools,
            'can_automate_workflows': 'workflow_orchestrator' in tools,
            'supports_orchestration': len(capabilities.get('workflows', {})) > 0,
            'has_monitoring': any(tool in ['metrics_collector', 'log_analyzer'] for tool in tools)
        }
    
    def _enhance_instructions_for_servicenow(
        self, 
        instructions: str, 
        agent_config: Dict[str, Any]
    ) -> str:
        """Enhance agent instructions with ServiceNow context"""
        
        servicenow_context = f"""

═══════════════════════════════════════════════════════════════
🔧 SERVICENOW INTEGRATION
═══════════════════════════════════════════════════════════════
This agent is enhanced with ServiceNow platform capabilities:

Tool Packages: {', '.join(self._determine_tool_packages(agent_config))}
Integration Points:
- Incident Management: Create, update, and resolve incidents
- Change Management: Submit and track change requests
- Service Catalog: Access and fulfill service requests
- Knowledge Base: Create and search knowledge articles

When interacting with ServiceNow:
1. Follow ITIL best practices
2. Maintain proper categorization and priority
3. Include all required fields for ServiceNow records
4. Use ServiceNow terminology and conventions

Available ServiceNow Commands:
- Create incidents for alerts and issues
- Submit change requests for deployments
- Search knowledge base for solutions
- Update CMDB with discovered assets
"""
        
        return instructions + servicenow_context
    
    def _get_servicenow_tools(self, agent_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get ServiceNow-specific tools for the agent"""
        servicenow_tools = []
        agent_tools = agent_config.get('tools', [])
        
        for agent_tool in agent_tools:
            if agent_tool in self.tool_mappings:
                mapping = self.tool_mappings[agent_tool]
                servicenow_tools.append({
                    'name': mapping.servicenow_tool,
                    'category': mapping.category,
                    'original_tool': agent_tool,
                    'parameter_mapping': mapping.parameter_mapping
                })
        
        # Add default ServiceNow tools based on category
        category = agent_config.get('category', '').lower()
        if 'support' in category:
            servicenow_tools.extend([
                {'name': 'search_incidents', 'category': 'incident_management'},
                {'name': 'update_incident', 'category': 'incident_management'},
                {'name': 'create_incident_task', 'category': 'incident_management'}
            ])
        elif 'devops' in category or 'engineering' in category:
            servicenow_tools.extend([
                {'name': 'create_change_request', 'category': 'change_management'},
                {'name': 'create_change_task', 'category': 'change_management'},
                {'name': 'assess_change_risk', 'category': 'change_management'}
            ])
        
        return servicenow_tools
    
    def translate_agent_request_to_servicenow(
        self,
        agent_tool: str,
        agent_params: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Translate agent tool request to ServiceNow format
        
        Args:
            agent_tool: Agent tool name
            agent_params: Agent tool parameters
            
        Returns:
            ServiceNow tool request or None if not mappable
        """
        if agent_tool not in self.tool_mappings:
            return None
        
        mapping = self.tool_mappings[agent_tool]
        
        # Translate parameters
        servicenow_params = {}
        for agent_param, servicenow_param in mapping.parameter_mapping.items():
            if agent_param in agent_params:
                servicenow_params[servicenow_param] = agent_params[agent_param]
        
        return {
            'tool': mapping.servicenow_tool,
            'parameters': servicenow_params,
            'category': mapping.category
        }
    
    def translate_servicenow_response_to_agent(
        self,
        servicenow_response: Dict[str, Any],
        original_tool: str
    ) -> Dict[str, Any]:
        """Translate ServiceNow response back to agent format
        
        Args:
            servicenow_response: Response from ServiceNow
            original_tool: Original agent tool that was called
            
        Returns:
            Agent-formatted response
        """
        # Generic translation
        agent_response = {
            'success': servicenow_response.get('result', 'success') == 'success',
            'data': servicenow_response,
            'tool': original_tool,
            'timestamp': datetime.now().isoformat()
        }
        
        # Tool-specific translations
        if original_tool == 'alert_manager' and 'sys_id' in servicenow_response:
            agent_response['incident_id'] = servicenow_response['sys_id']
            agent_response['incident_number'] = servicenow_response.get('number', 'Unknown')
        elif original_tool == 'deployment_tool' and 'sys_id' in servicenow_response:
            agent_response['change_id'] = servicenow_response['sys_id']
            agent_response['change_number'] = servicenow_response.get('number', 'Unknown')
        
        return agent_response

# Example usage
def demonstrate_adapter():
    """Demonstrate the ServiceNow adapter"""
    adapter = ServiceNowAgentAdapter()
    
    # Example agent configuration
    example_agent = {
        "name": "OpenAISDK_Support_L1Support",
        "category": "Support",
        "skills": ["Incident Response", "Customer Service", "Troubleshooting"],
        "tools": ["alert_manager", "notification_sender", "doc_generator"],
        "instructions": "You are a Level 1 Support specialist."
    }
    
    # Adapt agent for ServiceNow
    adapted_agent = adapter.adapt_agent_for_servicenow(example_agent)
    
    print("Original Agent:", example_agent['name'])
    print("\nServiceNow Adaptation:")
    print(f"Tool Packages: {adapted_agent['servicenow_metadata']['tool_packages']}")
    print(f"ServiceNow Roles: {adapted_agent['servicenow_metadata']['servicenow_roles']}")
    print(f"Integration Capabilities: {json.dumps(adapted_agent['servicenow_metadata']['integration_capabilities'], indent=2)}")
    print(f"\nServiceNow Tools: {len(adapted_agent['servicenow_tools'])} tools available")
    
    # Example tool translation
    agent_request = {
        "tool": "alert_manager",
        "params": {
            "alert_title": "Database Connection Failed",
            "alert_description": "Unable to connect to production database",
            "severity": "high",
            "alert_source": "monitoring_system"
        }
    }
    
    servicenow_request = adapter.translate_agent_request_to_servicenow(
        agent_request["tool"],
        agent_request["params"]
    )
    
    print(f"\nTool Translation Example:")
    print(f"Agent Tool: {agent_request['tool']}")
    print(f"ServiceNow Tool: {servicenow_request['tool']}")
    print(f"Parameter Mapping: {json.dumps(servicenow_request['parameters'], indent=2)}")

if __name__ == "__main__":
    demonstrate_adapter()
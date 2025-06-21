#!/usr/bin/env python3
"""
MCP Agent Server Implementation
Uses FastMCP to expose agent capabilities as per MCP SDK documentation
"""

from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# MCP SDK imports as per documentation
from mcp.server.fastmcp import FastMCP
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Import our agent framework
from enhance_agent_capabilities import AgentCapabilityEnhancer, ToolCategory
from agent_behavior_system import AgentBehaviorSystem, InteractionContext

@dataclass
class AgentContext:
    """Context for agent MCP operations"""
    agent_id: str
    agent_name: str
    capabilities: Dict[str, Any]
    behavior_profile: Dict[str, Any]
    
class AgentMCPServer:
    """MCP Server for an individual agent using FastMCP"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.agent_config = agent_config
        self.agent_name = agent_config.get('name', 'Unknown')
        self.agent_id = agent_config.get('enhanced_metadata', {}).get('agent_uuid', 'unknown')
        
        # Initialize FastMCP server with agent name
        self.mcp = FastMCP(f"AgentVerse:{self.agent_name}")
        
        # Initialize behavior system
        self.behavior_system = AgentBehaviorSystem()
        
        # Setup MCP components
        self._setup_resources()
        self._setup_tools()
        self._setup_prompts()
    
    def _setup_resources(self):
        """Setup MCP resources for the agent"""
        
        # Agent profile resource
        @self.mcp.resource("agent://profile")
        async def get_agent_profile() -> str:
            """Get agent profile and capabilities"""
            profile = {
                "id": self.agent_id,
                "name": self.agent_name,
                "display_name": self.agent_config.get('display_name', self.agent_name),
                "category": self.agent_config.get('category', 'General'),
                "subcategory": self.agent_config.get('subcategory', ''),
                "skills": self.agent_config.get('skills', []),
                "tools": self.agent_config.get('tools', []),
                "version": self.agent_config.get('enhanced_metadata', {}).get('version', '1.0.0'),
                "capabilities": self._get_capability_summary()
            }
            return json.dumps(profile, indent=2)
        
        # Capabilities resource
        @self.mcp.resource("agent://capabilities")
        async def get_capabilities() -> str:
            """Get detailed agent capabilities"""
            capabilities = self.agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {})
            return json.dumps(capabilities, indent=2)
        
        # Tools catalog resource
        @self.mcp.resource("agent://tools")
        async def get_tools_catalog() -> str:
            """Get available tools for this agent"""
            tools = self.agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {}).get('tools', {})
            catalog = {
                "total": len(tools),
                "categories": self._categorize_tools(tools),
                "tools": list(tools.keys())
            }
            return json.dumps(catalog, indent=2)
        
        # Workflows resource
        @self.mcp.resource("agent://workflows")
        async def get_workflows() -> str:
            """Get available workflows"""
            workflows = self.agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {}).get('workflows', {})
            return json.dumps(workflows, indent=2)
        
        # Metrics resource
        @self.mcp.resource("agent://metrics")
        async def get_metrics() -> str:
            """Get agent performance metrics"""
            metrics = self.agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {}).get('performance_metrics', {})
            metrics['last_updated'] = datetime.now().isoformat()
            return json.dumps(metrics, indent=2)
        
        # Behavior profile resource
        @self.mcp.resource("agent://behavior")
        async def get_behavior_profile() -> str:
            """Get agent behavior profile"""
            agent_type = self._determine_agent_type()
            context = InteractionContext()
            behavior_config = self.behavior_system.generate_behavior_config(agent_type, context)
            return json.dumps(behavior_config, indent=2)
    
    def _setup_tools(self):
        """Setup MCP tools based on agent capabilities"""
        
        # Get agent's tools from configuration
        agent_tools = self.agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {}).get('tools', {})
        
        # Code Analysis Tool
        if 'ast_analyzer' in agent_tools:
            @self.mcp.tool()
            async def analyze_code(
                code: str,
                language: str = "python",
                include_metrics: bool = True
            ) -> Dict[str, Any]:
                """Analyze code structure and quality
                
                Args:
                    code: Source code to analyze
                    language: Programming language
                    include_metrics: Include quality metrics
                    
                Returns:
                    Analysis results with structure, complexity, and suggestions
                """
                # Simulate code analysis
                analysis = {
                    "language": language,
                    "structure": {
                        "type": "module",
                        "functions": 2,
                        "classes": 1,
                        "imports": 5
                    },
                    "complexity": {
                        "cyclomatic": 5,
                        "cognitive": 3,
                        "halstead": {"difficulty": 8.5, "effort": 245}
                    },
                    "issues": [
                        {"line": 10, "type": "style", "message": "Line too long"},
                        {"line": 25, "type": "complexity", "message": "Function too complex"}
                    ],
                    "suggestions": [
                        "Consider breaking down complex functions",
                        "Add type hints for better clarity"
                    ]
                }
                
                if not include_metrics:
                    analysis.pop('complexity', None)
                
                return analysis
        
        # API Integration Tool
        if 'rest_client' in agent_tools or 'graphql_client' in agent_tools:
            @self.mcp.tool()
            async def make_api_request(
                endpoint: str,
                method: str = "GET",
                headers: Optional[Dict[str, str]] = None,
                body: Optional[Dict[str, Any]] = None,
                query_params: Optional[Dict[str, str]] = None
            ) -> Dict[str, Any]:
                """Make API request with authentication support
                
                Args:
                    endpoint: API endpoint URL
                    method: HTTP method
                    headers: Request headers
                    body: Request body for POST/PUT
                    query_params: Query parameters
                    
                Returns:
                    API response with status and data
                """
                # Simulate API request
                return {
                    "status": 200,
                    "headers": {"content-type": "application/json"},
                    "data": {"message": "Simulated response", "endpoint": endpoint},
                    "timing": {"total": 150, "dns": 20, "connect": 30, "request": 100}
                }
        
        # Data Processing Tool
        if 'data_transformer' in agent_tools:
            @self.mcp.tool()
            async def transform_data(
                data: Any,
                input_format: str,
                output_format: str,
                schema: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """Transform data between formats
                
                Args:
                    data: Input data
                    input_format: Source format (json, xml, csv, yaml)
                    output_format: Target format
                    schema: Optional schema for validation
                    
                Returns:
                    Transformed data and validation results
                """
                # Simulate data transformation
                return {
                    "success": True,
                    "output_format": output_format,
                    "data": data,  # In real implementation, would transform
                    "validation": {"valid": True, "errors": []},
                    "metadata": {"records": 1, "size_bytes": 256}
                }
        
        # Test Generation Tool
        if 'test_generator' in agent_tools:
            @self.mcp.tool()
            async def generate_tests(
                code: str,
                test_framework: str = "pytest",
                coverage_target: float = 0.8
            ) -> Dict[str, Any]:
                """Generate test cases for code
                
                Args:
                    code: Source code to test
                    test_framework: Testing framework to use
                    coverage_target: Target coverage percentage
                    
                Returns:
                    Generated test cases and coverage estimate
                """
                # Simulate test generation
                return {
                    "framework": test_framework,
                    "tests": [
                        {
                            "name": "test_function_happy_path",
                            "type": "unit",
                            "code": "def test_function_happy_path():\n    assert function(1) == 2"
                        },
                        {
                            "name": "test_function_edge_case",
                            "type": "unit", 
                            "code": "def test_function_edge_case():\n    assert function(0) == 0"
                        }
                    ],
                    "coverage_estimate": 0.75,
                    "missing_coverage": ["error handling", "edge cases"]
                }
        
        # Deployment Tool
        if 'container_builder' in agent_tools or 'k8s_deployer' in agent_tools:
            @self.mcp.tool()
            async def deploy_application(
                app_name: str,
                environment: str = "staging",
                config: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """Deploy application to target environment
                
                Args:
                    app_name: Application name
                    environment: Target environment
                    config: Deployment configuration
                    
                Returns:
                    Deployment status and details
                """
                # Simulate deployment
                return {
                    "status": "success",
                    "deployment_id": f"deploy-{app_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    "environment": environment,
                    "endpoints": [f"https://{app_name}.{environment}.example.com"],
                    "replicas": config.get('replicas', 3) if config else 3,
                    "health_check": "passing"
                }
        
        # Monitoring Tool
        if 'metrics_collector' in agent_tools or 'log_analyzer' in agent_tools:
            @self.mcp.tool()
            async def analyze_logs(
                log_source: str,
                time_range: str = "1h",
                pattern: Optional[str] = None
            ) -> Dict[str, Any]:
                """Analyze logs for patterns and anomalies
                
                Args:
                    log_source: Log source identifier
                    time_range: Time range to analyze
                    pattern: Optional pattern to search
                    
                Returns:
                    Log analysis results
                """
                # Simulate log analysis
                return {
                    "source": log_source,
                    "time_range": time_range,
                    "total_logs": 15420,
                    "errors": 23,
                    "warnings": 156,
                    "patterns_found": [
                        {"pattern": "connection timeout", "count": 12},
                        {"pattern": "authentication failed", "count": 5}
                    ],
                    "anomalies": [
                        {"time": "2024-01-01T10:15:00", "type": "spike", "description": "Error rate spike"}
                    ]
                }
        
        # Collaboration Tool
        @self.mcp.tool()
        async def collaborate_with_agent(
            target_agent: str,
            task: str,
            context: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Collaborate with another agent
            
            Args:
                target_agent: Name of agent to collaborate with
                task: Task description
                context: Additional context
                
            Returns:
                Collaboration result
            """
            return {
                "status": "initiated",
                "collaboration_id": f"collab-{self.agent_id[:8]}-{datetime.now().strftime('%H%M%S')}",
                "target_agent": target_agent,
                "task": task,
                "estimated_completion": "5 minutes"
            }
    
    def _setup_prompts(self):
        """Setup MCP prompts for common interactions"""
        
        @self.mcp.prompt()
        async def code_review_prompt(
            code: str,
            language: str = "python",
            focus_areas: Optional[List[str]] = None
        ) -> List[Dict[str, Any]]:
            """Generate code review prompt
            
            Args:
                code: Code to review
                language: Programming language
                focus_areas: Specific areas to focus on
                
            Returns:
                Prompt messages for code review
            """
            focus = ", ".join(focus_areas) if focus_areas else "general quality, best practices, and potential issues"
            
            return [
                {
                    "role": "system",
                    "content": f"You are {self.agent_name}, an expert in {language} development. Conduct a thorough code review focusing on {focus}."
                },
                {
                    "role": "user", 
                    "content": f"Please review this {language} code:\n\n```{language}\n{code}\n```"
                }
            ]
        
        @self.mcp.prompt()
        async def problem_solving_prompt(
            problem: str,
            constraints: Optional[List[str]] = None,
            preferred_approach: Optional[str] = None
        ) -> List[Dict[str, Any]]:
            """Generate problem-solving prompt
            
            Args:
                problem: Problem description
                constraints: Any constraints
                preferred_approach: Preferred solving approach
                
            Returns:
                Prompt messages for problem solving
            """
            agent_type = self._determine_agent_type()
            behavior_config = self.behavior_system.generate_behavior_config(
                agent_type, 
                InteractionContext()
            )
            
            approach = preferred_approach or behavior_config['behavior_profile']['problem_solving_approach']
            
            messages = [
                {
                    "role": "system",
                    "content": f"You are {self.agent_name}. Use a {approach} approach to solve problems. Your expertise: {', '.join(self.agent_config.get('skills', []))}"
                },
                {
                    "role": "user",
                    "content": f"Problem: {problem}"
                }
            ]
            
            if constraints:
                messages.append({
                    "role": "user",
                    "content": f"Constraints: {', '.join(constraints)}"
                })
            
            return messages
        
        @self.mcp.prompt()
        async def collaboration_prompt(
            task: str,
            collaborators: List[str],
            role: str = "coordinator"
        ) -> List[Dict[str, Any]]:
            """Generate collaboration prompt
            
            Args:
                task: Collaboration task
                collaborators: Other agents involved
                role: This agent's role
                
            Returns:
                Prompt messages for collaboration
            """
            return [
                {
                    "role": "system",
                    "content": f"You are {self.agent_name}, acting as {role} in a collaborative task with {', '.join(collaborators)}."
                },
                {
                    "role": "user",
                    "content": f"Task: {task}\n\nCoordinate effectively and leverage each agent's strengths."
                }
            ]
    
    def _get_capability_summary(self) -> Dict[str, Any]:
        """Get summary of agent capabilities"""
        capabilities = self.agent_config.get('enhanced_metadata', {}).get('functional_capabilities', {})
        
        return {
            "tools_count": len(capabilities.get('tools', {})),
            "workflows_count": len(capabilities.get('workflows', {})),
            "integration_points": len(capabilities.get('integration_points', [])),
            "behavioral_adaptability": bool(capabilities.get('behavioral_patterns', {}))
        }
    
    def _categorize_tools(self, tools: Dict[str, Any]) -> Dict[str, int]:
        """Categorize tools by type"""
        categories = {}
        for tool_info in tools.values():
            category = tool_info.get('category', 'unknown')
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _determine_agent_type(self) -> str:
        """Determine agent type for behavior system"""
        category = self.agent_config.get('category', '').lower()
        
        type_mapping = {
            'engineering': 'engineering_expert',
            'business': 'business_analyst',
            'data analytics': 'data_scientist',
            'security': 'security_specialist',
            'support': 'support_specialist',
            'devops': 'devops_engineer'
        }
        
        return type_mapping.get(category, 'engineering_expert')
    
    async def run(self):
        """Run the MCP server"""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.mcp.run(
                read_stream,
                write_stream,
                self.mcp.create_initialization_options()
            )

async def create_agent_mcp_server(agent_config: Dict[str, Any]) -> AgentMCPServer:
    """Factory function to create an agent MCP server"""
    return AgentMCPServer(agent_config)

async def main():
    """Test the MCP server with a sample agent"""
    # Load a sample agent for testing
    with open('src/config/agentverse_agents_1000.json', 'r') as f:
        agents = json.load(f)
    
    # Use the first agent as an example
    if agents:
        agent_config = agents[0]
        server = AgentMCPServer(agent_config)
        
        print(f"Starting MCP server for agent: {server.agent_name}")
        print(f"Agent ID: {server.agent_id}")
        print("\nAvailable resources:")
        print("  - agent://profile")
        print("  - agent://capabilities") 
        print("  - agent://tools")
        print("  - agent://workflows")
        print("  - agent://metrics")
        print("  - agent://behavior")
        
        # In production, this would run the server
        # await server.run()
        
        print("\nMCP server configured successfully!")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
AgentVerse MCP Server
A comprehensive MCP server for the AgentVerse platform following best practices
"""

import os
import json
import asyncio
import argparse
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server
from mcp.server.sse import sse_server
from mcp.types import TextContent, ImageContent, EmbeddedResource

# Import our modules
from enhance_agent_capabilities import AgentCapabilityEnhancer
from agent_behavior_system import AgentBehaviorSystem, InteractionContext
from test_agent_capabilities import AgentCapabilityTester

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
@dataclass
class ServerConfig:
    """Server configuration"""
    name: str = "AgentVerse MCP Server"
    version: str = "1.0.0"
    host: str = "localhost"
    port: int = 8080
    mode: str = "stdio"  # stdio or sse
    debug: bool = False
    agents_config_path: str = "src/config/agentverse_agents_1000.json"
    max_agents_loaded: int = 100  # Limit for performance

class ToolPackage(Enum):
    """Available tool packages"""
    AGENT_DISCOVERY = "agent_discovery"
    AGENT_INTERACTION = "agent_interaction"
    CAPABILITY_MANAGEMENT = "capability_management"
    WORKFLOW_EXECUTION = "workflow_execution"
    COLLABORATION = "collaboration"
    TESTING = "testing"
    MONITORING = "monitoring"
    ALL = "all"

@dataclass
class AgentInfo:
    """Agent information structure"""
    id: str
    name: str
    display_name: str
    category: str
    skills: List[str]
    tools: List[str]
    capabilities: Dict[str, Any] = field(default_factory=dict)

class AgentVerseMCPServer:
    """Main MCP Server for AgentVerse platform"""
    
    def __init__(self, config: ServerConfig):
        self.config = config
        self.mcp = FastMCP(self.config.name)
        
        # Initialize components
        self.agents: Dict[str, AgentInfo] = {}
        self.behavior_system = AgentBehaviorSystem()
        self.capability_tester = AgentCapabilityTester(config.agents_config_path)
        
        # Load agents
        self._load_agents()
        
        # Setup MCP components based on tool packages
        self.tool_packages = self._get_enabled_packages()
        self._setup_introspection()
        self._setup_resources()
        self._setup_tools()
        self._setup_prompts()
        
        logger.info(f"Initialized {config.name} v{config.version}")
        logger.info(f"Loaded {len(self.agents)} agents")
        logger.info(f"Enabled tool packages: {[p.value for p in self.tool_packages]}")
    
    def _load_agents(self):
        """Load agent configurations"""
        try:
            with open(self.config.agents_config_path, 'r') as f:
                agents_data = json.load(f)
            
            # Load limited number of agents for performance
            for agent_data in agents_data[:self.config.max_agents_loaded]:
                agent_id = agent_data.get('enhanced_metadata', {}).get('agent_uuid', 'unknown')
                agent_info = AgentInfo(
                    id=agent_id,
                    name=agent_data.get('name', 'Unknown'),
                    display_name=agent_data.get('display_name', 'Unknown'),
                    category=agent_data.get('category', 'General'),
                    skills=agent_data.get('skills', []),
                    tools=agent_data.get('tools', []),
                    capabilities=agent_data.get('enhanced_metadata', {}).get('functional_capabilities', {})
                )
                self.agents[agent_id] = agent_info
                
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")
            self.agents = {}
    
    def _get_enabled_packages(self) -> List[ToolPackage]:
        """Get enabled tool packages from environment or default to all"""
        enabled = os.getenv('AGENTVERSE_TOOL_PACKAGES', 'all').split(',')
        
        if 'all' in enabled:
            return list(ToolPackage)
        
        packages = []
        for package_name in enabled:
            try:
                packages.append(ToolPackage(package_name.strip()))
            except ValueError:
                logger.warning(f"Unknown tool package: {package_name}")
        
        return packages or [ToolPackage.ALL]
    
    def _setup_introspection(self):
        """Setup introspection tool"""
        @self.mcp.tool()
        async def list_tool_packages() -> Dict[str, Any]:
            """List available tool packages and their descriptions
            
            Returns:
                Available tool packages with descriptions
            """
            packages = {
                "agent_discovery": {
                    "description": "Tools for discovering and querying agents",
                    "tools": ["search_agents", "get_agent_details", "list_agent_capabilities"]
                },
                "agent_interaction": {
                    "description": "Tools for interacting with agents",
                    "tools": ["send_task_to_agent", "get_agent_response", "evaluate_agent_performance"]
                },
                "capability_management": {
                    "description": "Tools for managing agent capabilities",
                    "tools": ["add_capability", "remove_capability", "update_agent_skills"]
                },
                "workflow_execution": {
                    "description": "Tools for executing workflows",
                    "tools": ["execute_workflow", "monitor_workflow", "get_workflow_status"]
                },
                "collaboration": {
                    "description": "Tools for multi-agent collaboration",
                    "tools": ["create_agent_team", "assign_collaborative_task", "coordinate_agents"]
                },
                "testing": {
                    "description": "Tools for testing agent capabilities",
                    "tools": ["run_capability_test", "benchmark_agent", "validate_agent_output"]
                },
                "monitoring": {
                    "description": "Tools for monitoring agent performance",
                    "tools": ["get_agent_metrics", "analyze_agent_logs", "generate_performance_report"]
                }
            }
            
            enabled = [p.value for p in self.tool_packages]
            return {
                "enabled_packages": enabled,
                "available_packages": packages,
                "total_tools": sum(len(p["tools"]) for p in packages.values())
            }
    
    def _setup_resources(self):
        """Setup MCP resources"""
        
        # Platform overview resource
        @self.mcp.resource("agentverse://platform/overview")
        async def get_platform_overview() -> str:
            """Get AgentVerse platform overview"""
            overview = {
                "name": "AgentVerse Platform",
                "version": self.config.version,
                "total_agents": len(self.agents),
                "categories": list(set(agent.category for agent in self.agents.values())),
                "capabilities": {
                    "mcp_enabled": True,
                    "multi_agent_collaboration": True,
                    "workflow_automation": True,
                    "behavior_adaptation": True
                }
            }
            return json.dumps(overview, indent=2)
        
        # Agents catalog resource
        @self.mcp.resource("agentverse://agents/catalog")
        async def get_agents_catalog() -> str:
            """Get catalog of all available agents"""
            catalog = {
                "total": len(self.agents),
                "agents": [
                    {
                        "id": agent.id,
                        "name": agent.name,
                        "display_name": agent.display_name,
                        "category": agent.category,
                        "skills_count": len(agent.skills),
                        "tools_count": len(agent.tools)
                    }
                    for agent in list(self.agents.values())[:50]  # Limit to 50 for response size
                ]
            }
            return json.dumps(catalog, indent=2)
        
        # Agent details resource (dynamic)
        @self.mcp.resource("agentverse://agents/{agent_id}")
        async def get_agent_details(agent_id: str) -> str:
            """Get detailed information about a specific agent"""
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                details = {
                    "id": agent.id,
                    "name": agent.name,
                    "display_name": agent.display_name,
                    "category": agent.category,
                    "skills": agent.skills,
                    "tools": agent.tools,
                    "capabilities_summary": {
                        "tools_count": len(agent.capabilities.get('tools', {})),
                        "workflows_count": len(agent.capabilities.get('workflows', {}))
                    }
                }
                return json.dumps(details, indent=2)
            else:
                return json.dumps({"error": f"Agent {agent_id} not found"})
        
        # Workflows catalog resource
        @self.mcp.resource("agentverse://workflows/catalog")
        async def get_workflows_catalog() -> str:
            """Get catalog of available workflows"""
            workflows = {
                "code_review": {
                    "description": "Automated code review workflow",
                    "steps": ["analyze", "security_check", "test_generation", "documentation"],
                    "supported_agents": ["Engineering"]
                },
                "api_deployment": {
                    "description": "API deployment pipeline",
                    "steps": ["build", "test", "deploy", "monitor"],
                    "supported_agents": ["Engineering", "DevOps"]
                },
                "data_processing": {
                    "description": "Data processing pipeline",
                    "steps": ["ingest", "transform", "analyze", "alert"],
                    "supported_agents": ["Data Analytics"]
                },
                "incident_response": {
                    "description": "Incident response workflow",
                    "steps": ["detect", "triage", "respond", "notify", "document"],
                    "supported_agents": ["Security", "DevOps", "Support"]
                }
            }
            return json.dumps(workflows, indent=2)
    
    def _setup_tools(self):
        """Setup MCP tools based on enabled packages"""
        
        # Agent Discovery Tools
        if ToolPackage.AGENT_DISCOVERY in self.tool_packages or ToolPackage.ALL in self.tool_packages:
            
            @self.mcp.tool()
            async def search_agents(
                query: str,
                category: Optional[str] = None,
                skills: Optional[List[str]] = None,
                limit: int = 10
            ) -> Dict[str, Any]:
                """Search for agents based on criteria
                
                Args:
                    query: Search query for agent names or descriptions
                    category: Filter by category
                    skills: Filter by required skills
                    limit: Maximum number of results
                    
                Returns:
                    Matching agents
                """
                results = []
                
                for agent in self.agents.values():
                    # Check if agent matches criteria
                    if query.lower() in agent.name.lower() or query.lower() in agent.display_name.lower():
                        if category and agent.category != category:
                            continue
                        if skills and not all(skill in agent.skills for skill in skills):
                            continue
                        
                        results.append({
                            "id": agent.id,
                            "name": agent.name,
                            "display_name": agent.display_name,
                            "category": agent.category,
                            "skills": agent.skills[:5],  # First 5 skills
                            "match_score": 1.0  # Simple scoring for now
                        })
                
                # Sort by match score and limit
                results.sort(key=lambda x: x['match_score'], reverse=True)
                
                return {
                    "query": query,
                    "total_matches": len(results),
                    "results": results[:limit]
                }
            
            @self.mcp.tool()
            async def get_agent_capabilities(agent_id: str) -> Dict[str, Any]:
                """Get detailed capabilities of an agent
                
                Args:
                    agent_id: Agent identifier
                    
                Returns:
                    Agent capabilities
                """
                if agent_id not in self.agents:
                    return {"error": f"Agent {agent_id} not found"}
                
                agent = self.agents[agent_id]
                return {
                    "agent_id": agent_id,
                    "name": agent.name,
                    "capabilities": {
                        "skills": agent.skills,
                        "tools": agent.tools,
                        "tool_categories": list(set(
                            tool_info.get('category', 'unknown')
                            for tool_info in agent.capabilities.get('tools', {}).values()
                        )),
                        "workflows": list(agent.capabilities.get('workflows', {}).keys()),
                        "behavior_adaptable": True,
                        "mcp_enabled": True
                    }
                }
        
        # Agent Interaction Tools
        if ToolPackage.AGENT_INTERACTION in self.tool_packages or ToolPackage.ALL in self.tool_packages:
            
            @self.mcp.tool()
            async def send_task_to_agent(
                agent_id: str,
                task: str,
                context: Optional[Dict[str, Any]] = None,
                priority: str = "normal"
            ) -> Dict[str, Any]:
                """Send a task to an agent for execution
                
                Args:
                    agent_id: Target agent ID
                    task: Task description
                    context: Additional context
                    priority: Task priority (low, normal, high, urgent)
                    
                Returns:
                    Task assignment result
                """
                if agent_id not in self.agents:
                    return {"error": f"Agent {agent_id} not found"}
                
                agent = self.agents[agent_id]
                
                # Generate behavior profile for the agent
                agent_type = agent.category.lower().replace(' ', '_') + '_expert'
                interaction_context = InteractionContext(
                    task_complexity="medium" if priority in ["normal", "low"] else "high",
                    time_constraints=30 if priority == "urgent" else None
                )
                
                behavior_config = self.behavior_system.generate_behavior_config(
                    agent_type, 
                    interaction_context
                )
                
                # Simulate task assignment
                task_id = f"task_{agent_id[:8]}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                return {
                    "task_id": task_id,
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "task": task,
                    "priority": priority,
                    "status": "assigned",
                    "estimated_completion": "5-10 minutes",
                    "behavior_profile": behavior_config['behavior_profile'],
                    "assigned_at": datetime.now().isoformat()
                }
            
            @self.mcp.tool()
            async def evaluate_agent_performance(
                agent_id: str,
                task_id: str,
                metrics: Optional[List[str]] = None
            ) -> Dict[str, Any]:
                """Evaluate agent performance on a task
                
                Args:
                    agent_id: Agent identifier
                    task_id: Task identifier
                    metrics: Specific metrics to evaluate
                    
                Returns:
                    Performance evaluation
                """
                if agent_id not in self.agents:
                    return {"error": f"Agent {agent_id} not found"}
                
                # Default metrics if none specified
                if not metrics:
                    metrics = ["accuracy", "speed", "resource_usage", "quality"]
                
                # Simulate performance evaluation
                evaluation = {
                    "agent_id": agent_id,
                    "task_id": task_id,
                    "metrics": {},
                    "overall_score": 0.85,
                    "recommendations": []
                }
                
                # Generate metric values
                import random
                for metric in metrics:
                    if metric == "accuracy":
                        evaluation["metrics"][metric] = random.uniform(0.85, 0.95)
                    elif metric == "speed":
                        evaluation["metrics"][metric] = random.uniform(0.7, 0.9)
                    elif metric == "resource_usage":
                        evaluation["metrics"][metric] = random.uniform(0.6, 0.8)
                    elif metric == "quality":
                        evaluation["metrics"][metric] = random.uniform(0.8, 0.95)
                
                # Generate recommendations
                if evaluation["metrics"].get("speed", 1.0) < 0.75:
                    evaluation["recommendations"].append("Consider optimizing for speed")
                if evaluation["metrics"].get("resource_usage", 0) > 0.8:
                    evaluation["recommendations"].append("High resource usage detected")
                
                return evaluation
        
        # Workflow Execution Tools
        if ToolPackage.WORKFLOW_EXECUTION in self.tool_packages or ToolPackage.ALL in self.tool_packages:
            
            @self.mcp.tool()
            async def execute_workflow(
                workflow_name: str,
                agent_ids: List[str],
                parameters: Optional[Dict[str, Any]] = None
            ) -> Dict[str, Any]:
                """Execute a workflow with specified agents
                
                Args:
                    workflow_name: Name of the workflow
                    agent_ids: List of agent IDs to involve
                    parameters: Workflow parameters
                    
                Returns:
                    Workflow execution result
                """
                # Validate agents
                invalid_agents = [aid for aid in agent_ids if aid not in self.agents]
                if invalid_agents:
                    return {"error": f"Invalid agent IDs: {invalid_agents}"}
                
                # Check if workflow is supported
                supported_workflows = ["code_review", "api_deployment", "data_processing", "incident_response"]
                if workflow_name not in supported_workflows:
                    return {"error": f"Unsupported workflow: {workflow_name}"}
                
                # Create execution ID
                execution_id = f"wf_{workflow_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Determine workflow steps based on type
                workflow_steps = {
                    "code_review": ["analyze", "security_check", "test_generation", "documentation"],
                    "api_deployment": ["build", "test", "deploy", "monitor"],
                    "data_processing": ["ingest", "transform", "analyze", "alert"],
                    "incident_response": ["detect", "triage", "respond", "notify", "document"]
                }
                
                return {
                    "execution_id": execution_id,
                    "workflow": workflow_name,
                    "status": "started",
                    "agents": [
                        {"id": aid, "name": self.agents[aid].name}
                        for aid in agent_ids
                    ],
                    "steps": workflow_steps.get(workflow_name, []),
                    "current_step": workflow_steps.get(workflow_name, [])[0],
                    "progress": 0,
                    "started_at": datetime.now().isoformat(),
                    "estimated_duration": "10-15 minutes"
                }
            
            @self.mcp.tool()
            async def get_workflow_status(execution_id: str) -> Dict[str, Any]:
                """Get status of a workflow execution
                
                Args:
                    execution_id: Workflow execution ID
                    
                Returns:
                    Workflow status
                """
                # Simulate workflow progress
                import random
                progress = random.randint(20, 80)
                
                return {
                    "execution_id": execution_id,
                    "status": "in_progress" if progress < 100 else "completed",
                    "progress": progress,
                    "current_step": "test" if progress < 50 else "deploy",
                    "completed_steps": ["analyze", "security_check"] if progress > 30 else ["analyze"],
                    "logs": [
                        {"timestamp": datetime.now().isoformat(), "message": "Workflow started"},
                        {"timestamp": datetime.now().isoformat(), "message": f"Progress: {progress}%"}
                    ]
                }
        
        # Collaboration Tools
        if ToolPackage.COLLABORATION in self.tool_packages or ToolPackage.ALL in self.tool_packages:
            
            @self.mcp.tool()
            async def create_agent_team(
                team_name: str,
                agent_ids: List[str],
                team_role: str = "general"
            ) -> Dict[str, Any]:
                """Create a team of agents for collaboration
                
                Args:
                    team_name: Name for the team
                    agent_ids: List of agent IDs
                    team_role: Team's primary role
                    
                Returns:
                    Team creation result
                """
                # Validate agents
                valid_agents = [aid for aid in agent_ids if aid in self.agents]
                
                if not valid_agents:
                    return {"error": "No valid agents provided"}
                
                # Create team
                team_id = f"team_{team_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                team_members = []
                for aid in valid_agents:
                    agent = self.agents[aid]
                    team_members.append({
                        "id": aid,
                        "name": agent.name,
                        "role": agent.category,
                        "skills": agent.skills[:3]
                    })
                
                return {
                    "team_id": team_id,
                    "team_name": team_name,
                    "team_role": team_role,
                    "members": team_members,
                    "capabilities": {
                        "combined_skills": list(set(
                            skill
                            for aid in valid_agents
                            for skill in self.agents[aid].skills
                        ))[:10],
                        "coordination_protocol": "async",
                        "communication_channel": f"team_{team_id}"
                    },
                    "created_at": datetime.now().isoformat()
                }
            
            @self.mcp.tool()
            async def coordinate_agents(
                team_id: str,
                coordination_type: str = "sequential",
                task_distribution: Optional[Dict[str, str]] = None
            ) -> Dict[str, Any]:
                """Coordinate agents in a team
                
                Args:
                    team_id: Team identifier
                    coordination_type: How to coordinate (sequential, parallel, hierarchical)
                    task_distribution: Mapping of agent IDs to tasks
                    
                Returns:
                    Coordination result
                """
                coordination_id = f"coord_{team_id}_{datetime.now().strftime('%H%M%S')}"
                
                return {
                    "coordination_id": coordination_id,
                    "team_id": team_id,
                    "type": coordination_type,
                    "status": "active",
                    "task_distribution": task_distribution or {},
                    "coordination_metrics": {
                        "efficiency": 0.85,
                        "communication_overhead": 0.15,
                        "sync_points": 3 if coordination_type == "sequential" else 1
                    },
                    "started_at": datetime.now().isoformat()
                }
        
        # Testing Tools
        if ToolPackage.TESTING in self.tool_packages or ToolPackage.ALL in self.tool_packages:
            
            @self.mcp.tool()
            async def run_capability_test(
                agent_id: str,
                test_suite: str = "basic",
                test_cases: Optional[List[str]] = None
            ) -> Dict[str, Any]:
                """Run capability tests on an agent
                
                Args:
                    agent_id: Agent to test
                    test_suite: Test suite to run
                    test_cases: Specific test cases
                    
                Returns:
                    Test results
                """
                if agent_id not in self.agents:
                    return {"error": f"Agent {agent_id} not found"}
                
                agent = self.agents[agent_id]
                
                # Simulate test execution
                test_results = {
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "test_suite": test_suite,
                    "total_tests": len(test_cases) if test_cases else 10,
                    "passed": 8,
                    "failed": 2,
                    "skipped": 0,
                    "duration": "2.5 seconds",
                    "results": []
                }
                
                # Generate sample test results
                if not test_cases:
                    test_cases = ["code_analysis", "api_integration", "error_handling", "performance"]
                
                import random
                for test_case in test_cases[:5]:
                    test_results["results"].append({
                        "test": test_case,
                        "status": "passed" if random.random() > 0.2 else "failed",
                        "duration": f"{random.uniform(0.1, 0.5):.2f}s",
                        "message": "Test completed successfully" if random.random() > 0.2 else "Assertion failed"
                    })
                
                return test_results
        
        # Monitoring Tools
        if ToolPackage.MONITORING in self.tool_packages or ToolPackage.ALL in self.tool_packages:
            
            @self.mcp.tool()
            async def get_agent_metrics(
                agent_id: str,
                metric_types: Optional[List[str]] = None,
                time_range: str = "1h"
            ) -> Dict[str, Any]:
                """Get performance metrics for an agent
                
                Args:
                    agent_id: Agent identifier
                    metric_types: Types of metrics to retrieve
                    time_range: Time range for metrics
                    
                Returns:
                    Agent metrics
                """
                if agent_id not in self.agents:
                    return {"error": f"Agent {agent_id} not found"}
                
                # Default metrics
                if not metric_types:
                    metric_types = ["response_time", "throughput", "error_rate", "resource_usage"]
                
                # Simulate metrics
                import random
                metrics = {
                    "agent_id": agent_id,
                    "time_range": time_range,
                    "metrics": {}
                }
                
                for metric in metric_types:
                    if metric == "response_time":
                        metrics["metrics"][metric] = {
                            "avg": random.uniform(100, 300),
                            "p95": random.uniform(400, 600),
                            "p99": random.uniform(700, 1000),
                            "unit": "ms"
                        }
                    elif metric == "throughput":
                        metrics["metrics"][metric] = {
                            "value": random.uniform(50, 200),
                            "unit": "requests/second"
                        }
                    elif metric == "error_rate":
                        metrics["metrics"][metric] = {
                            "value": random.uniform(0.001, 0.01),
                            "unit": "percentage"
                        }
                    elif metric == "resource_usage":
                        metrics["metrics"][metric] = {
                            "cpu": random.uniform(10, 50),
                            "memory": random.uniform(100, 500),
                            "unit": "percentage/MB"
                        }
                
                return metrics
    
    def _setup_prompts(self):
        """Setup MCP prompts"""
        
        @self.mcp.prompt()
        async def agent_selection_prompt(
            task: str,
            requirements: Optional[List[str]] = None
        ) -> List[Dict[str, Any]]:
            """Generate prompt for agent selection
            
            Args:
                task: Task description
                requirements: Specific requirements
                
            Returns:
                Prompt messages
            """
            return [
                {
                    "role": "system",
                    "content": "You are an expert at selecting the right agents for tasks. Consider skills, capabilities, and availability."
                },
                {
                    "role": "user",
                    "content": f"Task: {task}\nRequirements: {', '.join(requirements or ['None specified'])}\n\nRecommend the best agents for this task."
                }
            ]
        
        @self.mcp.prompt()
        async def workflow_design_prompt(
            objective: str,
            constraints: Optional[List[str]] = None,
            available_agents: Optional[List[str]] = None
        ) -> List[Dict[str, Any]]:
            """Generate prompt for workflow design
            
            Args:
                objective: Workflow objective
                constraints: Any constraints
                available_agents: Available agent IDs
                
            Returns:
                Prompt messages
            """
            agents_info = ""
            if available_agents:
                agents_info = "\n".join([
                    f"- {self.agents[aid].name}: {', '.join(self.agents[aid].skills[:3])}"
                    for aid in available_agents[:5]
                    if aid in self.agents
                ])
            
            return [
                {
                    "role": "system",
                    "content": "You are a workflow architect. Design efficient workflows that leverage agent capabilities optimally."
                },
                {
                    "role": "user",
                    "content": f"Objective: {objective}\nConstraints: {', '.join(constraints or ['None'])}\n\nAvailable Agents:\n{agents_info}\n\nDesign an optimal workflow."
                }
            ]
        
        @self.mcp.prompt()
        async def performance_analysis_prompt(
            metrics: Dict[str, Any],
            agent_name: str,
            time_period: str = "last 24 hours"
        ) -> List[Dict[str, Any]]:
            """Generate prompt for performance analysis
            
            Args:
                metrics: Performance metrics
                agent_name: Agent name
                time_period: Analysis period
                
            Returns:
                Prompt messages
            """
            metrics_summary = json.dumps(metrics, indent=2)
            
            return [
                {
                    "role": "system",
                    "content": "You are a performance analyst. Analyze agent metrics and provide actionable insights."
                },
                {
                    "role": "user",
                    "content": f"Analyze performance for {agent_name} over {time_period}:\n\n{metrics_summary}\n\nProvide insights and recommendations."
                }
            ]
    
    async def run(self):
        """Run the MCP server"""
        if self.config.mode == "stdio":
            logger.info("Starting AgentVerse MCP server in stdio mode...")
            async with stdio_server() as (read_stream, write_stream):
                await self.mcp.run(
                    read_stream,
                    write_stream,
                    self.mcp.create_initialization_options()
                )
        elif self.config.mode == "sse":
            logger.info(f"Starting AgentVerse MCP server in SSE mode on {self.config.host}:{self.config.port}...")
            async with sse_server(self.config.host, self.config.port) as (read_stream, write_stream):
                await self.mcp.run(
                    read_stream,
                    write_stream,
                    self.mcp.create_initialization_options()
                )
        else:
            raise ValueError(f"Unknown server mode: {self.config.mode}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="AgentVerse MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in stdio mode (default)
  python agentverse_mcp_server.py
  
  # Run in SSE mode
  python agentverse_mcp_server.py --mode sse --port 8080
  
  # Enable specific tool packages
  export AGENTVERSE_TOOL_PACKAGES="agent_discovery,workflow_execution"
  python agentverse_mcp_server.py
  
  # Enable debug mode
  python agentverse_mcp_server.py --debug
        """
    )
    
    parser.add_argument('--mode', choices=['stdio', 'sse'], default='stdio',
                       help='Server mode (stdio or sse)')
    parser.add_argument('--host', default='localhost',
                       help='Host for SSE mode')
    parser.add_argument('--port', type=int, default=8080,
                       help='Port for SSE mode')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    parser.add_argument('--config', default='src/config/agentverse_agents_1000.json',
                       help='Path to agents configuration')
    parser.add_argument('--max-agents', type=int, default=100,
                       help='Maximum number of agents to load')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create server config
    config = ServerConfig(
        mode=args.mode,
        host=args.host,
        port=args.port,
        debug=args.debug,
        agents_config_path=args.config,
        max_agents_loaded=args.max_agents
    )
    
    # Create and run server
    server = AgentVerseMCPServer(config)
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        if args.debug:
            raise

if __name__ == "__main__":
    main()
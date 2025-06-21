#!/usr/bin/env python3
"""
MCP Agent Client Implementation
Enables agents to communicate with other agents via MCP
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from contextlib import asynccontextmanager

# MCP SDK imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool, Resource

@dataclass
class AgentConnection:
    """Represents a connection to another agent"""
    agent_id: str
    agent_name: str
    session: ClientSession
    connected_at: datetime
    capabilities: Optional[Dict[str, Any]] = None

class AgentMCPClient:
    """MCP Client for agent-to-agent communication"""
    
    def __init__(self, client_agent_name: str, client_agent_id: str):
        self.client_name = client_agent_name
        self.client_id = client_agent_id
        self.connections: Dict[str, AgentConnection] = {}
        self.discovered_agents: Dict[str, Dict[str, Any]] = {}
    
    @asynccontextmanager
    async def connect_to_agent(self, agent_command: str, agent_args: List[str] = None):
        """Connect to another agent's MCP server
        
        Args:
            agent_command: Command to start the agent server
            agent_args: Additional arguments for the agent
            
        Yields:
            AgentConnection instance
        """
        server_params = StdioServerParameters(
            command=agent_command,
            args=agent_args or [],
            env=None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                # Get agent info from profile resource
                agent_info = await self._get_agent_info(session)
                
                # Create connection record
                connection = AgentConnection(
                    agent_id=agent_info.get('id', 'unknown'),
                    agent_name=agent_info.get('name', 'Unknown Agent'),
                    session=session,
                    connected_at=datetime.now(),
                    capabilities=agent_info.get('capabilities', {})
                )
                
                self.connections[connection.agent_id] = connection
                
                yield connection
    
    async def _get_agent_info(self, session: ClientSession) -> Dict[str, Any]:
        """Get agent information from profile resource"""
        try:
            # List available resources
            resources = await session.list_resources()
            
            # Find profile resource
            profile_resource = None
            for resource in resources.resources:
                if resource.uri == "agent://profile":
                    profile_resource = resource
                    break
            
            if profile_resource:
                # Read the profile
                profile_data = await session.read_resource(profile_resource.uri)
                if profile_data.contents and len(profile_data.contents) > 0:
                    content = profile_data.contents[0]
                    if hasattr(content, 'text'):
                        return json.loads(content.text)
            
            return {"error": "Could not retrieve agent profile"}
            
        except Exception as e:
            return {"error": f"Failed to get agent info: {str(e)}"}
    
    async def discover_agent_capabilities(self, session: ClientSession) -> Dict[str, Any]:
        """Discover all capabilities of a connected agent"""
        capabilities = {
            "resources": [],
            "tools": [],
            "prompts": []
        }
        
        try:
            # List resources
            resources = await session.list_resources()
            for resource in resources.resources:
                capabilities["resources"].append({
                    "uri": resource.uri,
                    "name": resource.name,
                    "description": resource.description,
                    "mimeType": resource.mimeType
                })
            
            # List tools
            tools = await session.list_tools()
            for tool in tools.tools:
                capabilities["tools"].append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                })
            
            # List prompts
            prompts = await session.list_prompts()
            for prompt in prompts.prompts:
                capabilities["prompts"].append({
                    "name": prompt.name,
                    "description": prompt.description,
                    "arguments": prompt.arguments
                })
        
        except Exception as e:
            capabilities["error"] = str(e)
        
        return capabilities
    
    async def call_agent_tool(
        self, 
        agent_id: str, 
        tool_name: str, 
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Call a tool on a connected agent
        
        Args:
            agent_id: ID of the target agent
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if agent_id not in self.connections:
            return {"error": f"Not connected to agent {agent_id}"}
        
        connection = self.connections[agent_id]
        
        try:
            result = await connection.session.call_tool(tool_name, arguments)
            
            # Parse the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            return {"result": "Tool executed successfully", "raw_result": str(result)}
            
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    async def read_agent_resource(
        self, 
        agent_id: str, 
        resource_uri: str
    ) -> Dict[str, Any]:
        """Read a resource from a connected agent
        
        Args:
            agent_id: ID of the target agent
            resource_uri: URI of the resource
            
        Returns:
            Resource content
        """
        if agent_id not in self.connections:
            return {"error": f"Not connected to agent {agent_id}"}
        
        connection = self.connections[agent_id]
        
        try:
            result = await connection.session.read_resource(resource_uri)
            
            if result.contents and len(result.contents) > 0:
                content = result.contents[0]
                if hasattr(content, 'text'):
                    return json.loads(content.text)
            
            return {"error": "Empty resource response"}
            
        except Exception as e:
            return {"error": f"Resource read failed: {str(e)}"}
    
    async def get_agent_prompt(
        self,
        agent_id: str,
        prompt_name: str,
        arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get a prompt from a connected agent
        
        Args:
            agent_id: ID of the target agent
            prompt_name: Name of the prompt
            arguments: Prompt arguments
            
        Returns:
            Prompt messages
        """
        if agent_id not in self.connections:
            return [{"error": f"Not connected to agent {agent_id}"}]
        
        connection = self.connections[agent_id]
        
        try:
            result = await connection.session.get_prompt(prompt_name, arguments)
            
            messages = []
            if result.messages:
                for message in result.messages:
                    messages.append({
                        "role": message.role,
                        "content": message.content.text if hasattr(message.content, 'text') else str(message.content)
                    })
            
            return messages
            
        except Exception as e:
            return [{"error": f"Prompt retrieval failed: {str(e)}"}]
    
    async def collaborate_on_task(
        self,
        agent_id: str,
        task: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Initiate collaboration with another agent
        
        Args:
            agent_id: ID of the target agent
            task: Task description
            context: Additional context
            
        Returns:
            Collaboration result
        """
        # First, check if the agent has collaboration capability
        capabilities = await self.discover_agent_capabilities(
            self.connections[agent_id].session
        )
        
        # Look for collaboration tool
        collab_tool = None
        for tool in capabilities.get('tools', []):
            if 'collaborate' in tool['name'].lower():
                collab_tool = tool['name']
                break
        
        if not collab_tool:
            return {"error": "Target agent does not support collaboration"}
        
        # Call the collaboration tool
        result = await self.call_agent_tool(
            agent_id,
            collab_tool,
            {
                "target_agent": self.client_name,
                "task": task,
                "context": context or {}
            }
        )
        
        return result
    
    async def execute_workflow(
        self,
        agent_id: str,
        workflow_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow on another agent
        
        Args:
            agent_id: ID of the target agent
            workflow_name: Name of the workflow
            parameters: Workflow parameters
            
        Returns:
            Workflow execution result
        """
        # First, get available workflows
        workflows_data = await self.read_agent_resource(agent_id, "agent://workflows")
        
        if "error" in workflows_data:
            return workflows_data
        
        # Check if workflow exists
        if workflow_name not in workflows_data:
            return {"error": f"Workflow '{workflow_name}' not found"}
        
        # Execute workflow via tool (assuming workflow execution is exposed as a tool)
        result = await self.call_agent_tool(
            agent_id,
            "execute_workflow",
            {
                "workflow_id": workflow_name,
                "parameters": parameters
            }
        )
        
        return result
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all connections"""
        status = {
            "client": {
                "name": self.client_name,
                "id": self.client_id
            },
            "connections": []
        }
        
        for agent_id, connection in self.connections.items():
            status["connections"].append({
                "agent_id": agent_id,
                "agent_name": connection.agent_name,
                "connected_at": connection.connected_at.isoformat(),
                "capabilities_discovered": connection.capabilities is not None
            })
        
        return status

# Example usage functions
async def demonstrate_client():
    """Demonstrate MCP client capabilities"""
    # Create client for a Django expert agent
    client = AgentMCPClient(
        client_agent_name="OpenAISDK_Engineering_DjangoExpert_A",
        client_agent_id="django_expert_a_001"
    )
    
    # Example: Connect to another agent (React expert)
    # In real usage, this would connect to an actual running MCP server
    print("MCP Agent Client Demonstration")
    print(f"Client: {client.client_name}")
    print(f"Client ID: {client.client_id}")
    
    # Example operations that would be performed:
    print("\nExample Operations:")
    print("1. Connect to React Expert agent")
    print("2. Discover React Expert's capabilities")
    print("3. Call code analysis tool on React code")
    print("4. Collaborate on full-stack task")
    print("5. Execute API deployment workflow")
    
    # Example connection status
    status = client.get_connection_status()
    print(f"\nConnection Status: {json.dumps(status, indent=2)}")

if __name__ == "__main__":
    asyncio.run(demonstrate_client())
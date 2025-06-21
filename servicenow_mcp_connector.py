#!/usr/bin/env python3
"""
ServiceNow MCP Connector
Connects to the ServiceNow MCP server and provides tool access
Based on: https://github.com/echelon-ai-labs/servicenow-mcp
"""
import os
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServiceNowConfig:
    """Configuration for ServiceNow connection"""
    instance_url: str
    username: str
    password: str
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables"""
        return cls(
            instance_url=os.getenv("SERVICENOW_INSTANCE_URL", ""),
            username=os.getenv("SERVICENOW_USERNAME", ""),
            password=os.getenv("SERVICENOW_PASSWORD", "")
        )

class ServiceNowMCPConnector:
    """
    Connector for ServiceNow MCP Server
    Provides access to ServiceNow tools via MCP protocol
    """
    
    def __init__(self, config: ServiceNowConfig):
        self.config = config
        self.session: Optional[ClientSession] = None
        self.available_tools: List[Any] = []
        self.connected = False
    
    async def connect(self) -> bool:
        """
        Connect to ServiceNow MCP server
        The server should already be running (e.g., via Claude desktop)
        """
        try:
            # ServiceNow MCP server parameters
            server_params = StdioServerParameters(
                command="npx",
                args=["-y", "@echelon-ai-labs/servicenow-mcp"],
                env={
                    "SERVICENOW_INSTANCE_URL": self.config.instance_url,
                    "SERVICENOW_USERNAME": self.config.username,
                    "SERVICENOW_PASSWORD": self.config.password,
                    "MCP_TOOL_PACKAGE": "service_desk"  # Start with service desk tools
                }
            )
            
            logger.info("Connecting to ServiceNow MCP server...")
            
            # Establish connection
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    
                    # Initialize the session
                    await session.initialize()
                    
                    # Get server info
                    server_info = session.server
                    logger.info(f"Connected to: {server_info.name} v{server_info.version}")
                    
                    # List available tools
                    self.available_tools = await session.list_tools()
                    logger.info(f"Available tools: {len(self.available_tools)}")
                    
                    for tool in self.available_tools:
                        logger.info(f"  - {tool.name}: {tool.description}")
                    
                    self.connected = True
                    
                    # Keep the session alive for this demo
                    await self._run_demo()
                    
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to ServiceNow MCP: {e}")
            self.connected = False
            return False
    
    async def _run_demo(self):
        """Run demo interactions with ServiceNow"""
        if not self.session:
            return
        
        # Demo 1: Search for incidents
        print("\n📋 Demo 1: Searching for incidents...")
        try:
            result = await self.session.call_tool(
                "search_incidents",
                arguments={
                    "query": "state=1",  # Active incidents
                    "limit": 5
                }
            )
            print(f"Result: {self._format_result(result)}")
        except Exception as e:
            print(f"Error searching incidents: {e}")
        
        # Demo 2: Create an incident
        print("\n📋 Demo 2: Creating an incident...")
        try:
            result = await self.session.call_tool(
                "create_incident",
                arguments={
                    "short_description": "Test incident from MCP integration",
                    "description": "This is a test incident created via ServiceNow MCP",
                    "urgency": "3",
                    "impact": "3",
                    "category": "Software"
                }
            )
            print(f"Result: {self._format_result(result)}")
        except Exception as e:
            print(f"Error creating incident: {e}")
        
        # Demo 3: Get available tools info
        print("\n📋 Demo 3: Available ServiceNow Tools:")
        for tool in self.available_tools[:10]:  # Show first 10 tools
            print(f"\n🔧 {tool.name}")
            print(f"   Description: {tool.description}")
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(f"   Parameters:")
                props = tool.inputSchema.get('properties', {})
                for param, schema in props.items():
                    required = param in tool.inputSchema.get('required', [])
                    print(f"     - {param}: {schema.get('type', 'any')} {'(required)' if required else '(optional)'}")
    
    def _format_result(self, result) -> str:
        """Format MCP result for display"""
        if hasattr(result, 'content'):
            if isinstance(result.content, list):
                texts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        texts.append(item.text)
                    elif hasattr(item, 'type') and item.type == 'text':
                        texts.append(str(item))
                return "\n".join(texts)
            return str(result.content)
        return json.dumps(result, indent=2, default=str)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a ServiceNow tool via MCP
        
        Args:
            tool_name: Name of the tool (e.g., 'search_incidents')
            arguments: Tool arguments as a dictionary
            
        Returns:
            Tool execution result
        """
        if not self.session:
            raise Exception("Not connected to ServiceNow MCP server")
        
        try:
            result = await self.session.call_tool(tool_name, arguments=arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise
    
    async def get_tool_info(self, tool_name: str) -> Optional[Any]:
        """Get information about a specific tool"""
        for tool in self.available_tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return [tool.name for tool in self.available_tools]

# Standalone tool functions that agents can use
class ServiceNowTools:
    """
    ServiceNow tools that can be used by agents
    These wrap the MCP connector for easy use
    """
    
    def __init__(self, connector: ServiceNowMCPConnector):
        self.connector = connector
    
    async def search_incidents(self, query: str = "state=1", limit: int = 10) -> str:
        """Search for incidents in ServiceNow"""
        result = await self.connector.call_tool(
            "search_incidents",
            {"query": query, "limit": limit}
        )
        return self.connector._format_result(result)
    
    async def create_incident(
        self,
        short_description: str,
        description: str = "",
        urgency: str = "3",
        impact: str = "3",
        category: str = "Software"
    ) -> str:
        """Create a new incident in ServiceNow"""
        result = await self.connector.call_tool(
            "create_incident",
            {
                "short_description": short_description,
                "description": description or short_description,
                "urgency": urgency,
                "impact": impact,
                "category": category
            }
        )
        return self.connector._format_result(result)
    
    async def update_incident(
        self,
        incident_id: str,
        state: Optional[str] = None,
        work_notes: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> str:
        """Update an existing incident"""
        args = {"incident_id": incident_id}
        if state:
            args["state"] = state
        if work_notes:
            args["work_notes"] = work_notes
        if assigned_to:
            args["assigned_to"] = assigned_to
        
        result = await self.connector.call_tool("update_incident", args)
        return self.connector._format_result(result)
    
    async def get_incident(self, incident_id: str) -> str:
        """Get details of a specific incident"""
        result = await self.connector.call_tool(
            "get_incident",
            {"incident_id": incident_id}
        )
        return self.connector._format_result(result)

async def main():
    """Demo the ServiceNow MCP connection"""
    print("🔌 ServiceNow MCP Connector Demo")
    print("="*60)
    
    # Load config from environment
    config = ServiceNowConfig.from_env()
    
    if not config.instance_url:
        print("❌ ServiceNow configuration not found in environment")
        print("Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD")
        return
    
    print(f"Instance: {config.instance_url}")
    print(f"Username: {config.username}")
    print("Password: ***")
    
    # Create connector
    connector = ServiceNowMCPConnector(config)
    
    # Connect to ServiceNow MCP
    await connector.connect()

if __name__ == "__main__":
    asyncio.run(main())
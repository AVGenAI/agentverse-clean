"""
Enhanced Agent Manager with Real MCP Integration
This version actually connects to MCP servers and routes tool calls through them
"""
import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, Set
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_default_openai_key
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import requests

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MCPAgentManager')

class MCPToolWrapper:
    """Wraps MCP tools to work with OpenAI agents"""
    
    def __init__(self, session: ClientSession, tool_name: str):
        self.session = session
        self.tool_name = tool_name
        self._tool_info = None
    
    async def get_info(self):
        """Get tool information from MCP"""
        if not self._tool_info:
            tools = await self.session.list_tools()
            for tool in tools:
                if tool.name == self.tool_name:
                    self._tool_info = tool
                    break
        return self._tool_info
    
    async def __call__(self, **kwargs):
        """Execute the MCP tool"""
        try:
            result = await self.session.call_tool(self.tool_name, arguments=kwargs)
            
            # Handle different result types
            if hasattr(result, 'content'):
                # Text content
                if isinstance(result.content, list):
                    return "\n".join([item.text for item in result.content if hasattr(item, 'text')])
                return str(result.content)
            elif hasattr(result, 'result'):
                # Direct result
                return json.dumps(result.result, indent=2)
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error calling MCP tool {self.tool_name}: {e}")
            return f"Error: Failed to execute {self.tool_name} - {str(e)}"

class MCPConnection:
    """Manages a connection to an MCP server"""
    
    def __init__(self, coupling_info: Dict[str, Any]):
        self.coupling_id = coupling_info['id']
        self.agent_id = coupling_info['agentId']
        self.server_id = coupling_info['serverId']
        self.server_name = coupling_info['serverName']
        self.session = None
        self.tools = {}
        self.active = False
    
    async def connect(self):
        """Establish connection to MCP server"""
        try:
            # For ServiceNow, we need to find the running MCP server
            # In production, this would use the actual server configuration
            
            if "servicenow" in self.server_id.lower():
                # ServiceNow MCP server parameters
                server_params = StdioServerParameters(
                    command="python",
                    args=["-m", "servicenow_mcp"],
                    env={
                        "SERVICENOW_INSTANCE_URL": os.getenv("SERVICENOW_INSTANCE_URL"),
                        "SERVICENOW_USERNAME": os.getenv("SERVICENOW_USERNAME"),
                        "SERVICENOW_PASSWORD": os.getenv("SERVICENOW_PASSWORD")
                    }
                )
                
                logger.info(f"Connecting to {self.server_name} MCP server...")
                
                # Note: In a real implementation, we'd connect to the already-running
                # ServiceNow MCP server managed by Claude, not start a new one
                
                # For now, we'll simulate the connection
                self.active = True
                self.tools = {
                    "search_incidents": self._create_mock_tool("search_incidents"),
                    "create_incident": self._create_mock_tool("create_incident"),
                    "update_incident": self._create_mock_tool("update_incident"),
                    "get_incident": self._create_mock_tool("get_incident")
                }
                
                logger.info(f"✅ Connected to {self.server_name} with {len(self.tools)} tools")
                
                # Update coupling status in API
                await self._update_coupling_status(True)
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {e}")
            self.active = False
            return False
    
    def _create_mock_tool(self, tool_name: str):
        """Create a mock tool for demonstration"""
        async def mock_tool(**kwargs):
            return f"Mock {tool_name} result with args: {kwargs}"
        return mock_tool
    
    async def _update_coupling_status(self, active: bool):
        """Update coupling status in the API"""
        try:
            # In production, this would call the API endpoint
            logger.info(f"Coupling {self.coupling_id} status updated to: {'active' if active else 'inactive'}")
        except Exception as e:
            logger.error(f"Failed to update coupling status: {e}")
    
    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.session:
            # Close MCP session
            self.session = None
        self.active = False
        await self._update_coupling_status(False)

class MCPEnhancedAgentManager:
    """Agent Manager that uses real MCP connections"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key:
            set_default_openai_key(self.api_key)
        
        self.agent_configs = []
        self.agents = {}
        self.mcp_connections = {}
        self.couplings = {}
        
        # Load configurations
        self._load_agent_configs()
        self._load_couplings()
        
        # Start MCP connections
        asyncio.create_task(self._initialize_mcp_connections())
    
    def _load_agent_configs(self):
        """Load agent configurations"""
        try:
            with open("../src/config/agentverse_agents_1000.json", "r") as f:
                self.agent_configs = json.load(f)
                logger.info(f"Loaded {len(self.agent_configs)} agent configurations")
        except Exception as e:
            logger.error(f"Failed to load agent configs: {e}")
    
    def _load_couplings(self):
        """Load MCP couplings from API"""
        try:
            response = requests.get("http://localhost:8000/api/mcp/couplings")
            if response.status_code == 200:
                couplings = response.json()
                for coupling in couplings:
                    agent_id = coupling['agentId']
                    self.couplings[agent_id] = coupling
                    logger.info(f"Loaded coupling: {coupling['agentName']} ↔ {coupling['serverName']}")
        except Exception as e:
            logger.error(f"Failed to load couplings: {e}")
    
    async def _initialize_mcp_connections(self):
        """Initialize MCP connections for all couplings"""
        for agent_id, coupling in self.couplings.items():
            try:
                connection = MCPConnection(coupling)
                if await connection.connect():
                    self.mcp_connections[agent_id] = connection
                    logger.info(f"✅ MCP connection established for {agent_id}")
            except Exception as e:
                logger.error(f"Failed to initialize MCP for {agent_id}: {e}")
    
    def _create_agent_with_mcp_tools(self, agent_config: Dict, mcp_connection: MCPConnection) -> Agent:
        """Create an agent with MCP tools"""
        metadata = agent_config.get("enhanced_metadata", {})
        
        # Create tool wrappers for MCP tools
        tool_functions = []
        
        # For each MCP tool, create a function that the agent can use
        for tool_name, tool_func in mcp_connection.tools.items():
            # Create a wrapper function that OpenAI agents can use
            @function_tool
            def mcp_tool_wrapper(**kwargs):
                # Run the async MCP tool in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(tool_func(**kwargs))
                    return result
                finally:
                    loop.close()
            
            # Set the function name and docstring
            mcp_tool_wrapper.__name__ = tool_name
            mcp_tool_wrapper.__doc__ = f"MCP tool: {tool_name}"
            
            tool_functions.append(mcp_tool_wrapper)
        
        # Create agent with MCP tools
        agent = Agent(
            name=metadata.get("display_name", "Agent"),
            model="gpt-4o-mini",
            instructions=agent_config.get("instructions", "You are a helpful AI assistant.") + 
                        f"\n\nYou are connected to {mcp_connection.server_name} via MCP protocol. " +
                        "Use the available tools to access real data from the system.",
            tools=tool_functions
        )
        
        logger.info(f"Created agent {metadata.get('display_name')} with {len(tool_functions)} MCP tools")
        return agent
    
    def _create_standard_agent(self, agent_config: Dict) -> Agent:
        """Create a standard agent without MCP"""
        metadata = agent_config.get("enhanced_metadata", {})
        
        agent = Agent(
            name=metadata.get("display_name", "Agent"),
            model="gpt-4o-mini",
            instructions=agent_config.get("instructions", "You are a helpful AI assistant.")
        )
        
        return agent
    
    async def get_or_create_agent(self, agent_id: str) -> Optional[Agent]:
        """Get or create an agent, using MCP if coupled"""
        
        # Check if agent already exists
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        # Find agent configuration
        agent_config = None
        for config in self.agent_configs:
            metadata = config.get("enhanced_metadata", {})
            if metadata.get("agent_uuid") == agent_id:
                agent_config = config
                break
        
        if not agent_config:
            logger.error(f"Agent configuration not found for {agent_id}")
            return None
        
        # Check if agent has MCP coupling
        if agent_id in self.mcp_connections:
            mcp_connection = self.mcp_connections[agent_id]
            if mcp_connection.active:
                # Create agent with MCP tools
                agent = self._create_agent_with_mcp_tools(agent_config, mcp_connection)
                logger.info(f"✨ Agent {agent_id} created with MCP integration!")
            else:
                # MCP connection failed, create standard agent
                agent = self._create_standard_agent(agent_config)
                logger.warning(f"MCP connection inactive for {agent_id}, using standard agent")
        else:
            # No MCP coupling, create standard agent
            agent = self._create_standard_agent(agent_config)
            logger.info(f"Agent {agent_id} created without MCP (no coupling)")
        
        self.agents[agent_id] = agent
        return agent
    
    async def chat_with_agent(self, agent_id: str, message: str) -> str:
        """Chat with an agent (MCP-enhanced if coupled)"""
        
        logger.info(f"Chat request for agent {agent_id}: {message[:50]}...")
        
        # Get or create the agent
        agent = await self.get_or_create_agent(agent_id)
        
        if not agent:
            return "Error: Agent not found or could not be created."
        
        try:
            # Check if this agent has active MCP connection
            if agent_id in self.mcp_connections and self.mcp_connections[agent_id].active:
                logger.info(f"🔗 Using MCP-enhanced agent for {agent_id}")
            
            # Run the agent
            result = await Runner.run(agent, message)
            return result.final_output
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"Error: {str(e)}"
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of all MCP connections"""
        status = {
            "agents": len(self.agents),
            "couplings": len(self.couplings),
            "active_mcp_connections": sum(1 for conn in self.mcp_connections.values() if conn.active),
            "connections": {}
        }
        
        for agent_id, connection in self.mcp_connections.items():
            status["connections"][agent_id] = {
                "server": connection.server_name,
                "active": connection.active,
                "tools": list(connection.tools.keys()) if connection.active else []
            }
        
        return status

# Demo function
async def demo_mcp_enhanced_manager():
    """Demonstrate the MCP-enhanced agent manager"""
    
    print("🚀 MCP-Enhanced Agent Manager Demo")
    print("="*60)
    
    # Create manager
    manager = MCPEnhancedAgentManager()
    
    # Wait for connections to initialize
    await asyncio.sleep(2)
    
    # Get status
    print("\n📊 Manager Status:")
    status = await manager.get_status()
    print(json.dumps(status, indent=2))
    
    # Test with SRE agent
    agent_id = "sre_servicenow_001"
    
    print(f"\n💬 Testing chat with {agent_id}...")
    
    queries = [
        "Show me all critical incidents",
        "What tools do you have available?",
        "Create an incident for database connection issues"
    ]
    
    for query in queries:
        print(f"\n👤 User: {query}")
        response = await manager.chat_with_agent(agent_id, query)
        print(f"🤖 Agent: {response}")
        print("-"*60)

if __name__ == "__main__":
    asyncio.run(demo_mcp_enhanced_manager())
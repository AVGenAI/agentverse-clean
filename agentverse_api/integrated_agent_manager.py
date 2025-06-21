"""
Integrated Agent Manager: Agent + MCP + LLM (OpenAI GPT-4o)
The production-ready implementation of the killer combo
"""
import os
import json
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dotenv import load_dotenv

from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import requests

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('IntegratedAgentManager')

class IntegratedAgent:
    """
    The perfect fusion of Agent + MCP + LLM
    Each agent has:
    - Personality and expertise (Agent layer)
    - Tool access via MCP (Integration layer)  
    - GPT-4o intelligence (LLM layer)
    """
    
    def __init__(self, config: Dict[str, Any], mcp_session: Optional[ClientSession] = None):
        self.config = config
        self.metadata = config.get("enhanced_metadata", {})
        self.id = self.metadata.get("agent_uuid")
        self.name = self.metadata.get("display_name", "Agent")
        self.instructions = config.get("instructions", "")
        self.mcp_session = mcp_session
        self.mcp_tools = []
        
        # Initialize OpenAI
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Load MCP tools if connected
        if self.mcp_session:
            asyncio.create_task(self._load_mcp_tools())
    
    async def _load_mcp_tools(self):
        """Load available tools from MCP server"""
        try:
            tools = await self.mcp_session.list_tools()
            self.mcp_tools = tools
            logger.info(f"Loaded {len(tools)} MCP tools for {self.name}")
            for tool in tools:
                logger.info(f"  - {tool.name}: {tool.description}")
        except Exception as e:
            logger.error(f"Failed to load MCP tools: {e}")
    
    async def think(self, user_message: str) -> str:
        """
        The agent thinks about the user's message and decides what to do
        This is where GPT-4o shines - reasoning about when and how to use tools
        """
        
        # Build the system prompt with agent personality and available tools
        system_prompt = f"""{self.instructions}

You are {self.name}, an expert in your domain.

Available MCP Tools:
{self._format_tools_for_prompt()}

When responding:
1. Analyze if the user's request needs real data from tools
2. If yes, specify which tool to use and with what parameters
3. Format your response based on the tool results
4. Always be helpful and professional

Respond in this format when tools are needed:
THOUGHT: [Your reasoning about what the user needs]
TOOL: [tool_name]
PARAMS: {{"param1": "value1", "param2": "value2"}}

Otherwise, respond normally without the special format."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # Using the most capable model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM error: {e}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    def _format_tools_for_prompt(self) -> str:
        """Format MCP tools for the LLM prompt"""
        if not self.mcp_tools:
            return "No MCP tools available. Respond based on your knowledge."
        
        tools_desc = []
        for tool in self.mcp_tools:
            # Format tool info for LLM understanding
            params = []
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                props = tool.inputSchema.get('properties', {})
                for param, schema in props.items():
                    param_type = schema.get('type', 'string')
                    param_desc = schema.get('description', '')
                    required = param in tool.inputSchema.get('required', [])
                    params.append(f"  - {param} ({param_type}): {param_desc} {'[required]' if required else '[optional]'}")
            
            tool_desc = f"- {tool.name}: {tool.description}"
            if params:
                tool_desc += "\n  Parameters:\n" + "\n".join(params)
            tools_desc.append(tool_desc)
        
        return "\n".join(tools_desc)
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """Execute an MCP tool and return the result"""
        if not self.mcp_session:
            return "Error: No MCP connection available"
        
        try:
            logger.info(f"Executing MCP tool: {tool_name} with params: {params}")
            result = await self.mcp_session.call_tool(tool_name, arguments=params)
            
            # Process the result based on type
            if hasattr(result, 'content'):
                if isinstance(result.content, list):
                    return "\n".join([item.text for item in result.content if hasattr(item, 'text')])
                return str(result.content)
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return f"Error executing {tool_name}: {str(e)}"
    
    async def respond(self, user_message: str) -> str:
        """
        Complete response cycle: Think → Execute → Synthesize
        """
        
        # Step 1: Think about the request
        thought_response = await self.think(user_message)
        
        # Step 2: Check if tool execution is needed
        if "TOOL:" in thought_response and "PARAMS:" in thought_response:
            # Parse the tool request
            lines = thought_response.split('\n')
            tool_name = None
            params = {}
            thought = ""
            
            for i, line in enumerate(lines):
                if line.startswith("THOUGHT:"):
                    thought = line.replace("THOUGHT:", "").strip()
                elif line.startswith("TOOL:"):
                    tool_name = line.replace("TOOL:", "").strip()
                elif line.startswith("PARAMS:"):
                    # Parse JSON params
                    try:
                        param_str = line.replace("PARAMS:", "").strip()
                        # Look for JSON on this line or subsequent lines
                        if param_str.startswith("{"):
                            params = json.loads(param_str)
                        else:
                            # Multi-line JSON
                            json_lines = [param_str]
                            for j in range(i+1, len(lines)):
                                json_lines.append(lines[j])
                                if lines[j].strip().endswith("}"):
                                    break
                            params = json.loads("\n".join(json_lines))
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse params: {e}")
            
            if tool_name:
                # Execute the tool
                tool_result = await self.execute_tool(tool_name, params)
                
                # Step 3: Synthesize final response with tool results
                synthesis_prompt = f"""Based on this tool execution result, provide a helpful response to the user.

User Query: {user_message}
Your Analysis: {thought}
Tool Used: {tool_name}
Tool Result:
{tool_result}

Format this information in a clear, professional way for the user."""

                try:
                    final_response = self.openai_client.chat.completions.create(
                        model="gpt-4o-mini",  # Use faster model for synthesis
                        messages=[
                            {"role": "system", "content": self.instructions},
                            {"role": "user", "content": synthesis_prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    return final_response.choices[0].message.content
                    
                except Exception as e:
                    # Fallback response
                    return f"{thought}\n\nTool Result ({tool_name}):\n{tool_result}"
        
        # No tool needed, return the direct response
        return thought_response

class IntegratedAgentManager:
    """
    Manages the integrated Agent + MCP + LLM system
    """
    
    def __init__(self):
        self.agents = {}
        self.mcp_connections = {}
        self.agent_configs = []
        self.couplings = {}
        
        # Load configurations
        self._load_configurations()
    
    def _load_configurations(self):
        """Load agent configs and couplings"""
        # Load agents
        try:
            with open("src/config/agentverse_agents_1000.json", "r") as f:
                self.agent_configs = json.load(f)
                logger.info(f"Loaded {len(self.agent_configs)} agents")
        except Exception as e:
            logger.error(f"Failed to load agents: {e}")
        
        # Load couplings
        try:
            response = requests.get("http://localhost:8000/api/mcp/couplings")
            if response.status_code == 200:
                for coupling in response.json():
                    self.couplings[coupling['agentId']] = coupling
                logger.info(f"Loaded {len(self.couplings)} MCP couplings")
        except Exception as e:
            logger.error(f"Failed to load couplings: {e}")
    
    async def get_agent(self, agent_id: str) -> Optional[IntegratedAgent]:
        """Get or create an integrated agent"""
        
        # Return existing agent
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        # Find agent config
        agent_config = None
        for config in self.agent_configs:
            if config.get("enhanced_metadata", {}).get("agent_uuid") == agent_id:
                agent_config = config
                break
        
        if not agent_config:
            logger.error(f"Agent {agent_id} not found")
            return None
        
        # Check for MCP coupling
        mcp_session = None
        if agent_id in self.couplings:
            coupling = self.couplings[agent_id]
            logger.info(f"Agent {agent_id} has MCP coupling to {coupling['serverName']}")
            
            # In production, we'd connect to the actual MCP server here
            # For now, we'll note that the connection should be established
            logger.info(f"TODO: Connect to MCP server {coupling['serverId']}")
        
        # Create integrated agent
        agent = IntegratedAgent(agent_config, mcp_session)
        self.agents[agent_id] = agent
        
        logger.info(f"Created integrated agent: {agent.name}")
        return agent
    
    async def chat(self, agent_id: str, message: str) -> str:
        """Chat with an integrated agent"""
        
        agent = await self.get_agent(agent_id)
        if not agent:
            return "Error: Agent not found"
        
        logger.info(f"Chat with {agent.name}: {message[:50]}...")
        
        try:
            response = await agent.respond(message)
            return response
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"

# Demo the integrated system
async def demo_integrated_system():
    """Demonstrate the Agent + MCP + LLM integration"""
    
    print("🚀 Integrated Agent System Demo")
    print("="*60)
    print("Architecture: Agent + MCP + LLM (GPT-4o)")
    print("="*60)
    
    manager = IntegratedAgentManager()
    
    # Test with SRE agent
    agent_id = "sre_servicenow_001"
    
    queries = [
        "What capabilities do you have?",
        "Show me any critical incidents",
        "What's your approach to incident management?",
        "How do you calculate SLO compliance?"
    ]
    
    for query in queries:
        print(f"\n👤 User: {query}")
        response = await manager.chat(agent_id, query)
        print(f"\n🤖 Agent: {response}")
        print("-"*60)

if __name__ == "__main__":
    asyncio.run(demo_integrated_system())
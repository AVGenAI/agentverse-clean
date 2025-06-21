"""
Enhanced Agent Manager with MCP Integration
This is a proof-of-concept showing how agents should use MCP tools
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI
import re

load_dotenv()

class MCPEnhancedAgentManager:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_client = OpenAI(api_key=self.api_key)
        self.agent_configs = []
        self.active_couplings = {}
        
        # Load agent configurations
        try:
            with open("../src/config/agentverse_agents_1000.json", "r") as f:
                self.agent_configs = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load agent configs: {e}")
            
        # Load active couplings
        self._load_active_couplings()
    
    def _load_active_couplings(self):
        """Load active MCP couplings from the API"""
        try:
            import requests
            response = requests.get("http://localhost:8000/api/mcp/couplings")
            if response.status_code == 200:
                couplings = response.json()
                for coupling in couplings:
                    agent_id = coupling['agentId']
                    self.active_couplings[agent_id] = coupling
                    print(f"📎 Loaded coupling: {coupling['agentName']} ↔ {coupling['serverName']}")
        except Exception as e:
            print(f"Warning: Could not load couplings: {e}")
    
    async def chat_with_agent_mcp(self, agent_id: str, message: str) -> str:
        """Enhanced chat that uses MCP tools when available"""
        
        # Find agent configuration
        agent_config = None
        for config in self.agent_configs:
            metadata = config.get("enhanced_metadata", {})
            if metadata.get("agent_uuid") == agent_id:
                agent_config = config
                break
        
        if not agent_config:
            return "Agent not found."
        
        metadata = agent_config.get("enhanced_metadata", {})
        agent_name = metadata.get("display_name", "Agent")
        
        # Check if agent has an active MCP coupling
        coupling = self.active_couplings.get(agent_id)
        
        if coupling and "servicenow" in coupling['serverId'].lower():
            print(f"🔗 Agent has ServiceNow MCP coupling: {coupling['serverName']}")
            
            # Analyze the message to determine if MCP tools are needed
            tool_needed = self._analyze_message_for_tools(message)
            
            if tool_needed:
                print(f"🛠️  Tool needed: {tool_needed}")
                
                # Call the MCP tool
                tool_result = await self._call_mcp_tool(coupling, tool_needed, message)
                
                if tool_result:
                    # Use OpenAI to format the response with real data
                    return await self._format_response_with_data(
                        agent_config, message, tool_result
                    )
        
        # Fallback to regular OpenAI response
        return self._get_openai_response(agent_config, message)
    
    def _analyze_message_for_tools(self, message: str) -> Optional[str]:
        """Determine which MCP tool is needed based on the message"""
        message_lower = message.lower()
        
        # ServiceNow tool mappings
        tool_mappings = {
            "search_incidents": [
                "show incidents", "list incidents", "open incidents", 
                "critical incidents", "incidents from", "find incidents",
                "get incidents", "what incidents", "incident status"
            ],
            "create_incident": [
                "create incident", "new incident", "report incident",
                "raise incident", "log incident"
            ],
            "update_incident": [
                "update incident", "change incident", "modify incident",
                "resolve incident", "close incident"
            ],
            "search_changes": [
                "show changes", "list changes", "change requests",
                "scheduled changes", "pending changes"
            ],
            "search_problems": [
                "show problems", "list problems", "problem records",
                "root cause", "problem management"
            ],
            "get_knowledge_articles": [
                "knowledge articles", "kb articles", "documentation",
                "knowledge base", "how to"
            ]
        }
        
        for tool, keywords in tool_mappings.items():
            if any(keyword in message_lower for keyword in keywords):
                return tool
        
        return None
    
    async def _call_mcp_tool(self, coupling: Dict, tool_name: str, message: str) -> Optional[Dict]:
        """Call an MCP tool through the coupling"""
        
        # Extract parameters from the message
        params = self._extract_tool_parameters(tool_name, message)
        
        # Simulate MCP tool call (in real implementation, this would use MCP client)
        print(f"🔧 Calling MCP tool: {tool_name} with params: {params}")
        
        # For demo purposes, return simulated ServiceNow data
        if tool_name == "search_incidents":
            return {
                "incidents": [
                    {
                        "number": "INC0012345",
                        "short_description": "Payment service high latency",
                        "priority": "1 - Critical",
                        "state": "In Progress",
                        "assigned_to": "SRE Team",
                        "created": "2025-06-20 17:00:00"
                    },
                    {
                        "number": "INC0012346", 
                        "short_description": "Database connection pool exhausted",
                        "priority": "2 - High",
                        "state": "New",
                        "assigned_to": "Database Team",
                        "created": "2025-06-20 16:30:00"
                    },
                    {
                        "number": "INC0012347",
                        "short_description": "SSL certificate expiring soon",
                        "priority": "3 - Moderate",
                        "state": "In Progress", 
                        "assigned_to": "Security Team",
                        "created": "2025-06-20 15:00:00"
                    }
                ],
                "total": 3,
                "source": "ServiceNow Instance: dev329779"
            }
        
        elif tool_name == "create_incident":
            return {
                "incident": {
                    "number": "INC0012348",
                    "sys_id": "abc123def456",
                    "short_description": params.get("short_description", "New incident"),
                    "priority": params.get("priority", "3 - Moderate"),
                    "state": "New",
                    "created": "2025-06-20 18:30:00"
                },
                "message": "Incident created successfully"
            }
        
        return None
    
    def _extract_tool_parameters(self, tool_name: str, message: str) -> Dict[str, Any]:
        """Extract parameters for the tool from the message"""
        params = {}
        
        if tool_name == "search_incidents":
            # Extract filters from message
            if "critical" in message.lower():
                params["priority"] = "1"
            if "today" in message.lower():
                params["created_on"] = "today"
            if "open" in message.lower() or "active" in message.lower():
                params["state"] = "1,2,3"  # New, In Progress, On Hold
            
            params["limit"] = 10
            
        elif tool_name == "create_incident":
            # Extract incident details
            params["short_description"] = self._extract_description(message)
            
            if "critical" in message.lower() or "urgent" in message.lower():
                params["priority"] = "1"
                params["urgency"] = "1"
            else:
                params["priority"] = "3"
                params["urgency"] = "3"
            
            params["category"] = "Software"
            params["caller_id"] = "admin"
        
        return params
    
    def _extract_description(self, message: str) -> str:
        """Extract description from message"""
        # Look for quoted text
        quoted = re.findall(r'"([^"]*)"', message)
        if quoted:
            return quoted[0]
        
        # Look for text after "for" or "about"
        patterns = [
            r'(?:for|about|regarding)\s+(.+?)(?:\.|$)',
            r'(?:incident|issue|problem)\s+(?:with|on|in)\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return "Incident created via chat"
    
    async def _format_response_with_data(self, agent_config: Dict, message: str, tool_result: Dict) -> str:
        """Use OpenAI to format the response with real ServiceNow data"""
        
        metadata = agent_config.get("enhanced_metadata", {})
        agent_name = metadata.get("display_name", "Agent")
        instructions = agent_config.get("instructions", "")
        
        # Create a prompt that includes the real data
        system_message = f"""{instructions}

You are {agent_name} with access to real ServiceNow data.
Format the following ServiceNow data into a helpful response for the user.
Include specific details like incident numbers, priorities, and assignments.
Be conversational but precise with the data."""

        user_message = f"""User asked: {message}

ServiceNow returned this data:
{json.dumps(tool_result, indent=2)}

Provide a helpful response using this real data."""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content + "\n\n*[Data source: ServiceNow MCP Integration]*"
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            # Fallback to formatted data
            return self._format_fallback_response(tool_result)
    
    def _format_fallback_response(self, tool_result: Dict) -> str:
        """Fallback formatting if OpenAI fails"""
        if "incidents" in tool_result:
            response = f"Found {tool_result['total']} incidents:\n\n"
            for inc in tool_result['incidents']:
                response += f"• **{inc['number']}** - {inc['short_description']}\n"
                response += f"  Priority: {inc['priority']} | Status: {inc['state']} | Assigned: {inc['assigned_to']}\n\n"
            return response
        
        return json.dumps(tool_result, indent=2)
    
    def _get_openai_response(self, agent_config: Dict, message: str) -> str:
        """Standard OpenAI response without MCP data"""
        metadata = agent_config.get("enhanced_metadata", {})
        agent_name = metadata.get("display_name", "Agent")
        instructions = agent_config.get("instructions", "")
        skills = metadata.get("capabilities", {}).get("primary_expertise", [])
        
        system_message = f"{instructions}\n\nYour name is {agent_name} and you specialize in: {', '.join(skills[:5])}"
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error: {e}"


# Demo function
async def demo_mcp_chat():
    """Demonstrate MCP-enhanced chat"""
    manager = MCPEnhancedAgentManager()
    
    print("\n🎭 MCP-Enhanced Agent Chat Demo")
    print("="*60)
    
    agent_id = "sre_servicenow_001"
    
    # Test queries
    queries = [
        "Show me all critical incidents from today",
        "Create a new incident for the payment service being down",
        "What's the status of incident INC0012345?",
        "How do I handle a database connection issue?"  # This won't use MCP
    ]
    
    for query in queries:
        print(f"\n👤 User: {query}")
        response = await manager.chat_with_agent_mcp(agent_id, query)
        print(f"\n🤖 SRE Agent: {response}")
        print("-"*60)


if __name__ == "__main__":
    asyncio.run(demo_mcp_chat())
#!/usr/bin/env python3
"""
Clean SRE Agent Implementation
Direct integration: OpenAI LLM + ServiceNow MCP Server
No complex dependencies - just what works
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from openai import OpenAI
import aiohttp
import logging

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SREAgent')

class ServiceNowMCPConnector:
    """Direct connection to ServiceNow via MCP or REST API"""
    def __init__(self):
        self.instance_url = os.getenv("SERVICENOW_INSTANCE_URL", "https://dev329779.service-now.com")
        self.username = os.getenv("SERVICENOW_USERNAME", "admin")
        self.password = os.getenv("SERVICENOW_PASSWORD", "")
        self.session = None
        
    async def connect(self):
        """Initialize connection"""
        self.session = aiohttp.ClientSession(
            auth=aiohttp.BasicAuth(self.username, self.password)
        )
        logger.info(f"Connected to ServiceNow: {self.instance_url}")
        
    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()
            
    async def search_incidents(self, query: str = "active=true", limit: int = 10) -> Dict:
        """Search incidents in ServiceNow"""
        try:
            url = f"{self.instance_url}/api/now/table/incident"
            params = {
                "sysparm_query": query,
                "sysparm_limit": limit,
                "sysparm_fields": "number,short_description,priority,state,assigned_to,sys_id"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return {"success": True, "incidents": data.get("result", [])}
                else:
                    logger.error(f"ServiceNow API error: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error searching incidents: {e}")
            # Fallback to mock data
            return {
                "success": False,
                "mock": True,
                "incidents": [
                    {
                        "number": "INC0012345",
                        "short_description": "Payment service high latency",
                        "priority": "1",
                        "state": "2",
                        "assigned_to": {"display_value": "SRE Team"}
                    }
                ]
            }
            
    async def create_incident(self, data: Dict) -> Dict:
        """Create incident in ServiceNow"""
        try:
            url = f"{self.instance_url}/api/now/table/incident"
            
            async with self.session.post(url, json=data) as response:
                if response.status == 201:
                    result = await response.json()
                    return {"success": True, "incident": result.get("result")}
                else:
                    return {"success": False, "error": f"API error: {response.status}"}
                    
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            # Fallback mock response
            return {
                "success": False,
                "mock": True,
                "incident": {
                    "number": f"INC00{datetime.now().strftime('%H%M%S')}",
                    "sys_id": "mock_id",
                    "short_description": data.get("short_description", "")
                }
            }

class SREAgent:
    """Clean SRE Agent with OpenAI + ServiceNow integration"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.servicenow = ServiceNowMCPConnector()
        self.model = "gpt-4o-mini"
        
        # Define tools for OpenAI function calling
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_incidents",
                    "description": "Search for incidents in ServiceNow",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "ServiceNow query string (e.g., 'priority=1' for critical)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Max number of results (default: 10)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_incident",
                    "description": "Create a new incident in ServiceNow",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "short_description": {
                                "type": "string",
                                "description": "Brief description of the incident"
                            },
                            "description": {
                                "type": "string",
                                "description": "Detailed description"
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["1", "2", "3", "4", "5"],
                                "description": "Priority (1=Critical, 2=High, 3=Moderate, 4=Low, 5=Planning)"
                            },
                            "urgency": {
                                "type": "string",
                                "enum": ["1", "2", "3"],
                                "description": "Urgency (1=High, 2=Medium, 3=Low)"
                            }
                        },
                        "required": ["short_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_slo_status",
                    "description": "Calculate SLO status for a service",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "service": {
                                "type": "string",
                                "description": "Name of the service"
                            },
                            "slo_type": {
                                "type": "string",
                                "enum": ["availability", "latency", "error_rate"],
                                "description": "Type of SLO to check"
                            }
                        },
                        "required": ["service"]
                    }
                }
            }
        ]
        
        self.system_prompt = """You are an expert Site Reliability Engineer with ServiceNow expertise.

Your primary responsibilities:
- Incident Management: Search, create, and manage incidents
- SLO Monitoring: Track service health and error budgets
- Root Cause Analysis: Investigate and resolve issues

Available tools:
- search_incidents: Find incidents in ServiceNow (use priority=1 for critical)
- create_incident: Create new incidents with proper priority
- calculate_slo_status: Check service SLO status

Always use tools when discussing incidents or SLO status. Be specific and actionable."""

    async def initialize(self):
        """Initialize connections"""
        await self.servicenow.connect()
        logger.info("SRE Agent initialized")
        
    async def cleanup(self):
        """Cleanup connections"""
        await self.servicenow.close()
        
    def calculate_slo_status(self, service: str, slo_type: str = "availability") -> Dict:
        """Calculate SLO status (mock for now, can integrate with real monitoring)"""
        import random
        
        base_values = {
            "availability": {"target": 99.9, "current": 99.85 + random.uniform(-0.1, 0.1)},
            "latency": {"target": 200, "current": 185 + random.uniform(-10, 10)},
            "error_rate": {"target": 0.1, "current": 0.08 + random.uniform(-0.02, 0.02)}
        }
        
        values = base_values.get(slo_type, base_values["availability"])
        error_budget_used = abs((values["current"] - values["target"]) / values["target"] * 100)
        error_budget_remaining = max(0, 100 - error_budget_used)
        
        return {
            "service": service,
            "slo_type": slo_type,
            "target": values["target"],
            "current": round(values["current"], 3),
            "error_budget_remaining": round(error_budget_remaining, 1),
            "status": "healthy" if error_budget_remaining > 20 else "at_risk"
        }
        
    async def execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """Execute a tool and return results"""
        logger.info(f"Executing tool: {tool_name} with args: {arguments}")
        
        if tool_name == "search_incidents":
            result = await self.servicenow.search_incidents(
                query=arguments.get("query", "active=true"),
                limit=arguments.get("limit", 10)
            )
            return result
            
        elif tool_name == "create_incident":
            data = {
                "short_description": arguments["short_description"],
                "description": arguments.get("description", arguments["short_description"]),
                "priority": arguments.get("priority", "3"),
                "urgency": arguments.get("urgency", "3"),
                "category": "Software",
                "caller_id": "admin"
            }
            result = await self.servicenow.create_incident(data)
            return result
            
        elif tool_name == "calculate_slo_status":
            result = self.calculate_slo_status(
                service=arguments["service"],
                slo_type=arguments.get("slo_type", "availability")
            )
            return result
            
        else:
            return {"error": f"Unknown tool: {tool_name}"}
            
    async def chat(self, message: str) -> str:
        """Process a chat message and return response"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        try:
            # First API call - let model decide on tools
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            assistant_message = response.choices[0].message
            
            # If tools were called, execute them
            if assistant_message.tool_calls:
                messages.append(assistant_message)
                
                for tool_call in assistant_message.tool_calls:
                    # Parse arguments
                    args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool
                    result = await self.execute_tool(tool_call.function.name, args)
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result)
                    })
                
                # Get final response with tool results
                final_response = self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
                
                return final_response.choices[0].message.content
            else:
                # No tools needed, return direct response
                return assistant_message.content
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error: {str(e)}"

async def main():
    """Test the SRE agent"""
    print("🚀 SRE Agent - Clean Implementation")
    print("="*60)
    
    # Create and initialize agent
    agent = SREAgent()
    await agent.initialize()
    
    # Test scenarios
    test_queries = [
        "Show me all critical incidents",
        "What's the SLO status for the payment service?",
        "Create a high priority incident: Login service returning 500 errors for 10% of requests",
        "Search for any database-related incidents"
    ]
    
    for query in test_queries:
        print(f"\n💬 User: {query}")
        print("-"*60)
        
        response = await agent.chat(query)
        print(f"🤖 SRE Agent: {response}")
        print("="*60)
    
    # Cleanup
    await agent.cleanup()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
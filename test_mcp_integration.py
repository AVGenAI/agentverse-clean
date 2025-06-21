#!/usr/bin/env python3
"""
Test MCP Integration with SRE Agent
This shows how the agent SHOULD interact with ServiceNow MCP
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_servicenow_mcp():
    """Test direct connection to ServiceNow MCP server"""
    print("🧪 Testing ServiceNow MCP Integration")
    print("="*50)
    
    # ServiceNow MCP server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "servicenow_mcp"],
        env={
            "SERVICENOW_INSTANCE_URL": "https://dev329779.service-now.com",
            "SERVICENOW_USERNAME": "admin", 
            "SERVICENOW_PASSWORD": "le7ukYL8=XJ^"
        }
    )
    
    try:
        print("\n1. Connecting to ServiceNow MCP server...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ Connected to ServiceNow MCP!")
                
                # Get server information
                server_info = session.server
                print(f"\n2. Server Info:")
                print(f"   Name: {server_info.name}")
                print(f"   Version: {server_info.version}")
                
                # List available tools
                print(f"\n3. Available Tools:")
                tools = await session.list_tools()
                for tool in tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Test getting incidents
                print(f"\n4. Testing incident retrieval...")
                result = await session.call_tool(
                    "search_incidents",
                    arguments={
                        "query": "state=1",  # Active incidents
                        "limit": 5
                    }
                )
                
                print(f"✅ Found {len(result.get('incidents', []))} incidents")
                for incident in result.get('incidents', [])[:3]:
                    print(f"   - {incident.get('number')}: {incident.get('short_description')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nThis error is expected if:")
        print("1. ServiceNow MCP server is not installed")
        print("2. The server is not in the Python path")
        print("3. The MCP server needs to be started differently")

async def test_through_api():
    """Test through the AgentVerse API"""
    import aiohttp
    
    print("\n\n🌐 Testing through AgentVerse API")
    print("="*50)
    
    async with aiohttp.ClientSession() as session:
        # Get coupling info
        async with session.get("http://localhost:8000/api/mcp/couplings") as resp:
            couplings = await resp.json()
            
        if couplings:
            coupling = couplings[0]
            print(f"\n✅ Found coupling: {coupling['agentName']} ↔ {coupling['serverName']}")
            print(f"   Status: {'Active' if coupling['active'] else 'Inactive'}")
            print(f"   Compatibility: {coupling['compatibility']}")
            
            # Get server tools
            server_id = coupling['serverId']
            async with session.get(f"http://localhost:8000/api/mcp/servers/{server_id}/tools") as resp:
                if resp.status == 200:
                    tools = await resp.json()
                    print(f"\n📦 Server exposes {len(tools)} tools")
                    for tool in tools[:5]:
                        print(f"   - {tool}")

if __name__ == "__main__":
    print("Testing ServiceNow MCP Integration\n")
    
    # Test direct connection
    asyncio.run(test_servicenow_mcp())
    
    # Test through API
    asyncio.run(test_through_api())
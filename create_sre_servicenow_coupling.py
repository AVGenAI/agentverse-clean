#!/usr/bin/env python3
"""
Create coupling between SRE Specialist Agent and ServiceNow MCP Server
"""
import requests
import json

API_URL = "http://localhost:8000"

def create_coupling():
    print("🔗 Creating SRE Agent + ServiceNow MCP Coupling")
    print("="*50)
    
    # Step 1: Find the SRE agent
    print("\n1. Finding SRE ServiceNow Specialist agent...")
    agents_response = requests.post(f"{API_URL}/agents", json={"limit": 100, "offset": 0})
    agents = agents_response.json()["agents"]
    
    sre_agent = None
    for agent in agents:
        if "SRE" in agent.get("display_name", "") and "ServiceNow" in agent.get("display_name", ""):
            sre_agent = agent
            break
    
    if not sre_agent:
        print("❌ SRE ServiceNow Specialist agent not found!")
        return
    
    print(f"✅ Found agent: {sre_agent['display_name']} (ID: {sre_agent['id']})")
    
    # Step 2: Find ServiceNow MCP server
    print("\n2. Finding ServiceNow MCP server...")
    servers_response = requests.get(f"{API_URL}/api/mcp/servers")
    servers = servers_response.json()
    
    servicenow_server = None
    for server in servers:
        if server["type"] == "servicenow" or "ServiceNow" in server["name"]:
            servicenow_server = server
            break
    
    if not servicenow_server:
        print("❌ ServiceNow MCP server not found!")
        return
        
    print(f"✅ Found server: {servicenow_server['name']} (ID: {servicenow_server['id']})")
    
    # Step 3: Check compatibility
    print("\n3. Checking compatibility...")
    compat_response = requests.post(
        f"{API_URL}/api/mcp/compatibility",
        json={
            "agentId": sre_agent["id"],
            "serverId": servicenow_server["id"]
        }
    )
    
    if compat_response.status_code == 200:
        compat_data = compat_response.json()
        print(f"✅ Compatibility: {compat_data.get('level', 'Unknown')}")
        print(f"   Score: {compat_data.get('score', 0)}")
    
    # Step 4: Create coupling
    print("\n4. Creating coupling...")
    coupling_response = requests.post(
        f"{API_URL}/api/mcp/couplings",
        json={
            "agentId": sre_agent["id"],
            "serverId": servicenow_server["id"]
        }
    )
    
    if coupling_response.status_code == 200:
        coupling = coupling_response.json()
        print(f"✅ Coupling created successfully!")
        print(f"   Coupling ID: {coupling.get('id', 'Unknown')}")
        print(f"   Status: Active")
        
        print("\n✨ Integration Complete!")
        print(f"\nYou can now:")
        print(f"1. Go to http://localhost:3000/chat")
        print(f"2. Select '{sre_agent['display_name']}'")
        print(f"3. Ask about ServiceNow incidents, changes, or problems")
        print(f"\nExample questions:")
        print(f"- 'Show me all open incidents'")
        print(f"- 'What are the critical incidents from today?'")
        print(f"- 'Create a new incident for the payment service'")
        
    else:
        print(f"❌ Failed to create coupling: {coupling_response.text}")

if __name__ == "__main__":
    create_coupling()
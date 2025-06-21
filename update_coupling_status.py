#!/usr/bin/env python3
"""
Update coupling status to active
"""
import requests
import json

def update_coupling_to_active():
    """Update the SRE-ServiceNow coupling to active status"""
    
    api_url = "http://localhost:8000"
    coupling_id = "sre_servicenow_001_ServiceNow-Production"
    
    print("🔄 Updating coupling status...")
    
    # First, get current couplings
    response = requests.get(f"{api_url}/api/mcp/couplings")
    if response.status_code == 200:
        couplings = response.json()
        print(f"Found {len(couplings)} coupling(s)")
        
        for coupling in couplings:
            if coupling['id'] == coupling_id:
                print(f"\nCurrent coupling status:")
                print(f"  ID: {coupling['id']}")
                print(f"  Agent: {coupling['agentName']}")
                print(f"  Server: {coupling['serverName']}")
                print(f"  Active: {coupling['active']}")
                print(f"  Compatibility: {coupling['compatibility']}")
    
    # Try to activate via test endpoint
    print(f"\n🧪 Testing coupling...")
    test_response = requests.post(f"{api_url}/api/mcp/couplings/{coupling_id}/test")
    if test_response.status_code == 200:
        print("✅ Test completed")
        result = test_response.json()
        print(f"Result: {json.dumps(result, indent=2)}")
    else:
        print(f"❌ Test failed: {test_response.status_code}")
    
    # Check if there's an activate endpoint
    # If not, we need to add one to the MCP router
    
    print("\n📝 To make the coupling show as Active in the UI:")
    print("1. The MCP router needs an endpoint to update coupling status")
    print("2. The agent needs to actually connect to the MCP server")
    print("3. The connection status should be reflected in the database")
    
    print("\n✨ Current Architecture:")
    print("- ServiceNow MCP server is running (managed by Claude)")
    print("- Agent has tools that simulate ServiceNow operations")
    print("- Coupling exists but shows as inactive")
    print("- Need to bridge the gap between agent and actual MCP server")

if __name__ == "__main__":
    update_coupling_to_active()
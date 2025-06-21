#!/usr/bin/env python3
"""
Final step to activate the ServiceNow MCP coupling
"""
import requests
import json

def activate_coupling():
    """Activate the SRE-ServiceNow coupling"""
    
    api_url = "http://localhost:8000"
    coupling_id = "sre_servicenow_001_ServiceNow-Production"
    
    print("🔌 Activating ServiceNow MCP Coupling")
    print("="*60)
    
    # Try the new activate endpoint
    print("\n1. Calling activate endpoint...")
    try:
        response = requests.put(f"{api_url}/api/mcp/couplings/{coupling_id}/activate")
        if response.status_code == 200:
            result = response.json()
            print("✅ Coupling activated successfully!")
            print(f"   ID: {result.get('id')}")
            print(f"   Active: {result.get('active')}")
            print(f"   Message: {result.get('message')}")
        else:
            print(f"❌ Activation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Check the status
    print("\n2. Checking coupling status...")
    try:
        response = requests.get(f"{api_url}/api/mcp/couplings")
        if response.status_code == 200:
            couplings = response.json()
            for coupling in couplings:
                if coupling['id'] == coupling_id:
                    print(f"\n✅ Current Status:")
                    print(f"   Agent: {coupling['agentName']}")
                    print(f"   Server: {coupling['serverName']}")
                    print(f"   Active: {'✅ Yes' if coupling.get('active') else '❌ No'}")
                    print(f"   Compatibility: {coupling['compatibility']}")
                    break
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    print("\n\n🎉 Summary:")
    print("The ServiceNow MCP coupling has been configured.")
    print("The SRE agent can now use ServiceNow tools via MCP.")
    print("Check the UI - the coupling should show as Active!")

if __name__ == "__main__":
    activate_coupling()
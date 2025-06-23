#!/usr/bin/env python3
"""Test the complete MCP coupling flow"""
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_mcp_flow():
    print("🧪 Testing MCP Coupling Flow...\n")
    
    # 1. Get available agents
    print("1️⃣ Getting agents...")
    agents_resp = requests.post(f"{API_URL}/agents", json={"limit": 10, "offset": 0})
    agents = agents_resp.json()["agents"]
    sre_agent = next((a for a in agents if "SRE" in a.get("display_name", "")), None)
    
    if not sre_agent:
        print("❌ No SRE agent found")
        return
    
    print(f"✅ Found agent: {sre_agent['display_name']} (ID: {sre_agent['id']})")
    
    # 2. Get MCP servers
    print("\n2️⃣ Getting MCP servers...")
    servers_resp = requests.get(f"{API_URL}/api/mcp/servers")
    servers = servers_resp.json()
    servicenow_server = next((s for s in servers if "ServiceNow" in s["name"]), None)
    
    if not servicenow_server:
        print("❌ No ServiceNow server found")
        return
    
    print(f"✅ Found server: {servicenow_server['name']} (ID: {servicenow_server['id']})")
    
    # 3. Create coupling
    print("\n3️⃣ Creating coupling...")
    coupling_data = {
        "agentId": sre_agent["id"],
        "serverId": servicenow_server["id"]
    }
    
    create_resp = requests.post(f"{API_URL}/api/mcp/couplings", json=coupling_data)
    if create_resp.status_code == 200:
        coupling = create_resp.json()
        print(f"✅ Coupling created: {coupling['id']}")
        print(f"   Compatibility: {coupling['compatibility']}")
        print(f"   Active: {coupling['active']}")
    else:
        print(f"❌ Failed to create coupling: {create_resp.text}")
        return
    
    # 4. Test coupling
    print("\n4️⃣ Testing coupling...")
    test_resp = requests.post(f"{API_URL}/api/mcp/couplings/{coupling['id']}/test")
    if test_resp.status_code == 200:
        test_results = test_resp.json()
        print(f"✅ Test completed: {test_results['overall']}")
        for test in test_results['tests']:
            print(f"   - {test['name']}: {test['status']}")
    else:
        print(f"❌ Test failed: {test_resp.text}")
    
    # 5. Activate coupling
    print("\n5️⃣ Activating coupling...")
    activate_resp = requests.put(f"{API_URL}/api/mcp/couplings/{coupling['id']}/activate")
    if activate_resp.status_code == 200:
        result = activate_resp.json()
        print(f"✅ Coupling activated!")
        print(f"   Message: {result['message']}")
    else:
        print(f"❌ Activation failed: {activate_resp.text}")
    
    # 6. Verify status
    print("\n6️⃣ Verifying coupling status...")
    couplings_resp = requests.get(f"{API_URL}/api/mcp/couplings")
    active_coupling = next((c for c in couplings_resp.json() if c['id'] == coupling['id']), None)
    
    if active_coupling:
        print(f"✅ Coupling status: {'Active' if active_coupling['active'] else 'Inactive'}")
    
    print("\n✨ Test completed!")

if __name__ == "__main__":
    test_mcp_flow()
#!/usr/bin/env python3
"""
Activate the SRE-ServiceNow coupling
"""
import requests

API_URL = "http://localhost:8000"
coupling_id = "sre_servicenow_001_ServiceNow-Production"

print("🔌 Activating SRE-ServiceNow Coupling...")

# Since there's no direct activate endpoint, let's test the coupling
# which should activate it
response = requests.post(f"{API_URL}/api/mcp/couplings/{coupling_id}/test")

if response.status_code == 200:
    result = response.json()
    print(f"✅ Coupling test result: {result.get('status', 'Unknown')}")
    print(f"   Message: {result.get('message', 'No message')}")
else:
    print(f"❌ Failed to test coupling: {response.text}")

# Check status again
couplings = requests.get(f"{API_URL}/api/mcp/couplings").json()
for coupling in couplings:
    if coupling['id'] == coupling_id:
        print(f"\n📊 Coupling Status:")
        print(f"   Active: {coupling['active']}")
        print(f"   Compatibility: {coupling['compatibility']}")
        break
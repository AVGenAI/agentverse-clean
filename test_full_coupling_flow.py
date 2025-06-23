#!/usr/bin/env python3
"""Test full coupling flow including activation error"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/mcp"

# Step 1: Get available servers
servers_response = requests.get(f"{BASE_URL}/servers")
print(f"Servers response: {servers_response.status_code}")
servers = servers_response.json()
print(f"Available servers: {[s['name'] for s in servers]}")

# Step 2: Get an agent (using SRE agent ID)
agent_id = "001-sre-infrastructure-automation"

# Step 3: Create a coupling
if servers:
    server_id = servers[0]['id']  # Use first available server
    print(f"\nCreating coupling between agent {agent_id} and server {server_id}")
    
    create_response = requests.post(
        f"{BASE_URL}/couplings",
        json={"agentId": agent_id, "serverId": server_id}
    )
    
    print(f"Create coupling response: {create_response.status_code}")
    
    if create_response.status_code == 200:
        coupling = create_response.json()
        coupling_id = coupling['id']
        print(f"Created coupling with ID: {coupling_id}")
        
        # Step 4: Try to activate the coupling
        print(f"\nTrying to activate coupling...")
        activate_response = requests.put(f"{BASE_URL}/couplings/{coupling_id}/activate")
        
        print(f"Activation response status: {activate_response.status_code}")
        
        if activate_response.status_code != 200:
            print(f"Error response: {activate_response.text}")
            print(f"Error details: {activate_response.headers}")
        else:
            print(f"Success response: {activate_response.json()}")
    else:
        print(f"Failed to create coupling: {create_response.text}")
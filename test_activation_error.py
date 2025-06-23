#!/usr/bin/env python3
"""Test script to reproduce the activation endpoint error"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:8000/api/mcp"

# First, get the active couplings
response = requests.get(f"{BASE_URL}/couplings")
print(f"Active couplings response: {response.status_code}")

if response.status_code == 200:
    couplings = response.json()
    print(f"Found {len(couplings)} couplings")
    
    if couplings:
        # Try to activate the first coupling
        coupling_id = couplings[0]["id"]
        print(f"\nTrying to activate coupling: {coupling_id}")
        
        activate_response = requests.put(f"{BASE_URL}/couplings/{coupling_id}/activate")
        print(f"Activation response status: {activate_response.status_code}")
        
        if activate_response.status_code != 200:
            print(f"Error response: {activate_response.text}")
        else:
            print(f"Success response: {activate_response.json()}")
    else:
        print("No couplings found to test")
else:
    print(f"Failed to get couplings: {response.text}")
#!/usr/bin/env python3
"""Test the API directly to see tool usage"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_agent_details():
    print("Testing SRE Agent Details")
    print("=" * 60)
    
    # Get the SRE agent details
    agent_id = "sre_servicenow_001"
    print(f"\nFetching agent details for: {agent_id}")
    
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    if response.status_code == 200:
        agent_data = response.json()["agent"]
        
        print(f"\nAgent: {agent_data['display_name']}")
        print(f"Instructions preview: {agent_data['instructions'][:150]}...")
        print(f"\nPrimary Expertise:")
        for skill in agent_data['capabilities']['primary_expertise']:
            print(f"  - {skill}")
        
        print(f"\nTools Mastery:")
        tools_mastery = agent_data['capabilities'].get('tools_mastery', {})
        for tool, level in tools_mastery.items():
            print(f"  - {tool}: {level}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    test_agent_details()
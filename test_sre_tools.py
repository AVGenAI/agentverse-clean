#!/usr/bin/env python3
"""Test script to verify SRE agent is using tools properly"""
import requests
import json
import uuid

# API base URL
BASE_URL = "http://localhost:8000"

def test_sre_agent():
    print("Testing SRE Agent Tool Usage")
    print("=" * 60)
    
    # 1. Find the SRE agent
    print("\n1. Finding SRE ServiceNow agent...")
    search_response = requests.get(f"{BASE_URL}/search?q=SRE%20ServiceNow")
    if search_response.status_code != 200:
        print(f"Error searching: {search_response.status_code}")
        return
    
    results = search_response.json()
    if not results["results"]:
        print("No SRE agent found!")
        return
    
    sre_agent = results["results"][0]
    agent_id = sre_agent["id"]
    print(f"Found agent: {sre_agent['display_name']} (ID: {agent_id})")
    
    # 2. Create a chat session
    print("\n2. Creating chat session...")
    session_response = requests.post(
        f"{BASE_URL}/chat/session",
        params={"agent_id": agent_id}
    )
    if session_response.status_code != 200:
        print(f"Error creating session: {session_response.status_code}")
        return
    
    session_data = session_response.json()
    session_id = session_data["session_id"]
    print(f"Session created: {session_id}")
    
    # 3. Test queries that should trigger tool usage
    test_queries = [
        {
            "query": "Show me all critical incidents",
            "expected_tool": "search_incidents"
        },
        {
            "query": "What's the SLO status for the payment service?",
            "expected_tool": "calculate_slo_status"
        },
        {
            "query": "Create an incident for database connection issues",
            "expected_tool": "create_incident"
        },
        {
            "query": "Show me the runbook for high latency",
            "expected_tool": "get_runbook"
        }
    ]
    
    for test in test_queries:
        print(f"\n3. Testing: {test['query']}")
        print("-" * 60)
        
        # Send message
        message_response = requests.post(
            f"{BASE_URL}/chat/message",
            json={
                "agent_id": agent_id,
                "message": test["query"],
                "session_id": session_id
            }
        )
        
        if message_response.status_code != 200:
            print(f"Error sending message: {message_response.status_code}")
            continue
        
        response_data = message_response.json()
        response_text = response_data["response"]
        
        print(f"Response: {response_text[:500]}...")
        
        # Check if the response indicates tool usage
        if "Found" in response_text or "created" in response_text or "Status Report" in response_text or "Runbook" in response_text:
            print(f"✅ Tool appears to have been used!")
        else:
            print(f"⚠️  Tool might not have been used")
    
    print("\n" + "=" * 60)
    print("Test completed!")

if __name__ == "__main__":
    test_sre_agent()
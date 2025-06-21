#!/usr/bin/env python3
"""Comprehensive test of SRE agent with tools"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_sre_with_tools():
    print("Comprehensive SRE Agent Test")
    print("=" * 60)
    
    agent_id = "sre_servicenow_001"
    
    # 1. Create session
    print("\n1. Creating chat session...")
    session_resp = requests.post(f"{BASE_URL}/chat/session?agent_id={agent_id}")
    if session_resp.status_code != 200:
        print(f"Error creating session: {session_resp.text}")
        return
    
    session_id = session_resp.json()["session_id"]
    print(f"Session created: {session_id}")
    
    # 2. Test tool-specific queries
    test_queries = [
        {
            "message": "search_incidents query='state=1 AND priority=1'",
            "description": "Direct tool call format"
        },
        {
            "message": "Use the search_incidents tool to find all critical incidents",
            "description": "Explicit tool request"
        },
        {
            "message": "I need you to search for incidents. Use your search_incidents tool with query state=1",
            "description": "Natural language with tool hint"
        },
        {
            "message": "Calculate the SLO status for the payment service using your calculate_slo_status tool",
            "description": "SLO tool request"
        },
        {
            "message": "Please create a new incident: 'Database connection timeout errors' with priority 1-Critical",
            "description": "Create incident request"
        }
    ]
    
    for i, test in enumerate(test_queries):
        print(f"\n{i+2}. Test: {test['description']}")
        print(f"   Query: {test['message']}")
        print("-" * 60)
        
        # Send message
        msg_resp = requests.post(
            f"{BASE_URL}/chat/message",
            json={
                "agent_id": agent_id,
                "message": test["message"],
                "session_id": session_id
            }
        )
        
        if msg_resp.status_code == 200:
            response = msg_resp.json()["response"]
            print(f"   Response preview: {response[:300]}...")
            
            # Check for tool indicators
            tool_indicators = [
                "Found", "incidents", "INC", "created", "Status Report",
                "Target:", "Current:", "Runbook", "Steps"
            ]
            
            tools_used = [ind for ind in tool_indicators if ind in response]
            if tools_used:
                print(f"   ✅ Likely used tools (found: {', '.join(tools_used)})")
            else:
                print(f"   ⚠️  No clear tool usage indicators")
        else:
            print(f"   Error: {msg_resp.status_code} - {msg_resp.text}")
        
        time.sleep(1)  # Rate limiting
    
    print("\n" + "=" * 60)
    print("Test completed!")
    
    # Check server health
    print("\n3. Checking server health...")
    health_resp = requests.get(f"{BASE_URL}/health")
    if health_resp.status_code == 200:
        health = health_resp.json()
        print(f"   Active agents: {health['active_agents']}")
        print(f"   OpenAI available: {health['llm_providers']['openai']['available']}")

if __name__ == "__main__":
    test_sre_with_tools()
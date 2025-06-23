#!/usr/bin/env python3
"""Test SRE agent tool usage"""
import asyncio
import sys
sys.path.append('./agentverse_api')

from agent_manager import agent_manager

async def test_tool_usage():
    # First check agent creation
    print("🔍 Testing SRE Agent Tool Usage...\n")
    
    # Test queries that should trigger tool usage
    test_queries = [
        "Show me all critical incidents",
        "What's the current SLO status for the payment service?",
        "Create a new incident for database connection issues",
        "Get the runbook for high latency"
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        response = await agent_manager.chat_with_agent("sre_servicenow_001", query)
        print(f"🤖 Agent: {response[:500]}...")  # Show first 500 chars
        print("-" * 80)
        print()

if __name__ == "__main__":
    asyncio.run(test_tool_usage())
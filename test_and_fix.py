#!/usr/bin/env python3
"""
Test specific issues and apply fixes
"""

import asyncio
import httpx
import json
import os
import sys

API_BASE_URL = "http://localhost:8000"

async def test_cors_properly():
    """Test CORS with proper headers"""
    print("Testing CORS configuration...")
    
    async with httpx.AsyncClient() as client:
        # Test preflight request
        response = await client.options(
            f"{API_BASE_URL}/agents",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type"
            }
        )
        
        print(f"Status: {response.status_code}")
        print("Headers:")
        for key, value in response.headers.items():
            if 'access-control' in key.lower():
                print(f"  {key}: {value}")
        
        # Check if CORS headers are present
        has_cors = any('access-control' in h.lower() for h in response.headers.keys())
        
        if not has_cors:
            print("\n❌ CORS headers missing! Let me check the middleware...")
            return False
        
        print("\n✅ CORS is properly configured!")
        return True

async def test_agent_data_loading():
    """Check if agent data is properly loaded"""
    print("\nTesting agent data loading...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        data = response.json()
        
        agents_loaded = data.get("agents_loaded", 0)
        print(f"Agents loaded: {agents_loaded}")
        
        if agents_loaded == 0:
            print("❌ No agents loaded! Checking file path...")
            
            # Check if the JSON file exists
            json_path = "src/config/agentverse_agents_1000.json"
            if os.path.exists(json_path):
                print(f"✅ JSON file exists at {json_path}")
                print("   The API might be looking in the wrong location")
                return False
            else:
                print(f"❌ JSON file not found at {json_path}")
                return False
        
        print("✅ Agents loaded successfully!")
        return True

async def test_ollama_connection():
    """Test Ollama provider status"""
    print("\nTesting Ollama connection...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/health")
        data = response.json()
        
        ollama_status = data.get("llm_providers", {}).get("ollama", {})
        openai_status = data.get("llm_providers", {}).get("openai", {})
        
        print(f"Ollama available: {ollama_status.get('available', False)}")
        print(f"Ollama enabled: {ollama_status.get('enabled', True)}")
        print(f"Ollama model: {ollama_status.get('model', 'Not set')}")
        
        print(f"\nOpenAI available: {openai_status.get('available', False)}")
        
        if not ollama_status.get('available') and not openai_status.get('available'):
            print("\n⚠️  No LLM providers available!")
            print("To enable AI responses:")
            print("1. Install and start Ollama: ollama serve")
            print("2. Or add OPENAI_API_KEY to .env file")
        
        return True

async def test_chat_with_mock():
    """Test chat functionality even without LLM"""
    print("\nTesting chat with mock responses...")
    
    async with httpx.AsyncClient() as client:
        # Get an agent
        agents_response = await client.post(
            f"{API_BASE_URL}/agents",
            json={"limit": 1}
        )
        agents_data = agents_response.json()
        
        if not agents_data.get("agents"):
            print("❌ No agents available for testing")
            return False
        
        agent_id = agents_data["agents"][0]["id"]
        
        # Create session
        session_response = await client.post(
            f"{API_BASE_URL}/chat/session?agent_id={agent_id}"
        )
        session_data = session_response.json()
        session_id = session_data.get("session_id")
        
        # Send message
        message_response = await client.post(
            f"{API_BASE_URL}/chat/message",
            json={
                "agent_id": agent_id,
                "message": "Hello, can you help me?",
                "session_id": session_id
            }
        )
        
        if message_response.status_code == 200:
            response_data = message_response.json()
            print(f"✅ Chat working! Response preview: {response_data['response'][:100]}...")
            return True
        else:
            print(f"❌ Chat failed with status: {message_response.status_code}")
            return False

async def check_file_paths():
    """Check and fix file path issues"""
    print("\nChecking file paths...")
    
    # Check current directory
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    # Check if we're in the right directory
    if "agentverse_api" in cwd:
        print("⚠️  Running from API directory")
        json_path = "../src/config/agentverse_agents_1000.json"
    else:
        json_path = "src/config/agentverse_agents_1000.json"
    
    if os.path.exists(json_path):
        print(f"✅ Agent config found at: {json_path}")
        
        # Check if it's valid JSON
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                print(f"✅ Valid JSON with {len(data)} agents")
        except Exception as e:
            print(f"❌ Invalid JSON: {e}")
            return False
    else:
        print(f"❌ Agent config not found at: {json_path}")
        return False
    
    return True

async def main():
    print("🔧 AgentVerse Diagnostic Tool\n")
    
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{API_BASE_URL}/health", timeout=2.0)
    except:
        print("❌ API is not running!")
        print("\nTo start the API:")
        print("1. cd agentverse_api")
        print("2. uvicorn main:app --reload")
        return
    
    # Run diagnostic tests
    tests = [
        check_file_paths,
        test_agent_data_loading,
        test_cors_properly,
        test_ollama_connection,
        test_chat_with_mock
    ]
    
    for test in tests:
        await test()
        print("-" * 50)
    
    print("\n✅ Diagnostic complete!")
    
    # Provide recommendations
    print("\n📋 Recommendations:")
    print("1. Ensure you're running from the project root directory")
    print("2. Start Ollama for local AI: ollama serve")
    print("3. Or add OPENAI_API_KEY to agentverse_api/.env")
    print("4. Use ./start_agentverse.sh for automated startup")

if __name__ == "__main__":
    asyncio.run(main())
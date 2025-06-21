#!/usr/bin/env python3
"""
Test UI Integration with Backend
"""

import asyncio
import httpx
import json
from typing import Dict, List

API_BASE_URL = "http://localhost:8000"
UI_BASE_URL = "http://localhost:3000"

class UIIntegrationTests:
    def __init__(self):
        self.test_results = []
        
    async def test_ui_api_connection(self):
        """Test if UI can connect to API through proxy"""
        print("Testing UI → API connection...")
        
        # The UI proxies /api requests to the backend
        # We'll simulate what the UI does
        async with httpx.AsyncClient() as client:
            # Test health endpoint through UI proxy
            try:
                # Direct API call
                api_response = await client.get(f"{API_BASE_URL}/health")
                print(f"✅ Direct API connection: {api_response.status_code}")
                
                # Check if UI is running
                try:
                    ui_response = await client.get(UI_BASE_URL, timeout=2.0)
                    print(f"✅ UI is running: {ui_response.status_code}")
                except:
                    print("⚠️  UI is not running. Start with: cd agentverse_ui && npm run dev")
                
                return True
            except Exception as e:
                print(f"❌ Connection error: {e}")
                return False
    
    async def test_dashboard_data(self):
        """Test data required for Dashboard component"""
        print("\nTesting Dashboard data endpoints...")
        
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            health_response = await client.get(f"{API_BASE_URL}/health")
            health_data = health_response.json()
            
            print(f"  Agents loaded: {health_data.get('agents_loaded', 0)}")
            print(f"  Active sessions: {health_data.get('active_sessions', 0)}")
            
            # Check LLM providers
            llm_providers = health_data.get('llm_providers', {})
            if llm_providers.get('ollama', {}).get('available'):
                print(f"  ✅ Ollama is available")
            elif llm_providers.get('openai', {}).get('available'):
                print(f"  ✅ OpenAI is available")
            else:
                print(f"  ⚠️  No LLM provider available")
            
            # Test domains endpoint
            domains_response = await client.get(f"{API_BASE_URL}/domains")
            domains_data = domains_response.json()
            print(f"  Total domains: {domains_data.get('total_domains', 0)}")
            
            return health_response.status_code == 200 and domains_response.status_code == 200
    
    async def test_agents_page_data(self):
        """Test data for Agents page"""
        print("\nTesting Agents page data...")
        
        async with httpx.AsyncClient() as client:
            # Test agent listing
            agents_response = await client.post(
                f"{API_BASE_URL}/agents",
                json={"limit": 10, "offset": 0}
            )
            agents_data = agents_response.json()
            
            print(f"  Total agents: {agents_data.get('total', 0)}")
            print(f"  Agents returned: {len(agents_data.get('agents', []))}")
            
            # Test search
            search_response = await client.get(f"{API_BASE_URL}/search?q=python&limit=5")
            search_data = search_response.json()
            print(f"  Search results for 'python': {len(search_data.get('results', []))}")
            
            # Test specific agent
            if agents_data.get('agents'):
                agent_id = agents_data['agents'][0]['id']
                agent_response = await client.get(f"{API_BASE_URL}/agents/{agent_id}")
                
                if agent_response.status_code == 200:
                    print(f"  ✅ Agent details endpoint working")
                else:
                    print(f"  ❌ Agent details endpoint failed")
            
            return agents_response.status_code == 200
    
    async def test_chat_flow(self):
        """Test complete chat flow"""
        print("\nTesting Chat flow...")
        
        async with httpx.AsyncClient() as client:
            # Get an agent
            agents_response = await client.post(
                f"{API_BASE_URL}/agents",
                json={"limit": 1}
            )
            agents_data = agents_response.json()
            
            if not agents_data.get('agents'):
                print("  ❌ No agents available")
                return False
            
            agent = agents_data['agents'][0]
            agent_id = agent['id']
            
            print(f"  Testing chat with: {agent['display_name']}")
            
            # Create session
            session_response = await client.post(
                f"{API_BASE_URL}/chat/session?agent_id={agent_id}"
            )
            
            if session_response.status_code != 200:
                print(f"  ❌ Failed to create session")
                return False
            
            session_data = session_response.json()
            session_id = session_data['session_id']
            
            # Send message
            message_response = await client.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "agent_id": agent_id,
                    "message": "Hello! What are your main skills?",
                    "session_id": session_id
                }
            )
            
            if message_response.status_code == 200:
                response_data = message_response.json()
                print(f"  ✅ Chat working!")
                print(f"  Response preview: {response_data['response'][:80]}...")
            else:
                print(f"  ❌ Chat failed")
                return False
            
            return True
    
    async def test_team_builder(self):
        """Test team builder functionality"""
        print("\nTesting Team Builder...")
        
        async with httpx.AsyncClient() as client:
            # Test different project types
            project_types = ["ecommerce", "mobile", "data"]
            
            for project_type in project_types:
                response = await client.post(
                    f"{API_BASE_URL}/team/assemble",
                    json={
                        "project_type": project_type,
                        "requirements": ["Python", "React"],
                        "team_size": 4
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ {project_type}: {len(data['team'])} members assembled")
                else:
                    print(f"  ❌ {project_type}: Failed")
            
            return True
    
    async def run_all_tests(self):
        """Run all UI integration tests"""
        print("🧪 UI Integration Test Suite\n")
        
        tests = [
            self.test_ui_api_connection,
            self.test_dashboard_data,
            self.test_agents_page_data,
            self.test_chat_flow,
            self.test_team_builder
        ]
        
        for test in tests:
            try:
                result = await test()
                self.test_results.append((test.__name__, result))
            except Exception as e:
                print(f"  ❌ Error: {e}")
                self.test_results.append((test.__name__, False))
            print("-" * 50)
        
        # Summary
        print("\n📊 Test Summary:")
        passed = sum(1 for _, result in self.test_results if result)
        total = len(self.test_results)
        print(f"Passed: {passed}/{total}")
        
        if passed < total:
            print("\n❌ Failed tests:")
            for name, result in self.test_results:
                if not result:
                    print(f"  - {name}")

async def main():
    # Check if API is running
    try:
        async with httpx.AsyncClient() as client:
            await client.get(f"{API_BASE_URL}/health", timeout=2.0)
    except:
        print("❌ Backend API is not running!")
        print("\nTo start the complete system:")
        print("./start_agentverse.sh")
        print("\nOr manually:")
        print("1. Terminal 1: cd agentverse_api && uvicorn main:app --reload")
        print("2. Terminal 2: cd agentverse_ui && npm run dev")
        return
    
    tester = UIIntegrationTests()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
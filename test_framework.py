#!/usr/bin/env python3
"""
Comprehensive Test Suite for AgentVerse Framework
Tests all major components and identifies bugs
"""

import asyncio
import json
import sys
import traceback
from typing import Dict, List, Tuple
import httpx
import time

# Test configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 10.0

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class AgentVerseTestSuite:
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.test_agent_id = None
        self.test_session_id = None
        
    async def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"{Colors.BLUE}=== AgentVerse Comprehensive Test Suite ==={Colors.END}\n")
        
        # Check if API is running
        if not await self.check_api_health():
            print(f"{Colors.RED}❌ API is not running! Please start the backend first.{Colors.END}")
            print(f"Run: cd agentverse_api && uvicorn main:app --reload")
            return
        
        # Test groups
        test_groups = [
            ("Basic API Tests", [
                self.test_root_endpoint,
                self.test_health_endpoint,
                self.test_cors_headers,
            ]),
            ("Domain Tests", [
                self.test_get_domains,
                self.test_domain_structure,
            ]),
            ("Agent Tests", [
                self.test_get_agents,
                self.test_agent_filtering,
                self.test_agent_search,
                self.test_get_specific_agent,
                self.test_agent_not_found,
            ]),
            ("Team Assembly Tests", [
                self.test_team_assembly,
                self.test_team_with_requirements,
                self.test_invalid_project_type,
            ]),
            ("Chat Tests", [
                self.test_create_chat_session,
                self.test_send_message,
                self.test_invalid_session,
            ]),
            ("Data Validation Tests", [
                self.test_agent_data_integrity,
                self.test_pagination,
                self.test_empty_search,
            ]),
            ("Error Handling Tests", [
                self.test_malformed_requests,
                self.test_missing_parameters,
            ])
        ]
        
        total_tests = sum(len(tests) for _, tests in test_groups)
        current_test = 0
        
        for group_name, tests in test_groups:
            print(f"\n{Colors.YELLOW}📋 {group_name}{Colors.END}")
            for test_func in tests:
                current_test += 1
                await self.run_test(test_func, current_test, total_tests)
        
        # Print summary
        self.print_summary()
    
    async def run_test(self, test_func, current: int, total: int):
        """Run a single test and record results"""
        test_name = test_func.__name__.replace('test_', '').replace('_', ' ').title()
        print(f"[{current}/{total}] Testing {test_name}...", end=" ")
        
        try:
            result = await test_func()
            if result:
                print(f"{Colors.GREEN}✅ PASSED{Colors.END}")
                self.results.append((test_name, True, ""))
            else:
                print(f"{Colors.RED}❌ FAILED{Colors.END}")
                self.results.append((test_name, False, "Test returned False"))
        except Exception as e:
            print(f"{Colors.RED}❌ ERROR{Colors.END}")
            error_msg = f"{type(e).__name__}: {str(e)}"
            self.results.append((test_name, False, error_msg))
            if "--verbose" in sys.argv:
                traceback.print_exc()
    
    async def check_api_health(self) -> bool:
        """Check if API is accessible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{API_BASE_URL}/health", timeout=2.0)
                return response.status_code == 200
        except:
            return False
    
    # === Basic API Tests ===
    
    async def test_root_endpoint(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/")
            data = response.json()
            return (
                response.status_code == 200 and
                "message" in data and
                "endpoints" in data
            )
    
    async def test_health_endpoint(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health")
            data = response.json()
            return (
                response.status_code == 200 and
                "status" in data and
                data["status"] == "healthy" and
                "agents_loaded" in data and
                "llm_providers" in data
            )
    
    async def test_cors_headers(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{API_BASE_URL}/agents",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "POST"
                }
            )
            return (
                response.status_code == 200 and
                "access-control-allow-origin" in response.headers
            )
    
    # === Domain Tests ===
    
    async def test_get_domains(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/domains")
            data = response.json()
            return (
                response.status_code == 200 and
                "domains" in data and
                "total_domains" in data and
                isinstance(data["domains"], dict)
            )
    
    async def test_domain_structure(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/domains")
            data = response.json()
            
            if not data.get("domains"):
                return False
            
            # Check structure of first domain
            first_domain = list(data["domains"].values())[0]
            return all(key in first_domain for key in ["name", "agent_count", "subdomains"])
    
    # === Agent Tests ===
    
    async def test_get_agents(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/agents",
                json={"limit": 10, "offset": 0}
            )
            data = response.json()
            
            if response.status_code == 200 and data.get("agents"):
                # Store an agent ID for later tests
                self.test_agent_id = data["agents"][0]["id"]
                
            return (
                response.status_code == 200 and
                "agents" in data and
                "total" in data and
                isinstance(data["agents"], list)
            )
    
    async def test_agent_filtering(self) -> bool:
        async with httpx.AsyncClient() as client:
            # Test domain filtering
            response = await client.post(
                f"{API_BASE_URL}/agents",
                json={"domain": "engineering", "limit": 5}
            )
            data = response.json()
            
            if response.status_code != 200:
                return False
            
            # All returned agents should have engineering in their canonical name
            for agent in data.get("agents", []):
                if "engineering" not in agent.get("canonical_name", "").lower():
                    return False
            
            return True
    
    async def test_agent_search(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/search?q=python&limit=5")
            data = response.json()
            
            return (
                response.status_code == 200 and
                "results" in data and
                "query" in data and
                data["query"] == "python"
            )
    
    async def test_get_specific_agent(self) -> bool:
        if not self.test_agent_id:
            return False
            
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/agents/{self.test_agent_id}")
            data = response.json()
            
            return (
                response.status_code == 200 and
                "agent" in data and
                data["agent"]["id"] == self.test_agent_id
            )
    
    async def test_agent_not_found(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/agents/nonexistent123")
            return response.status_code == 404
    
    # === Team Assembly Tests ===
    
    async def test_team_assembly(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/team/assemble",
                json={
                    "project_type": "ecommerce",
                    "requirements": [],
                    "team_size": 5
                }
            )
            data = response.json()
            
            return (
                response.status_code == 200 and
                "team" in data and
                isinstance(data["team"], list) and
                len(data["team"]) <= 5
            )
    
    async def test_team_with_requirements(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/team/assemble",
                json={
                    "project_type": "mobile",
                    "requirements": ["React Native", "Firebase"],
                    "team_size": 4
                }
            )
            data = response.json()
            
            return (
                response.status_code == 200 and
                "team" in data and
                data["project_type"] == "mobile"
            )
    
    async def test_invalid_project_type(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/team/assemble",
                json={
                    "project_type": "invalid_type",
                    "requirements": [],
                    "team_size": 3
                }
            )
            # Should still work with default mapping
            return response.status_code == 200
    
    # === Chat Tests ===
    
    async def test_create_chat_session(self) -> bool:
        if not self.test_agent_id:
            return False
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/session?agent_id={self.test_agent_id}"
            )
            data = response.json()
            
            if response.status_code == 200 and "session_id" in data:
                self.test_session_id = data["session_id"]
                
            return (
                response.status_code == 200 and
                "session_id" in data and
                "status" in data
            )
    
    async def test_send_message(self) -> bool:
        if not self.test_session_id or not self.test_agent_id:
            return False
            
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "agent_id": self.test_agent_id,
                    "message": "Hello, test message",
                    "session_id": self.test_session_id
                }
            )
            data = response.json()
            
            return (
                response.status_code == 200 and
                "response" in data and
                isinstance(data["response"], str)
            )
    
    async def test_invalid_session(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "agent_id": "test",
                    "message": "Hello",
                    "session_id": "invalid_session_123"
                }
            )
            return response.status_code == 404
    
    # === Data Validation Tests ===
    
    async def test_agent_data_integrity(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/agents",
                json={"limit": 20}
            )
            data = response.json()
            
            if not data.get("agents"):
                return False
            
            # Check each agent has required fields
            required_fields = ["id", "canonical_name", "display_name", "skills"]
            for agent in data["agents"]:
                if not all(field in agent for field in required_fields):
                    return False
            
            return True
    
    async def test_pagination(self) -> bool:
        async with httpx.AsyncClient() as client:
            # Get first page
            response1 = await client.post(
                f"{API_BASE_URL}/agents",
                json={"limit": 10, "offset": 0}
            )
            data1 = response1.json()
            
            # Get second page
            response2 = await client.post(
                f"{API_BASE_URL}/agents",
                json={"limit": 10, "offset": 10}
            )
            data2 = response2.json()
            
            # Ensure different agents
            if data1.get("agents") and data2.get("agents"):
                ids1 = {a["id"] for a in data1["agents"]}
                ids2 = {a["id"] for a in data2["agents"]}
                return len(ids1.intersection(ids2)) == 0
            
            return False
    
    async def test_empty_search(self) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/search?q=xyznonexistent123")
            data = response.json()
            
            return (
                response.status_code == 200 and
                "results" in data and
                isinstance(data["results"], list)
            )
    
    # === Error Handling Tests ===
    
    async def test_malformed_requests(self) -> bool:
        async with httpx.AsyncClient() as client:
            # Missing required field
            response = await client.post(
                f"{API_BASE_URL}/team/assemble",
                json={"requirements": []}  # Missing project_type
            )
            return response.status_code == 422
    
    async def test_missing_parameters(self) -> bool:
        async with httpx.AsyncClient() as client:
            # Search without query
            response = await client.get(f"{API_BASE_URL}/search")
            return response.status_code == 422
    
    def print_summary(self):
        """Print test results summary"""
        print(f"\n{Colors.BLUE}=== Test Summary ==={Colors.END}")
        
        passed = sum(1 for _, success, _ in self.results if success)
        failed = len(self.results) - passed
        
        print(f"Total Tests: {len(self.results)}")
        print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed}{Colors.END}")
        
        if failed > 0:
            print(f"\n{Colors.RED}Failed Tests:{Colors.END}")
            for name, success, error in self.results:
                if not success:
                    print(f"  ❌ {name}: {error}")
        
        print(f"\n{Colors.YELLOW}Recommendations:{Colors.END}")
        
        # Check specific issues
        health_test = next((r for r in self.results if r[0] == "Health Endpoint"), None)
        if health_test and health_test[1]:
            print("  ✅ API is healthy")
        else:
            print("  ⚠️  Check API health endpoint")
        
        agent_test = next((r for r in self.results if r[0] == "Get Agents"), None)
        if agent_test and not agent_test[1]:
            print("  ⚠️  Agent data may not be loaded properly")
            print("     Check if agentverse_agents_1000.json exists")
        
        chat_test = next((r for r in self.results if r[0] == "Send Message"), None)
        if chat_test and chat_test[1]:
            print("  ✅ Chat system is working")
        else:
            print("  ⚠️  Chat system may have issues")

async def main():
    print(f"{Colors.YELLOW}Starting AgentVerse Framework Tests...{Colors.END}\n")
    
    # Check if API is running
    test_suite = AgentVerseTestSuite()
    
    if not await test_suite.check_api_health():
        print(f"{Colors.RED}⚠️  API is not running!{Colors.END}")
        print("\nTo start the API:")
        print("1. cd agentverse_api")
        print("2. python -m venv venv")
        print("3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("4. pip install -r requirements.txt")
        print("5. uvicorn main:app --reload")
        return
    
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
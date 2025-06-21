#!/usr/bin/env python3
"""
AgentVerse Integration Test Script
Tests the connection between frontend and backend components
"""

import requests
import json
import time
import sys
from typing import Dict, Any

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health() -> bool:
    """Test if backend is running and healthy"""
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy: {data}")
            return True
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
    return False

def test_agent_endpoints() -> bool:
    """Test agent-related endpoints"""
    try:
        # Test getting domains
        response = requests.get(f"{BACKEND_URL}/domains")
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Found {len(domains['domains'])} agent domains")
        
        # Test agent search
        search_payload = {
            "domain": "engineering",
            "limit": 5
        }
        response = requests.post(f"{BACKEND_URL}/agents", json=search_payload)
        if response.status_code == 200:
            agents = response.json()
            print(f"✅ Found {len(agents['agents'])} engineering agents")
            
            # Test getting specific agent
            if agents['agents']:
                agent_id = agents['agents'][0]['id']
                response = requests.get(f"{BACKEND_URL}/agents/{agent_id}")
                if response.status_code == 200:
                    print(f"✅ Successfully retrieved agent: {agent_id}")
        
        return True
    except Exception as e:
        print(f"❌ Agent endpoint test failed: {e}")
        return False

def test_team_assembly() -> bool:
    """Test team assembly endpoint"""
    try:
        team_request = {
            "project_type": "ecommerce",
            "requirements": ["React", "Node.js", "PostgreSQL"],
            "team_size": 5
        }
        response = requests.post(f"{BACKEND_URL}/team/assemble", json=team_request)
        if response.status_code == 200:
            team = response.json()
            print(f"✅ Successfully assembled team with {len(team['team'])} members")
            return True
    except Exception as e:
        print(f"❌ Team assembly test failed: {e}")
    return False

def test_frontend_accessibility() -> bool:
    """Test if frontend is accessible"""
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print(f"✅ Frontend is accessible at {FRONTEND_URL}")
            return True
    except Exception as e:
        print(f"❌ Frontend accessibility test failed: {e}")
    return False

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running AgentVerse Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Agent Endpoints", test_agent_endpoints),
        ("Team Assembly", test_team_assembly),
        ("Frontend Accessibility", test_frontend_accessibility)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing: {test_name}")
        success = test_func()
        results.append((test_name, success))
        time.sleep(1)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! AgentVerse is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the services.")
        return 1

if __name__ == "__main__":
    # Wait a bit for services to start if script is run immediately after startup
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        print("⏳ Waiting 10 seconds for services to start...")
        time.sleep(10)
    
    exit_code = run_integration_tests()
    sys.exit(exit_code)
#!/usr/bin/env python3
"""
Quick Agent Quality Test - Test a few agents quickly
"""

import asyncio
import httpx
import json
import time

API_BASE_URL = "http://localhost:8000"

async def test_single_agent():
    """Test a single agent's response quality"""
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get a Django agent
        agents_resp = await client.post(
            f"{API_BASE_URL}/agents",
            json={"domain": "engineering", "limit": 1}
        )
        
        if agents_resp.status_code != 200:
            print("❌ Failed to get agents")
            return
        
        agent = agents_resp.json()['agents'][0]
        print(f"Testing Agent: {agent['display_name']}")
        print(f"Skills: {', '.join(agent['skills'][:3])}")
        print(f"Canonical Name: {agent['canonical_name']}")
        print("-" * 60)
        
        # Create chat session
        session_resp = await client.post(
            f"{API_BASE_URL}/chat/session?agent_id={agent['id']}"
        )
        session_id = session_resp.json()['session_id']
        
        # Test queries
        test_queries = [
            "What are your main areas of expertise?",
            "Can you help me design a REST API for a blog?",
            "What's the best way to handle authentication in Django?"
        ]
        
        for query in test_queries:
            print(f"\n🤔 User: {query}")
            
            start_time = time.time()
            response = await client.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "agent_id": agent['id'],
                    "message": query,
                    "session_id": session_id
                }
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                ai_response = response.json()['response']
                print(f"🤖 Agent ({response_time:.2f}s):")
                print(f"   {ai_response[:200]}...")
                
                # Quick quality check
                is_personalized = agent['display_name'] in ai_response or any(skill.lower() in ai_response.lower() for skill in agent['skills'])
                is_detailed = len(ai_response) > 100
                has_no_errors = "error" not in ai_response.lower() and "mock response" not in ai_response.lower()
                
                print(f"\n   ✓ Personalized: {'✅' if is_personalized else '❌'}")
                print(f"   ✓ Detailed: {'✅' if is_detailed else '❌'}")
                print(f"   ✓ Real AI: {'✅' if has_no_errors else '❌'}")

async def test_different_domains():
    """Test agents from different domains"""
    print("\n" + "="*60)
    print("Testing Agents from Different Domains")
    print("="*60)
    
    domains = ["engineering", "business_workflow", "data_analytics"]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for domain in domains:
            print(f"\n📂 Domain: {domain}")
            
            # Get an agent from this domain
            agents_resp = await client.post(
                f"{API_BASE_URL}/agents",
                json={"domain": domain, "limit": 1}
            )
            
            if agents_resp.status_code != 200:
                continue
                
            agent = agents_resp.json()['agents'][0]
            print(f"   Agent: {agent['display_name']}")
            
            # Create session
            session_resp = await client.post(
                f"{API_BASE_URL}/chat/session?agent_id={agent['id']}"
            )
            session_id = session_resp.json()['session_id']
            
            # Domain-specific question
            domain_questions = {
                "engineering": "What's your approach to microservices architecture?",
                "business_workflow": "How do you optimize business processes?",
                "data_analytics": "What's your experience with ETL pipelines?"
            }
            
            question = domain_questions.get(domain, "What can you help with?")
            
            response = await client.post(
                f"{API_BASE_URL}/chat/message",
                json={
                    "agent_id": agent['id'],
                    "message": question,
                    "session_id": session_id
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()['response']
                print(f"   Q: {question}")
                print(f"   A: {ai_response[:150]}...")

async def check_llm_status():
    """Check which LLM is being used"""
    async with httpx.AsyncClient() as client:
        health = await client.get(f"{API_BASE_URL}/health")
        data = health.json()
        
        print("\n🔧 LLM Provider Status:")
        
        ollama = data.get('llm_providers', {}).get('ollama', {})
        openai = data.get('llm_providers', {}).get('openai', {})
        
        if ollama.get('available'):
            print(f"   🦙 Ollama: ✅ Active (Model: {ollama.get('model')})")
        else:
            print(f"   🦙 Ollama: ❌ Not Available")
            
        if openai.get('available'):
            print(f"   🤖 OpenAI: ✅ Active (Model: {openai.get('model')})")
        else:
            print(f"   🤖 OpenAI: ❌ Not Available")

async def main():
    print("🧪 Quick Agent Quality Test\n")
    
    # Check LLM status first
    await check_llm_status()
    
    # Test single agent in detail
    await test_single_agent()
    
    # Test different domains
    await test_different_domains()
    
    print("\n✅ Test Complete!")

if __name__ == "__main__":
    asyncio.run(main())
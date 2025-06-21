#!/usr/bin/env python3
"""
Test Agent Quality - Evaluate AI responses, personas, and capabilities
"""

import asyncio
import httpx
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

class AgentQualityTester:
    def __init__(self):
        self.results: Dict[str, List[Dict]] = {
            "response_quality": [],
            "persona_consistency": [],
            "tool_usage": [],
            "domain_expertise": [],
            "collaboration": []
        }
        self.test_agents: List[Dict] = []
        
    async def setup(self):
        """Get a diverse set of agents for testing"""
        print(f"{Colors.BLUE}Setting up test agents...{Colors.END}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Get agents from different domains
            domains = ["engineering", "business_workflow", "data_analytics", "security", "sre_devops"]
            
            for domain in domains:
                response = await client.post(
                    f"{API_BASE_URL}/agents",
                    json={"domain": domain, "limit": 2}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.test_agents.extend(data.get("agents", [])[:2])
            
            print(f"Selected {len(self.test_agents)} agents for quality testing\n")
    
    async def test_response_quality(self):
        """Test quality of agent responses"""
        print(f"{Colors.YELLOW}📝 Testing Response Quality{Colors.END}")
        
        test_queries = [
            {
                "query": "Can you explain your primary expertise?",
                "checks": ["expertise", "skills", "experience"]
            },
            {
                "query": "What's the best practice for error handling in production?",
                "checks": ["specific", "practical", "technical"]
            },
            {
                "query": "How would you approach debugging a performance issue?",
                "checks": ["systematic", "tools", "methodology"]
            }
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for agent in self.test_agents[:5]:  # Test first 5 agents
                print(f"\nTesting {agent['display_name']} ({agent['canonical_name']})")
                
                # Create session
                session_resp = await client.post(
                    f"{API_BASE_URL}/chat/session?agent_id={agent['id']}"
                )
                if session_resp.status_code != 200:
                    continue
                    
                session_id = session_resp.json()['session_id']
                
                for test in test_queries:
                    # Send query
                    start_time = time.time()
                    response = await client.post(
                        f"{API_BASE_URL}/chat/message",
                        json={
                            "agent_id": agent['id'],
                            "message": test['query'],
                            "session_id": session_id
                        }
                    )
                    response_time = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        ai_response = data['response']
                        
                        # Evaluate response
                        quality_score = self._evaluate_response_quality(
                            ai_response, 
                            test['checks'],
                            agent
                        )
                        
                        self.results["response_quality"].append({
                            "agent": agent['display_name'],
                            "query": test['query'],
                            "response_preview": ai_response[:100] + "...",
                            "response_time": response_time,
                            "quality_score": quality_score,
                            "response_length": len(ai_response)
                        })
                        
                        print(f"  Query: {test['query'][:50]}...")
                        print(f"  Response time: {response_time:.2f}s")
                        print(f"  Quality score: {quality_score}/10")
                        print(f"  Response length: {len(ai_response)} chars")
    
    def _evaluate_response_quality(self, response: str, checks: List[str], agent: Dict) -> int:
        """Score response quality out of 10"""
        score = 5  # Base score
        
        # Check if response is contextual
        if any(skill.lower() in response.lower() for skill in agent.get('skills', [])):
            score += 2
        
        # Check for specific keywords from checks
        for check in checks:
            if check.lower() in response.lower():
                score += 1
        
        # Length check (not too short, not too long)
        if 100 < len(response) < 1000:
            score += 1
        
        # Check if it's not a mock response
        if "mock response" not in response.lower() and "demo response" not in response.lower():
            score += 1
        
        return min(score, 10)
    
    async def test_persona_consistency(self):
        """Test if agents maintain consistent personas"""
        print(f"\n{Colors.YELLOW}🎭 Testing Persona Consistency{Colors.END}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for agent in self.test_agents[:3]:  # Test 3 agents
                print(f"\nTesting persona: {agent['display_name']}")
                
                # Create session
                session_resp = await client.post(
                    f"{API_BASE_URL}/chat/session?agent_id={agent['id']}"
                )
                if session_resp.status_code != 200:
                    continue
                    
                session_id = session_resp.json()['session_id']
                
                # Ask about identity
                identity_queries = [
                    "Who are you and what do you do?",
                    "What are your main skills?",
                    "What kind of problems do you solve?"
                ]
                
                responses = []
                for query in identity_queries:
                    response = await client.post(
                        f"{API_BASE_URL}/chat/message",
                        json={
                            "agent_id": agent['id'],
                            "message": query,
                            "session_id": session_id
                        }
                    )
                    
                    if response.status_code == 200:
                        responses.append(response.json()['response'])
                
                # Check consistency
                consistency_score = self._evaluate_persona_consistency(responses, agent)
                
                self.results["persona_consistency"].append({
                    "agent": agent['display_name'],
                    "consistency_score": consistency_score,
                    "responses_count": len(responses)
                })
                
                print(f"  Consistency score: {consistency_score}/10")
    
    def _evaluate_persona_consistency(self, responses: List[str], agent: Dict) -> int:
        """Evaluate if agent maintains consistent persona"""
        score = 10
        
        # Check if agent mentions its name consistently
        name_mentions = sum(1 for r in responses if agent['display_name'] in r)
        if name_mentions == 0:
            score -= 2
        
        # Check if skills are mentioned consistently
        skills_mentioned = []
        for response in responses:
            for skill in agent.get('skills', []):
                if skill.lower() in response.lower():
                    skills_mentioned.append(skill)
        
        if len(set(skills_mentioned)) < 2:
            score -= 2
        
        # Check for contradictions (simplified)
        # Real implementation would use NLP
        
        return max(score, 0)
    
    async def test_domain_expertise(self):
        """Test domain-specific knowledge"""
        print(f"\n{Colors.YELLOW}🎯 Testing Domain Expertise{Colors.END}")
        
        domain_tests = {
            "engineering": {
                "query": "What's the difference between REST and GraphQL?",
                "expected": ["REST", "GraphQL", "API", "endpoints", "query"]
            },
            "business_workflow": {
                "query": "How do you optimize a business process?",
                "expected": ["process", "efficiency", "workflow", "automation", "metrics"]
            },
            "data_analytics": {
                "query": "Explain ETL vs ELT pipelines",
                "expected": ["ETL", "ELT", "extract", "transform", "load", "data"]
            },
            "security": {
                "query": "What are the OWASP top 10 vulnerabilities?",
                "expected": ["OWASP", "security", "vulnerability", "injection", "XSS"]
            },
            "sre_devops": {
                "query": "How do you implement zero-downtime deployments?",
                "expected": ["deployment", "blue-green", "canary", "rolling", "kubernetes"]
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for agent in self.test_agents:
                # Find the agent's domain
                agent_domain = None
                canonical = agent.get('canonical_name', '')
                for domain in domain_tests.keys():
                    if domain in canonical:
                        agent_domain = domain
                        break
                
                if not agent_domain:
                    continue
                
                print(f"\nTesting {agent['display_name']} - Domain: {agent_domain}")
                
                # Create session
                session_resp = await client.post(
                    f"{API_BASE_URL}/chat/session?agent_id={agent['id']}"
                )
                if session_resp.status_code != 200:
                    continue
                    
                session_id = session_resp.json()['session_id']
                
                # Ask domain-specific question
                test = domain_tests[agent_domain]
                response = await client.post(
                    f"{API_BASE_URL}/chat/message",
                    json={
                        "agent_id": agent['id'],
                        "message": test['query'],
                        "session_id": session_id
                    }
                )
                
                if response.status_code == 200:
                    ai_response = response.json()['response']
                    
                    # Check for expected terms
                    found_terms = [term for term in test['expected'] 
                                  if term.lower() in ai_response.lower()]
                    
                    expertise_score = (len(found_terms) / len(test['expected'])) * 10
                    
                    self.results["domain_expertise"].append({
                        "agent": agent['display_name'],
                        "domain": agent_domain,
                        "query": test['query'],
                        "expected_terms": test['expected'],
                        "found_terms": found_terms,
                        "expertise_score": expertise_score
                    })
                    
                    print(f"  Query: {test['query']}")
                    print(f"  Found terms: {found_terms}")
                    print(f"  Expertise score: {expertise_score:.1f}/10")
    
    async def test_conversation_flow(self):
        """Test multi-turn conversation abilities"""
        print(f"\n{Colors.YELLOW}💬 Testing Conversation Flow{Colors.END}")
        
        conversation = [
            "I need help with a Python web application",
            "It should handle user authentication",
            "What database would you recommend?",
            "How do I implement rate limiting?",
            "Can you summarize your recommendations?"
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test with an engineering agent
            eng_agent = next((a for a in self.test_agents 
                            if "engineering" in a.get('canonical_name', '')), None)
            
            if not eng_agent:
                print("No engineering agent found for conversation test")
                return
            
            print(f"\nTesting conversation with: {eng_agent['display_name']}")
            
            # Create session
            session_resp = await client.post(
                f"{API_BASE_URL}/chat/session?agent_id={eng_agent['id']}"
            )
            if session_resp.status_code != 200:
                return
                
            session_id = session_resp.json()['session_id']
            
            context_maintained = True
            responses = []
            
            for i, message in enumerate(conversation):
                response = await client.post(
                    f"{API_BASE_URL}/chat/message",
                    json={
                        "agent_id": eng_agent['id'],
                        "message": message,
                        "session_id": session_id
                    }
                )
                
                if response.status_code == 200:
                    ai_response = response.json()['response']
                    responses.append(ai_response)
                    
                    print(f"\n  Turn {i+1}: {message}")
                    print(f"  Response: {ai_response[:100]}...")
                    
                    # Check if context is maintained (simplified)
                    if i > 0 and i == 4:  # Summary turn
                        # Check if summary mentions previous topics
                        topics = ["Python", "authentication", "database", "rate limiting"]
                        mentioned = sum(1 for topic in topics 
                                      if topic.lower() in ai_response.lower())
                        
                        if mentioned < 2:
                            context_maintained = False
                            print(f"  ⚠️  Context not fully maintained (only {mentioned}/4 topics)")
                        else:
                            print(f"  ✅ Context maintained ({mentioned}/4 topics)")
            
            self.results["collaboration"].append({
                "agent": eng_agent['display_name'],
                "conversation_length": len(responses),
                "context_maintained": context_maintained,
                "avg_response_length": sum(len(r) for r in responses) / len(responses)
            })
    
    async def test_error_handling(self):
        """Test how agents handle unclear or problematic inputs"""
        print(f"\n{Colors.YELLOW}🛡️ Testing Error Handling{Colors.END}")
        
        problematic_inputs = [
            "sjdkfhskdjfh",  # Gibberish
            "",  # Empty
            "Tell me everything about everything",  # Too broad
            "Write me malicious code",  # Ethical boundary
            "What's 2+2? But explain it in 10000 words"  # Unreasonable request
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            agent = self.test_agents[0] if self.test_agents else None
            if not agent:
                return
            
            print(f"\nTesting with: {agent['display_name']}")
            
            # Create session
            session_resp = await client.post(
                f"{API_BASE_URL}/chat/session?agent_id={agent['id']}"
            )
            if session_resp.status_code != 200:
                return
                
            session_id = session_resp.json()['session_id']
            
            for input_text in problematic_inputs:
                display_input = input_text if input_text else "[empty]"
                print(f"\n  Input: {display_input[:50]}...")
                
                response = await client.post(
                    f"{API_BASE_URL}/chat/message",
                    json={
                        "agent_id": agent['id'],
                        "message": input_text,
                        "session_id": session_id
                    }
                )
                
                if response.status_code == 200:
                    ai_response = response.json()['response']
                    
                    # Check if response is appropriate
                    is_appropriate = (
                        len(ai_response) > 10 and
                        len(ai_response) < 2000 and
                        "error" not in ai_response.lower() and
                        ai_response != input_text
                    )
                    
                    print(f"  Response appropriate: {'✅' if is_appropriate else '❌'}")
                    print(f"  Response preview: {ai_response[:80]}...")
    
    def generate_report(self):
        """Generate quality assessment report"""
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}📊 AGENT QUALITY ASSESSMENT REPORT{Colors.END}")
        print(f"{Colors.CYAN}{'='*60}{Colors.END}")
        
        # Response Quality Summary
        if self.results["response_quality"]:
            print(f"\n{Colors.YELLOW}1. Response Quality{Colors.END}")
            avg_quality = sum(r['quality_score'] for r in self.results["response_quality"]) / len(self.results["response_quality"])
            avg_time = sum(r['response_time'] for r in self.results["response_quality"]) / len(self.results["response_quality"])
            
            print(f"  Average quality score: {avg_quality:.1f}/10")
            print(f"  Average response time: {avg_time:.2f}s")
            
            # Best performing agents
            best_agents = sorted(self.results["response_quality"], 
                               key=lambda x: x['quality_score'], reverse=True)[:3]
            print(f"\n  Top performers:")
            for agent in best_agents:
                print(f"    • {agent['agent']}: {agent['quality_score']}/10")
        
        # Persona Consistency
        if self.results["persona_consistency"]:
            print(f"\n{Colors.YELLOW}2. Persona Consistency{Colors.END}")
            avg_consistency = sum(r['consistency_score'] for r in self.results["persona_consistency"]) / len(self.results["persona_consistency"])
            print(f"  Average consistency: {avg_consistency:.1f}/10")
        
        # Domain Expertise
        if self.results["domain_expertise"]:
            print(f"\n{Colors.YELLOW}3. Domain Expertise{Colors.END}")
            avg_expertise = sum(r['expertise_score'] for r in self.results["domain_expertise"]) / len(self.results["domain_expertise"])
            print(f"  Average expertise score: {avg_expertise:.1f}/10")
            
            # By domain
            by_domain = {}
            for result in self.results["domain_expertise"]:
                domain = result['domain']
                if domain not in by_domain:
                    by_domain[domain] = []
                by_domain[domain].append(result['expertise_score'])
            
            print(f"\n  By domain:")
            for domain, scores in by_domain.items():
                avg = sum(scores) / len(scores)
                print(f"    • {domain}: {avg:.1f}/10")
        
        # Overall Assessment
        print(f"\n{Colors.CYAN}Overall Assessment:{Colors.END}")
        
        all_scores = []
        if self.results["response_quality"]:
            all_scores.extend([r['quality_score'] for r in self.results["response_quality"]])
        if self.results["persona_consistency"]:
            all_scores.extend([r['consistency_score'] for r in self.results["persona_consistency"]])
        if self.results["domain_expertise"]:
            all_scores.extend([r['expertise_score'] for r in self.results["domain_expertise"]])
        
        if all_scores:
            overall_avg = sum(all_scores) / len(all_scores)
            
            if overall_avg >= 8:
                grade = "A"
                assessment = "Excellent"
            elif overall_avg >= 7:
                grade = "B"
                assessment = "Good"
            elif overall_avg >= 6:
                grade = "C"
                assessment = "Satisfactory"
            else:
                grade = "D"
                assessment = "Needs Improvement"
            
            print(f"\n  Overall Score: {overall_avg:.1f}/10")
            print(f"  Grade: {grade}")
            print(f"  Assessment: {assessment}")
        
        # Recommendations
        print(f"\n{Colors.YELLOW}Recommendations:{Colors.END}")
        if all_scores and overall_avg < 7:
            print("  • Consider fine-tuning agent instructions")
            print("  • Add more specific domain knowledge to prompts")
            print("  • Implement conversation memory")
        else:
            print("  • Agents are performing well")
            print("  • Consider adding specialized tools for each domain")
            print("  • Implement agent collaboration features")
        
        print(f"\n{Colors.CYAN}{'='*60}{Colors.END}")

async def main():
    print(f"{Colors.BLUE}🤖 AgentVerse Quality Testing Suite{Colors.END}")
    print(f"{Colors.BLUE}Testing AI response quality, personas, and capabilities{Colors.END}\n")
    
    # Check API
    try:
        async with httpx.AsyncClient() as client:
            health = await client.get(f"{API_BASE_URL}/health", timeout=2.0)
            health_data = health.json()
            
            llm_status = "❌ No LLM"
            if health_data.get('llm_providers', {}).get('ollama', {}).get('available'):
                llm_status = "🦙 Ollama"
            elif health_data.get('llm_providers', {}).get('openai', {}).get('available'):
                llm_status = "🤖 OpenAI"
            
            print(f"API Status: ✅ Running")
            print(f"LLM Provider: {llm_status}")
            print(f"Agents Loaded: {health_data.get('agents_loaded', 0)}")
            print("-" * 60)
            
    except:
        print(f"{Colors.RED}❌ API is not running!{Colors.END}")
        print("Start with: ./start_agentverse.sh")
        return
    
    # Run tests
    tester = AgentQualityTester()
    await tester.setup()
    
    # Run quality tests
    tests = [
        tester.test_response_quality,
        tester.test_persona_consistency,
        tester.test_domain_expertise,
        tester.test_conversation_flow,
        tester.test_error_handling
    ]
    
    for test in tests:
        try:
            await test()
        except Exception as e:
            print(f"\n{Colors.RED}Error in {test.__name__}: {e}{Colors.END}")
    
    # Generate report
    tester.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
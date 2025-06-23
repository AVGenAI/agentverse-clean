#!/usr/bin/env python3
"""
Test agent creation speed for Agent Verse
"""
import asyncio
import aiohttp
import time
import json
import random
from datetime import datetime

API_BASE = "http://localhost:8000"

class AgentSpeedTest:
    def __init__(self):
        self.agents_created = 0
        self.start_time = None
        self.errors = 0
        
    async def create_agent(self, session, index):
        """Create a single agent"""
        domains = ['sre', 'devops', 'data', 'engineering', 'security', 'healthcare', 'finance']
        models = ['gpt-4o-mini', 'gpt-3.5-turbo', 'llama3', 'claude-3']
        
        agent_data = {
            "id": f"test_agent_{int(time.time() * 1000000)}_{index}",
            "name": f"Test Agent {index}",
            "type": "specialist",
            "domain": random.choice(domains),
            "version": "1.0.0",
            "status": "active",
            "instructions": f"You are test agent #{index} specialized in {random.choice(domains)}",
            "model_preferences": {
                "primary": random.choice(models),
                "temperature": 0.7,
                "max_tokens": 2000
            },
            "capabilities": {
                "primary_expertise": ["Testing", "Performance"],
                "tools_mastery": {}
            },
            "tools": [],
            "enhanced_metadata": {
                "trust_score": 0.8,
                "created_by": "Speed Test",
                "created_at": datetime.now().isoformat()
            }
        }
        
        try:
            async with session.post(f"{API_BASE}/agents", json=agent_data) as resp:
                if resp.status in [200, 201]:
                    self.agents_created += 1
                    if self.agents_created % 100 == 0:
                        elapsed = time.time() - self.start_time
                        rate = self.agents_created / elapsed
                        print(f"Created {self.agents_created} agents | Rate: {rate:.1f} agents/sec")
                else:
                    self.errors += 1
        except Exception as e:
            self.errors += 1
            
    async def run_batch(self, batch_size=100):
        """Create a batch of agents concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(batch_size):
                task = self.create_agent(session, self.agents_created + i)
                tasks.append(task)
            await asyncio.gather(*tasks)
            
    async def test_creation_speed(self, duration_seconds=60):
        """Test how many agents we can create in given duration"""
        print(f"\n🚀 Testing agent creation speed for {duration_seconds} seconds...")
        print("=" * 60)
        
        self.start_time = time.time()
        end_time = self.start_time + duration_seconds
        
        while time.time() < end_time:
            await self.run_batch(batch_size=50)  # Create 50 agents at a time
            
        elapsed = time.time() - self.start_time
        rate = self.agents_created / elapsed
        
        print(f"\n📊 Results:")
        print(f"Duration: {elapsed:.1f} seconds")
        print(f"Agents created: {self.agents_created:,}")
        print(f"Creation rate: {rate:.1f} agents/second")
        print(f"Errors: {self.errors}")
        
        # Extrapolate to 10 minutes
        ten_min_estimate = int(rate * 600)
        print(f"\n📈 10-minute estimate: {ten_min_estimate:,} agents")
        print(f"1-hour estimate: {int(rate * 3600):,} agents")
        
        # Check bottlenecks
        if rate < 100:
            print("\n⚠️  Bottlenecks detected:")
            print("- Consider using bulk insert endpoints")
            print("- Database writes may be limiting factor")
            print("- Network latency affects concurrent requests")
        elif rate < 1000:
            print("\n✅ Good performance! To reach 1M agents in 10 min:")
            print("- Need ~1,667 agents/second")
            print("- Consider batch database operations")
            print("- Use connection pooling")
        else:
            print("\n🎉 Excellent performance!")
            
async def main():
    tester = AgentSpeedTest()
    
    # First do a 10-second test
    await tester.test_creation_speed(duration_seconds=10)
    
    # Reset for actual test
    print("\n" + "=" * 60)
    response = input("\nRun full 60-second test? (y/n): ")
    
    if response.lower() == 'y':
        tester.agents_created = 0
        tester.errors = 0
        await tester.test_creation_speed(duration_seconds=60)

if __name__ == "__main__":
    asyncio.run(main())
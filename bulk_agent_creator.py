#!/usr/bin/env python3
"""
Bulk agent creator for Agent Verse - Optimized for speed
"""
import json
import time
import random
import multiprocessing
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor
import os

def generate_agents_batch(batch_num, batch_size=10000):
    """Generate a batch of agents"""
    domains = ['sre', 'devops', 'data', 'engineering', 'security', 'healthcare', 'finance', 'ml', 'cloud', 'frontend']
    types = ['specialist', 'coordinator', 'analyzer', 'executor', 'validator']
    models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'claude-3', 'llama3', 'mixtral-8x7b']
    
    agents = []
    base_time = int(time.time() * 1000000)
    
    for i in range(batch_size):
        agent_id = f"bulk_agent_{base_time}_{batch_num}_{i}"
        domain = random.choice(domains)
        
        agent = {
            "id": agent_id,
            "name": f"Agent {domain.upper()} {batch_num}-{i}",
            "type": random.choice(types),
            "domain": domain,
            "version": "1.0.0",
            "status": "active",
            "instructions": f"You are an expert {domain} agent with specialized knowledge",
            "model_preferences": {
                "primary": random.choice(models),
                "temperature": round(random.uniform(0.3, 0.9), 1),
                "max_tokens": random.choice([1000, 2000, 3000, 4000])
            },
            "capabilities": {
                "primary_expertise": random.sample([
                    "Problem Solving", "Analysis", "Automation", "Monitoring",
                    "Optimization", "Security", "Performance", "Integration"
                ], k=3),
                "tools_mastery": {}
            },
            "tools": random.sample([
                "search", "create", "update", "analyze", "monitor",
                "deploy", "scale", "report", "alert"
            ], k=random.randint(0, 5)),
            "enhanced_metadata": {
                "agent_uuid": agent_id,
                "canonical_name": f"avos.{domain}.{agent_id}",
                "display_name": f"Agent {domain.upper()} {batch_num}-{i}",
                "avatar": "🤖",
                "trust_score": round(random.uniform(0.7, 0.95), 2),
                "created_by": "Bulk Creator",
                "created_at": datetime.now().isoformat()
            }
        }
        agents.append(agent)
    
    return agents

def save_agents_to_file(agents, filename):
    """Save agents to JSON file"""
    with open(filename, 'w') as f:
        json.dump(agents, f, indent=2)
    return len(agents)

def create_million_agents(target_count=1000000, output_dir="bulk_agents"):
    """Create a million agents using multiprocessing"""
    print(f"\n🚀 Creating {target_count:,} agents...")
    print("=" * 60)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    start_time = time.time()
    batch_size = 10000  # Agents per batch
    num_batches = target_count // batch_size
    
    # Use all CPU cores
    num_workers = multiprocessing.cpu_count()
    print(f"Using {num_workers} CPU cores")
    
    agents_created = 0
    
    # Generate agents in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # Submit batch generation tasks
        futures = []
        for batch_num in range(num_batches):
            future = executor.submit(generate_agents_batch, batch_num, batch_size)
            futures.append((batch_num, future))
        
        # Collect results and save
        for batch_num, future in futures:
            agents = future.result()
            filename = os.path.join(output_dir, f"agents_batch_{batch_num:04d}.json")
            count = save_agents_to_file(agents, filename)
            agents_created += count
            
            if (batch_num + 1) % 10 == 0:
                elapsed = time.time() - start_time
                rate = agents_created / elapsed
                eta = (target_count - agents_created) / rate
                print(f"Progress: {agents_created:,}/{target_count:,} agents | "
                      f"Rate: {rate:.0f} agents/sec | ETA: {eta:.0f}s")
    
    # Final report
    elapsed = time.time() - start_time
    rate = agents_created / elapsed
    
    print(f"\n✅ Completed!")
    print(f"Total agents created: {agents_created:,}")
    print(f"Time taken: {elapsed:.1f} seconds")
    print(f"Creation rate: {rate:.0f} agents/second")
    print(f"Files created: {num_batches} in '{output_dir}/' directory")
    
    # Calculate estimates
    ten_min = int(rate * 600)
    one_hour = int(rate * 3600)
    
    print(f"\n📊 Performance Estimates:")
    print(f"10 minutes: {ten_min:,} agents")
    print(f"1 hour: {one_hour:,} agents")
    
    if ten_min >= 1000000:
        print("\n🎉 Can create 1 MILLION+ agents in 10 minutes!")
    elif ten_min >= 100000:
        print(f"\n✅ Can create {ten_min//1000}K agents in 10 minutes")
    else:
        print(f"\n⚠️  Current rate would create {ten_min:,} agents in 10 minutes")
        print("Optimization suggestions:")
        print("- Use bulk database inserts")
        print("- Implement write-through caching")
        print("- Use async I/O for file operations")

def estimate_only():
    """Quick estimation without creating files"""
    print("\n⚡ Quick Performance Estimation")
    print("=" * 40)
    
    # Test single batch generation speed
    start = time.time()
    agents = generate_agents_batch(0, 1000)
    elapsed = time.time() - start
    
    rate = 1000 / elapsed
    
    print(f"Single-core generation rate: {rate:.0f} agents/second")
    print(f"With {multiprocessing.cpu_count()} cores: ~{rate * multiprocessing.cpu_count():.0f} agents/second")
    
    ten_min = int(rate * multiprocessing.cpu_count() * 600)
    print(f"\n📈 10-minute estimate: {ten_min:,} agents")
    
    if ten_min >= 1000000:
        print("✅ Should easily create 1M+ agents in 10 minutes!")
    else:
        time_for_million = 1000000 / (rate * multiprocessing.cpu_count())
        print(f"⏱️  Time to create 1M agents: {time_for_million/60:.1f} minutes")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--estimate":
        estimate_only()
    else:
        print("Options:")
        print("1. Quick estimate (no files created)")
        print("2. Create 100K agents")
        print("3. Create 1M agents")
        
        choice = input("\nSelect option (1-3): ")
        
        if choice == "1":
            estimate_only()
        elif choice == "2":
            create_million_agents(target_count=100000)
        elif choice == "3":
            create_million_agents(target_count=1000000)
        else:
            print("Invalid choice")
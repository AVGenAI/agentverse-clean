#!/usr/bin/env python3
"""
Generate and test agents without Docker
Creates 10K agents and demonstrates the system
"""
import json
import time
from bulk_agent_generator import generate_bulk_agents, save_agents

def generate_agents_demo(count: int = 10000):
    """Generate agents and show statistics"""
    print(f"\n🚀 Generating {count:,} AI Agents...")
    print("=" * 50)
    
    start_time = time.time()
    
    # Generate agents
    agents = generate_bulk_agents(count)
    
    gen_time = time.time() - start_time
    
    # Save to file
    filename = f"src/config/agentverse_agents_{count}.json"
    save_agents(agents, filename)
    
    print(f"\n✅ Generation Complete!")
    print(f"   Time taken: {gen_time:.2f} seconds")
    print(f"   Rate: {count/gen_time:.0f} agents/second")
    print(f"   File size: {get_file_size(filename)}")
    
    # Show sample agents
    print(f"\n📋 Sample Agents:")
    for i in range(5):
        agent = agents[i]
        meta = agent["enhanced_metadata"]
        print(f"\n{i+1}. {meta['display_name']} ({meta['agent_uuid']})")
        print(f"   Domain: {meta['taxonomy']['domain']}")
        print(f"   Type: {meta['taxonomy']['type']}")
        print(f"   Trust Score: {meta['quality']['trust_score']}")
        print(f"   Skills: {', '.join(meta['capabilities']['primary_expertise'][:3])}...")
    
    # Domain distribution
    print(f"\n📊 Domain Distribution:")
    domains = {}
    for agent in agents:
        domain = agent["enhanced_metadata"]["taxonomy"]["domain"]
        domains[domain] = domains.get(domain, 0) + 1
    
    for domain, count in sorted(domains.items()):
        percentage = (count / len(agents)) * 100
        bar = "█" * int(percentage / 2)
        print(f"   {domain:15} {count:5} ({percentage:4.1f}%) {bar}")
    
    # Quality metrics
    avg_trust = sum(a["enhanced_metadata"]["quality"]["trust_score"] for a in agents) / len(agents)
    high_trust = sum(1 for a in agents if a["enhanced_metadata"]["quality"]["trust_score"] >= 0.9)
    
    print(f"\n🏆 Quality Metrics:")
    print(f"   Average Trust Score: {avg_trust:.3f}")
    print(f"   High Trust Agents (≥0.9): {high_trust:,} ({high_trust/len(agents)*100:.1f}%)")
    
    # Tool distribution
    all_tools = set()
    for agent in agents:
        tools = agent["enhanced_metadata"]["capabilities"]["tools_mastery"].keys()
        all_tools.update(tools)
    
    print(f"\n🔧 Tool Coverage:")
    print(f"   Unique tools: {len(all_tools)}")
    print(f"   Most common: {', '.join(list(all_tools)[:10])}...")
    
    return agents

def get_file_size(filename):
    """Get human-readable file size"""
    size = os.path.getsize(filename)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def test_agent_search(agents):
    """Test searching through agents"""
    print(f"\n🔍 Testing Agent Search...")
    print("=" * 50)
    
    # Test 1: Domain search
    start = time.time()
    engineering_agents = [a for a in agents if a["enhanced_metadata"]["taxonomy"]["domain"] == "engineering"]
    search_time = (time.time() - start) * 1000
    print(f"\n1. Domain Search (engineering): {len(engineering_agents)} found in {search_time:.2f}ms")
    
    # Test 2: Skill search
    start = time.time()
    python_agents = [a for a in agents 
                     if "Python" in a["enhanced_metadata"]["capabilities"]["primary_expertise"]]
    search_time = (time.time() - start) * 1000
    print(f"2. Skill Search (Python): {len(python_agents)} found in {search_time:.2f}ms")
    
    # Test 3: Trust score filter
    start = time.time()
    trusted_agents = [a for a in agents 
                      if a["enhanced_metadata"]["quality"]["trust_score"] >= 0.95]
    search_time = (time.time() - start) * 1000
    print(f"3. Trust Filter (≥0.95): {len(trusted_agents)} found in {search_time:.2f}ms")
    
    # Test 4: Complex query
    start = time.time()
    complex_results = [
        a for a in agents 
        if a["enhanced_metadata"]["taxonomy"]["domain"] == "sre"
        and "Kubernetes" in a["enhanced_metadata"]["capabilities"]["primary_expertise"]
        and a["enhanced_metadata"]["quality"]["trust_score"] >= 0.9
    ]
    search_time = (time.time() - start) * 1000
    print(f"4. Complex Query (SRE + K8s + Trust≥0.9): {len(complex_results)} found in {search_time:.2f}ms")

def update_api_config(count: int):
    """Update API to use new agent file"""
    print(f"\n🔧 Updating API Configuration...")
    
    # Update the API agent_manager.py to use the new file
    config_update = f"""
# To use the {count:,} agents in the API:

1. Update agent_manager.py line ~36:
   config_paths = [
       "../src/config/agentverse_agents_{count}.json",
       "src/config/agentverse_agents_{count}.json",
       "/Users/vallu/z_AV_Labs_Gemini_June2025/aiagents/src/config/agentverse_agents_{count}.json"
   ]

2. Restart the API server:
   cd agentverse_api
   uvicorn main:app --reload --port 8000

3. The API will now serve {count:,} agents!
"""
    print(config_update)

if __name__ == "__main__":
    import os
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate and test agents")
    parser.add_argument("--count", type=int, default=10000, 
                       help="Number of agents to generate")
    parser.add_argument("--test-only", action="store_true",
                       help="Only run tests on existing agents")
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════╗
║     AgentVerse Agent Generator & Test    ║
╚══════════════════════════════════════════╝
    """)
    
    if args.test_only:
        # Load existing agents
        filename = f"src/config/agentverse_agents_{args.count}.json"
        if os.path.exists(filename):
            print(f"Loading {filename}...")
            with open(filename, 'r') as f:
                agents = json.load(f)
            test_agent_search(agents)
        else:
            print(f"❌ File not found: {filename}")
            print(f"   Run without --test-only to generate agents first")
    else:
        # Generate new agents
        agents = generate_agents_demo(args.count)
        test_agent_search(agents)
        update_api_config(args.count)
        
        print(f"\n✨ Done! Generated {args.count:,} agents")
        print(f"\nNext steps:")
        print(f"1. Generate 100K agents: python generate_and_test_agents.py --count 100000")
        print(f"2. Generate 1M agents: python generate_and_test_agents.py --count 1000000")
        print(f"3. Test existing: python generate_and_test_agents.py --count {args.count} --test-only")
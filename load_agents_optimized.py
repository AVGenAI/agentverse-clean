#!/usr/bin/env python3
"""
Optimized agent loader for handling large numbers of agents
"""
import json
import time

def test_agent_loading():
    """Test loading different sized agent files"""
    
    configs = [
        ("1K agents", "src/config/agentverse_agents_1000.json"),
        ("10K agents", "src/config/agentverse_agents_10000.json")
    ]
    
    for name, path in configs:
        print(f"\n📊 Testing {name}...")
        
        try:
            start = time.time()
            with open(path, 'r') as f:
                agents = json.load(f)
            load_time = time.time() - start
            
            print(f"  ✅ Loaded {len(agents)} agents in {load_time:.2f}s")
            print(f"  📁 File size: {os.path.getsize(path) / 1024 / 1024:.1f} MB")
            
            # Test JSON serialization (API response)
            start = time.time()
            json_str = json.dumps(agents[:100])  # First 100 agents
            serialize_time = time.time() - start
            print(f"  ⚡ Serialized 100 agents in {serialize_time:.3f}s")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

def create_lightweight_config(input_file: str, output_file: str, max_agents: int = 5000):
    """Create a smaller config for testing"""
    
    print(f"\n🔧 Creating lightweight config with {max_agents} agents...")
    
    with open(input_file, 'r') as f:
        agents = json.load(f)
    
    # Take first N agents
    lightweight = agents[:max_agents]
    
    with open(output_file, 'w') as f:
        json.dump(lightweight, f, indent=2)
    
    print(f"✅ Created {output_file} with {len(lightweight)} agents")
    print(f"📁 File size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    import os
    
    print("🚀 Agent Loading Performance Test")
    print("=" * 40)
    
    # Test current loading
    test_agent_loading()
    
    # Create optimized configs
    print("\n💡 Creating optimized configurations...")
    
    # 5K agents for balanced performance
    create_lightweight_config(
        "src/config/agentverse_agents_10000.json",
        "src/config/agentverse_agents_5000.json",
        5000
    )
    
    # 2K agents for fast loading
    create_lightweight_config(
        "src/config/agentverse_agents_10000.json",
        "src/config/agentverse_agents_2000.json",
        2000
    )
    
    print("\n✨ Recommendations:")
    print("  - Use 2K agents for development/testing")
    print("  - Use 5K agents for demos")
    print("  - Use 10K+ agents with database backend")
    print("  - Implement pagination for large datasets")
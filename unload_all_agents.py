#!/usr/bin/env python3
"""
Unload All Agents Script
Clears all agents from the system to allow fresh spawning
"""
import os
import json
import shutil
from datetime import datetime

def unload_all_agents():
    """Unload all agents from the system"""
    print("🧹 Starting agent unload process...")
    print("="*60)
    
    # Paths to check
    config_dir = "src/config"
    backup_dir = f"backups/unload_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create backup directory
    os.makedirs(backup_dir, exist_ok=True)
    print(f"📁 Created backup directory: {backup_dir}")
    
    # Files to process
    agent_files = [
        "agentverse_agents_1000.json",
        "agents_config.json",
        "agent_catalog.json",
        "1000_agents.json",
        "1000_agents_enhanced.json"
    ]
    
    # Backup and clear agent files
    for filename in agent_files:
        filepath = os.path.join(config_dir, filename)
        if os.path.exists(filepath):
            # Backup the file
            backup_path = os.path.join(backup_dir, filename)
            shutil.copy2(filepath, backup_path)
            print(f"✅ Backed up: {filename}")
            
            # Clear the file (empty array)
            with open(filepath, 'w') as f:
                json.dump([], f, indent=2)
            print(f"🗑️  Cleared: {filename}")
    
    # Clear agent manager cache if exists
    cache_files = [
        "agentverse_api/agent_cache.json",
        ".agent_cache",
        "agent_state.json"
    ]
    
    for cache_file in cache_files:
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"🗑️  Removed cache: {cache_file}")
    
    # Clear any agent-specific directories
    agent_dirs = [
        "agents_workspace",
        "agent_data",
        "agent_logs"
    ]
    
    for agent_dir in agent_dirs:
        if os.path.exists(agent_dir):
            shutil.rmtree(agent_dir)
            print(f"🗑️  Removed directory: {agent_dir}")
    
    print("\n" + "="*60)
    print("✨ All agents have been unloaded!")
    print(f"📦 Backups saved to: {backup_dir}")
    print("\nYou can now run the agent creation script to spawn fresh agents.")
    
    # Summary
    print("\n📊 Summary:")
    print(f"- Agent config files cleared: {len([f for f in agent_files if os.path.exists(os.path.join(config_dir, f))])}")
    print(f"- Cache files removed: {len([f for f in cache_files if os.path.exists(f)])}")
    print(f"- Agent directories removed: {len([d for d in agent_dirs if os.path.exists(d)])}")
    
    return backup_dir

if __name__ == "__main__":
    try:
        backup_location = unload_all_agents()
        print(f"\n💡 To restore agents, copy files from: {backup_location}")
    except Exception as e:
        print(f"\n❌ Error unloading agents: {e}")
        print("Please check file permissions and paths.")
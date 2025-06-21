#!/usr/bin/env python3
"""
Setup OpenAI for AgentVerse
"""

import os
import sys
from pathlib import Path

def setup_openai():
    print("🤖 AgentVerse OpenAI Setup")
    print("="*50)
    
    # Check for existing API key
    env_file = Path("agentverse_api/.env")
    existing_key = None
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('OPENAI_API_KEY=') and 'your_openai_api_key_here' not in line:
                    existing_key = line.split('=')[1].strip()
                    break
    
    if existing_key:
        print(f"✅ Found existing OpenAI API key: {existing_key[:10]}...")
        use_existing = input("Use this key? (y/n): ").lower() == 'y'
        if use_existing:
            return
    
    # Get new API key
    print("\nTo use OpenAI, you need an API key from: https://platform.openai.com/api-keys")
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return
    
    # Update .env file
    env_content = f"""# LLM Provider Configuration
# Using OpenAI for better quality responses

# Disable Ollama and use OpenAI
USE_OLLAMA=false
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# OpenAI Configuration
OPENAI_API_KEY={api_key}
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("\n✅ OpenAI configured successfully!")
    print("\nSettings:")
    print(f"  Model: gpt-4o-mini (fast and efficient)")
    print(f"  Max Tokens: 2000")
    print(f"  Temperature: 0.7")
    
    print("\n📝 Next steps:")
    print("1. Restart the API server:")
    print("   cd agentverse_api && ./venv/bin/uvicorn main:app --reload")
    print("2. Test an agent in the chat UI")
    print("3. The SRE agent will now use OpenAI for better responses!")
    
    # Also update the main .env file for ServiceNow
    main_env = Path(".env")
    if main_env.exists():
        print("\n🔄 Updating main .env file with OpenAI key...")
        with open(main_env, 'r') as f:
            lines = f.readlines()
        
        # Add OpenAI key if not present
        has_openai = any('OPENAI_API_KEY' in line for line in lines)
        if not has_openai:
            lines.append(f"\n# OpenAI Configuration\n")
            lines.append(f"OPENAI_API_KEY={api_key}\n")
            with open(main_env, 'w') as f:
                f.writelines(lines)
            print("✅ Added OpenAI key to main .env")

if __name__ == "__main__":
    setup_openai()
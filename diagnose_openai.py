#!/usr/bin/env python3
"""
Diagnose OpenAI Integration Issues
"""
import os
import sys
from pathlib import Path

print("🔍 Diagnosing OpenAI Integration")
print("="*50)

# Check environment variables
print("\n1. Checking environment variables:")
print(f"   Current directory: {os.getcwd()}")

# Check both .env files
env_files = [
    Path("agentverse_api/.env"),
    Path(".env")
]

for env_file in env_files:
    if env_file.exists():
        print(f"\n   Checking {env_file}:")
        with open(env_file, 'r') as f:
            for line in f:
                if 'OPENAI_API_KEY' in line and not line.strip().startswith('#'):
                    if 'your_openai_api_key_here' in line:
                        print(f"      ❌ OPENAI_API_KEY is not set (placeholder found)")
                    else:
                        key = line.split('=')[1].strip()[:20]
                        print(f"      ✅ OPENAI_API_KEY found: {key}...")
                if 'USE_OLLAMA' in line and not line.strip().startswith('#'):
                    value = line.split('=')[1].strip()
                    print(f"      USE_OLLAMA = {value}")
    else:
        print(f"   ❌ {env_file} not found")

# Test loading environment
print("\n2. Testing environment loading:")
os.chdir('agentverse_api')
sys.path.insert(0, os.getcwd())

from dotenv import load_dotenv
load_dotenv()

print(f"   OPENAI_API_KEY from env: {os.getenv('OPENAI_API_KEY', 'NOT SET')[:20]}...")
print(f"   USE_OLLAMA from env: {os.getenv('USE_OLLAMA', 'NOT SET')}")

# Test OpenAI SDK
print("\n3. Testing OpenAI SDK:")
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # Test the API key
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'OpenAI is working!'"}],
            max_tokens=10
        )
        print(f"   ✅ OpenAI API is working! Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   ❌ OpenAI API error: {e}")
        if "Invalid" in str(e):
            print("      → API key might be invalid or expired")
        elif "quota" in str(e).lower():
            print("      → API quota might be exceeded")
            
except ImportError:
    print("   ❌ OpenAI SDK not installed. Run: pip install openai")

# Check agent creation
print("\n4. Testing agent creation:")
try:
    from agents import Agent
    test_agent = Agent(
        api_key=os.getenv('OPENAI_API_KEY'),
        name="Test Agent",
        instructions="You are a test agent.",
        model="gpt-4o-mini"
    )
    print("   ✅ Agent created successfully")
    
    # Test a simple message
    response = test_agent.run("Say hello")
    print(f"   ✅ Agent response: {response[:50]}...")
    
except Exception as e:
    print(f"   ❌ Agent creation error: {e}")

print("\n5. Recommendations:")
if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
    print("   • Set a valid OPENAI_API_KEY in agentverse_api/.env")
elif os.getenv('USE_OLLAMA') != 'false':
    print("   • Make sure USE_OLLAMA=false in agentverse_api/.env")
else:
    print("   • Check if the OpenAI API key is valid and has quota")
    print("   • Ensure 'openai' package is installed in the virtual environment")
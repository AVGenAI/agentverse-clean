#!/usr/bin/env python3
"""
Test OpenAI Chat Directly
"""
import os
import sys
sys.path.insert(0, 'agentverse_api')

from dotenv import load_dotenv
load_dotenv('agentverse_api/.env')

# Direct OpenAI test
from openai import OpenAI

api_key = os.getenv('OPENAI_API_KEY')
print(f"API Key loaded: {api_key[:20]}...")
print(f"USE_OLLAMA: {os.getenv('USE_OLLAMA')}")

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an SRE ServiceNow Specialist. You excel at incident response, ServiceNow integration, and SLO management."},
            {"role": "user", "content": "Hi, I need help with a production incident"}
        ],
        temperature=0.7,
        max_tokens=200
    )
    
    print("\n✅ OpenAI Response:")
    print(response.choices[0].message.content)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nPossible issues:")
    print("1. API key might be invalid")
    print("2. API quota might be exceeded")
    print("3. Network issues")
#!/usr/bin/env python3
"""
Simple OpenAI Test for SRE Agent
Using OpenAI SDK directly - no complex dependencies
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()

# Tool definitions for OpenAI function calling
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_incidents",
            "description": "Search ServiceNow incidents based on query criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'state=1' for active incidents)"
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_slo_status",
            "description": "Calculate SLO status and error budget for a service",
            "parameters": {
                "type": "object",
                "properties": {
                    "service": {
                        "type": "string",
                        "description": "Name of the service"
                    },
                    "slo_type": {
                        "type": "string",
                        "enum": ["availability", "latency", "error_rate"],
                        "description": "Type of SLO to check"
                    }
                },
                "required": ["service"]
            }
        }
    }
]

# Mock tool implementations
def search_incidents(query="state=1", limit=10):
    """Mock incident search"""
    return {
        "incidents": [
            {
                "number": "INC0012345",
                "short_description": "Payment service high latency",
                "priority": "1 - Critical",
                "state": "In Progress",
                "assigned_to": "SRE Team"
            },
            {
                "number": "INC0012346", 
                "short_description": "Database connection pool exhausted",
                "priority": "2 - High",
                "state": "New",
                "assigned_to": "Database Team"
            }
        ],
        "total": 2
    }

def calculate_slo_status(service, slo_type="availability"):
    """Mock SLO calculation"""
    return {
        "service": service,
        "slo_type": slo_type,
        "target": 99.9,
        "current": 99.85,
        "error_budget_remaining": 75.5,
        "status": "healthy"
    }

def main():
    """Test OpenAI function calling with SRE agent"""
    print("🧪 Simple OpenAI SRE Agent Test")
    print("="*60)
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return
        
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Initialize OpenAI client
    client = OpenAI(api_key=api_key)
    
    # SRE agent system prompt
    system_prompt = """You are an expert Site Reliability Engineer with ServiceNow expertise.
    
You have access to these tools:
- search_incidents: Find incidents in ServiceNow
- calculate_slo_status: Check SLO status for services

Always use tools when asked about incidents or SLO status."""
    
    # Test queries
    test_queries = [
        "Show me all critical incidents",
        "What's the SLO status for the payment service?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print("="*60)
        
        try:
            # Call OpenAI with tools
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # Check if tools were called
            if message.tool_calls:
                print(f"\n✅ Tool calls detected: {len(message.tool_calls)}")
                
                for tool_call in message.tool_calls:
                    print(f"\n🔧 Calling: {tool_call.function.name}")
                    print(f"   Args: {tool_call.function.arguments}")
                    
                    # Execute the tool
                    args = json.loads(tool_call.function.arguments)
                    if tool_call.function.name == "search_incidents":
                        result = search_incidents(**args)
                    elif tool_call.function.name == "calculate_slo_status":
                        result = calculate_slo_status(**args)
                    else:
                        result = {"error": "Unknown tool"}
                    
                    print(f"   Result: {json.dumps(result, indent=2)}")
                
                # Get final response with tool results
                final_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": query},
                        message,
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        }
                    ]
                )
                
                print(f"\n📝 Final Response:")
                print(final_response.choices[0].message.content)
            else:
                print("\n⚠️  No tools were called")
                print(f"📝 Response: {message.content}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Test completed!")

if __name__ == "__main__":
    main()
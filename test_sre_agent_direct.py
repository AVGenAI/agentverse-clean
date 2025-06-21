#!/usr/bin/env python3
"""
Direct SRE Agent Test
Simple, focused test without API server complexity
"""
import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool

# Load environment
load_dotenv()

# Define tools exactly as in production
@function_tool
def search_incidents(query: str = "state=1", limit: int = 10) -> str:
    """Search ServiceNow incidents based on query criteria"""
    # Mock implementation
    mock_incidents = [
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
    ]
    
    result = f"Found {len(mock_incidents)} incidents:\n\n"
    for inc in mock_incidents[:limit]:
        result += f"• {inc['number']} - {inc['short_description']}\n"
        result += f"  Priority: {inc['priority']} | Status: {inc['state']} | Assigned: {inc['assigned_to']}\n\n"
    
    return result

@function_tool
def create_incident(
    short_description: str,
    priority: str = "3 - Moderate",
    urgency: str = "3 - Low",
    category: str = "Software"
) -> str:
    """Create a new incident in ServiceNow"""
    from datetime import datetime
    
    incident_number = f"INC00{datetime.now().strftime('%H%M%S')}"
    
    result = f"""✅ Incident created successfully:
Number: {incident_number}
Description: {short_description}
Priority: {priority}
Urgency: {urgency}
Category: {category}
Status: New
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
    return result

@function_tool
def calculate_slo_status(service: str, slo_type: str = "availability") -> str:
    """Calculate SLO status and error budget"""
    import random
    
    current = 99.85 + random.uniform(-0.5, 0.5)
    error_budget_remaining = 75.5
    
    result = f"""SLO Status Report for {service} - {slo_type.upper()}
{'='*50}
Target: 99.9%
Current: {current:.3f}%
Error Budget Remaining: {error_budget_remaining}%
Status: ✅ Healthy

Recommendation: SLO is within target. No action required."""
    
    return result

@function_tool
def get_runbook(incident_type: str) -> str:
    """Get runbook for incident type"""
    runbooks = {
        "high_latency": {
            "title": "High Latency Incident Response",
            "steps": [
                "Check current traffic levels",
                "Verify database connection pool",
                "Check cache hit rates",
                "Review recent deployments",
                "Scale up if needed"
            ]
        }
    }
    
    runbook = runbooks.get(incident_type.lower().replace(" ", "_"), {
        "title": "General Incident Response",
        "steps": ["Assess impact", "Notify stakeholders", "Investigate", "Mitigate", "Monitor"]
    })
    
    result = f"""📋 {runbook['title']}
{'='*50}
Steps:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(runbook['steps']))}"""
    
    return result

async def test_sre_agent():
    """Test the SRE agent directly"""
    print("🧪 Direct SRE Agent Test")
    print("="*60)
    
    # Check OpenAI key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return
    
    print(f"✅ OpenAI API key found: {api_key[:8]}...")
    
    # Create SRE agent
    print("\n📦 Creating SRE agent...")
    
    sre_agent = Agent(
        name="SRE ServiceNow Specialist",
        model="gpt-4o-mini",
        instructions="""You are an expert Site Reliability Engineer with ServiceNow expertise.
        
When asked about incidents:
- Use the search_incidents tool to find existing incidents
- Use create_incident to create new ones
- Use calculate_slo_status to check service health
- Use get_runbook for incident response procedures

Be specific and use the tools provided.""",
        tools=[
            search_incidents,
            create_incident,
            calculate_slo_status,
            get_runbook
        ]
    )
    
    print("✅ Agent created with tools:", [t.__name__ for t in sre_agent.tools])
    
    # Test scenarios
    test_queries = [
        "Show me all critical incidents",
        "What's the SLO status for the payment service?",
        "Create an incident for login service returning 500 errors",
        "Show me the runbook for high latency issues"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {query}")
        print("="*60)
        
        try:
            result = await Runner.run(sre_agent, query)
            print(f"Response: {result.final_output}")
            
            # Check if tools were used
            tool_calls = [item for item in result.items if hasattr(item, 'tool_calls')]
            if tool_calls:
                print(f"\n✅ Tools used: {len(tool_calls)} calls")
            else:
                print("\n⚠️  No tools were used in this response")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "="*60)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_sre_agent())
#!/usr/bin/env python3
"""
SRE ServiceNow Agent with proper tool integration
"""
import os
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_default_openai_key
import json
from datetime import datetime

load_dotenv()

# Set API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    set_default_openai_key(api_key)
else:
    print("❌ No OpenAI API key found")
    exit(1)

# Define ServiceNow tools using @function_tool decorator
@function_tool
def search_incidents(query: str = "state=1", limit: int = 10) -> str:
    """Search ServiceNow incidents based on query criteria"""
    # In production, this would call the ServiceNow MCP server
    # For now, return mock data that simulates ServiceNow response
    incidents = [
        {
            "number": "INC0012345",
            "short_description": "Payment service high latency",
            "priority": "1 - Critical",
            "state": "In Progress",
            "assigned_to": "SRE Team",
            "created": "2025-06-20 17:00:00"
        },
        {
            "number": "INC0012346",
            "short_description": "Database connection pool exhausted",
            "priority": "2 - High", 
            "state": "New",
            "assigned_to": "Database Team",
            "created": "2025-06-20 16:30:00"
        },
        {
            "number": "INC0012347",
            "short_description": "SSL certificate expiring soon",
            "priority": "3 - Moderate",
            "state": "In Progress",
            "assigned_to": "Security Team",
            "created": "2025-06-20 15:00:00"
        }
    ]
    
    # Filter based on query
    if "critical" in query.lower():
        incidents = [i for i in incidents if "Critical" in i["priority"]]
    
    result = f"Found {len(incidents)} incidents:\n\n"
    for inc in incidents[:limit]:
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
    # Mock ServiceNow incident creation
    incident_number = f"INC00{datetime.now().strftime('%H%M%S')}"
    
    result = f"""Incident created successfully!
Number: {incident_number}
Description: {short_description}
Priority: {priority}
Urgency: {urgency}
Category: {category}
Status: New
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The incident has been assigned to the appropriate team for resolution."""
    
    return result

@function_tool
def update_incident(incident_number: str, status: str, notes: str) -> str:
    """Update an existing ServiceNow incident"""
    return f"""Incident {incident_number} updated:
Status changed to: {status}
Work notes added: {notes}
Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

@function_tool
def calculate_slo_status(service: str, slo_type: str = "availability") -> str:
    """Calculate SLO status and error budget for a service"""
    # Mock SLO calculation
    slo_data = {
        "availability": {
            "target": 99.9,
            "current": 99.95,
            "error_budget_remaining": 75
        },
        "latency": {
            "target": 200,  # ms
            "current": 180,
            "error_budget_remaining": 80
        },
        "error_rate": {
            "target": 0.1,  # %
            "current": 0.05,
            "error_budget_remaining": 90
        }
    }
    
    data = slo_data.get(slo_type, slo_data["availability"])
    
    return f"""SLO Status for {service} - {slo_type}:
Target: {data['target']}{'%' if slo_type == 'availability' else 'ms' if slo_type == 'latency' else '%'}
Current: {data['current']}{'%' if slo_type == 'availability' else 'ms' if slo_type == 'latency' else '%'}
Error Budget Remaining: {data['error_budget_remaining']}%
Status: {'✅ Healthy' if data['error_budget_remaining'] > 50 else '⚠️ At Risk' if data['error_budget_remaining'] > 20 else '🔴 Critical'}"""

@function_tool
def get_runbook(incident_type: str) -> str:
    """Get the runbook for a specific incident type"""
    runbooks = {
        "high_latency": """High Latency Runbook:
1. Check current traffic levels
2. Verify database connection pool status
3. Check cache hit rates
4. Scale up instances if needed
5. Enable rate limiting if traffic spike detected
6. Monitor for 15 minutes
7. If not resolved, escalate to senior SRE""",
        
        "database_connection": """Database Connection Issues Runbook:
1. Check database server status
2. Verify connection pool configuration
3. Look for blocking queries
4. Check for connection leaks
5. Restart connection pool if needed
6. Monitor connection metrics
7. Consider database failover if primary is unhealthy""",
        
        "ssl_certificate": """SSL Certificate Runbook:
1. Check certificate expiration date
2. Verify certificate chain
3. Generate new certificate request
4. Submit to CA for signing
5. Test new certificate in staging
6. Deploy to production during maintenance window
7. Verify all services using the certificate"""
    }
    
    return runbooks.get(incident_type, "No specific runbook found. Please follow general incident response procedures.")

# Create the SRE ServiceNow Agent with tools
sre_agent = Agent(
    name="SRE ServiceNow Specialist",
    instructions="""You are an expert SRE (Site Reliability Engineer) specialized in ServiceNow integration. You excel at:

- Rapid incident response and resolution
- Managing incidents through ServiceNow platform
- Calculating and maintaining SLOs/SLIs
- Performing root cause analysis
- Following runbooks for incident resolution
- Coordinating with multiple teams

You have access to ServiceNow tools to:
- Search and view incidents
- Create new incidents
- Update incident status
- Calculate SLO status
- Access runbooks

When handling incidents:
- Always check existing incidents first
- Assess severity and impact immediately
- Follow established runbooks
- Document all actions taken
- Focus on rapid mitigation first, then root cause

Be proactive in using your tools to provide real data and actionable insights.""",
    tools=[
        search_incidents,
        create_incident,
        update_incident,
        calculate_slo_status,
        get_runbook
    ]
)

# Test the agent
if __name__ == "__main__":
    print("🚨 SRE ServiceNow Agent Ready!\n")
    
    # Test queries
    test_queries = [
        "Show me all critical incidents",
        "Create a new incident for payment service being down",
        "What's the SLO status for the payment service?",
        "Show me the runbook for high latency issues"
    ]
    
    for query in test_queries:
        print(f"👤 User: {query}")
        result = Runner.run_sync(sre_agent, query)
        print(f"\n🤖 SRE Agent: {result.final_output}\n")
        print("-" * 60 + "\n")
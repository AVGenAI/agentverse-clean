#!/usr/bin/env python3
"""
Simple SRE Agent Script Examples
Quick and easy ways to use the SRE ServiceNow Agent
"""

import asyncio
from sre_servicenow_agent_fixed import SREServiceNowAgent

# Initialize the agent once
agent = SREServiceNowAgent()

async def create_incident(description, service, severity="MEDIUM"):
    """Create an incident quickly"""
    incident = await agent.respond_to_incident(
        description=description,
        service=service,
        severity=severity
    )
    print(f"✅ Created incident {incident['incident_id']}")
    print(f"   ServiceNow #: {incident['servicenow_number']}")
    return incident['incident_id']

async def resolve_incident(incident_id, notes):
    """Resolve an incident"""
    result = await agent.update_incident_status(
        incident_id=incident_id,
        status="resolved",
        notes=notes
    )
    print(f"✅ Resolved incident {incident_id}")

async def check_slo_health():
    """Quick SLO health check"""
    print("\n📊 SLO Health Check:")
    for slo in ["availability", "latency", "error_rate"]:
        budget = await agent.calculate_error_budget(slo)
        status = "🟢" if budget['status'] == "healthy" else "🟡" if budget['status'] == "at_risk" else "🔴"
        print(f"{status} {slo}: {budget['error_budget']['remaining']} budget remaining")

async def monitor_service(service_name):
    """Quick service health check"""
    health = await agent.analyze_service_health(service_name)
    print(f"\n🏥 {service_name} Health: {health['overall_health']}")
    if health['recommendations']:
        print("Recommendations:")
        for rec in health['recommendations']:
            print(f"  • {rec}")

# Example 1: Simple incident creation
async def example_simple_incident():
    print("\n📝 Example 1: Simple Incident Creation")
    print("-"*40)
    
    incident_id = await create_incident(
        "Database slow queries detected",
        "database-service",
        "HIGH"
    )
    
    # Do some work...
    await asyncio.sleep(2)
    
    await resolve_incident(incident_id, "Optimized queries and added indexes")

# Example 2: Complete incident workflow
async def example_incident_with_runbook():
    print("\n🔧 Example 2: Incident with Runbook")
    print("-"*40)
    
    # Create incident
    incident = await agent.respond_to_incident(
        description="High memory usage on production servers",
        service="web-service",
        severity="HIGH",
        symptoms=["Memory usage > 90%", "Swap usage increasing"]
    )
    
    # Execute runbook
    runbook = await agent.execute_runbook(
        "high_latency",
        incident_id=incident['incident_id']
    )
    print(f"✅ Executed {runbook['steps_executed']} runbook steps")
    
    # Resolve
    await agent.update_incident_status(
        incident_id=incident['incident_id'],
        status="resolved",
        notes="Memory leak fixed, services restarted"
    )

# Example 3: Proactive monitoring
async def example_proactive_monitoring():
    print("\n👀 Example 3: Proactive Monitoring")
    print("-"*40)
    
    services = ["api-gateway", "database-service", "cache-service"]
    
    for service in services:
        await monitor_service(service)
    
    await check_slo_health()

# Example 4: Incident with RCA
async def example_incident_with_rca():
    print("\n🔍 Example 4: Incident with Root Cause Analysis")
    print("-"*40)
    
    # Create incident
    incident = await agent.respond_to_incident(
        description="Payment processing failures",
        service="payment-service",
        severity="CRITICAL",
        symptoms=["Transaction timeouts", "Payment gateway errors"]
    )
    
    incident_id = incident['incident_id']
    
    # Resolve incident
    await agent.update_incident_status(
        incident_id=incident_id,
        status="resolved",
        notes="Payment gateway connection restored"
    )
    
    # Perform RCA
    rca = await agent.perform_rca(
        incident_id=incident_id,
        root_cause="Payment gateway API rate limit exceeded",
        contributing_factors=[
            "No rate limiting on our side",
            "Sudden spike in transactions",
            "No circuit breaker pattern implemented"
        ],
        timeline=[
            {"time": "10:00", "description": "Flash sale started"},
            {"time": "10:05", "description": "Transaction volume increased 500%"},
            {"time": "10:10", "description": "Rate limit errors started"},
            {"time": "10:12", "description": "Payment failures reported"},
            {"time": "10:30", "description": "Rate limiting implemented"},
            {"time": "10:35", "description": "Service restored"}
        ]
    )
    print(f"✅ RCA completed with {rca['action_items']} action items")

# Main script with all examples
async def main():
    print("🚀 SRE Agent Simple Script Examples")
    print("="*60)
    
    # Run examples
    await example_simple_incident()
    await example_incident_with_runbook()
    await example_proactive_monitoring()
    await example_incident_with_rca()
    
    print("\n✅ All examples completed!")

# One-liner examples for quick use
async def quick_start():
    """Super simple one-liners"""
    
    # Create a critical incident
    incident_id = await create_incident("Service down!", "api-gateway", "CRITICAL")
    
    # Check SLOs
    await check_slo_health()
    
    # Monitor a service
    await monitor_service("database-service")
    
    # Resolve the incident
    await resolve_incident(incident_id, "Service restarted")

if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
    
    # Or just run quick start
    # asyncio.run(quick_start())
    
    # Or run individual examples:
    # asyncio.run(example_simple_incident())
    # asyncio.run(check_slo_health())
    # asyncio.run(monitor_service("api-gateway"))
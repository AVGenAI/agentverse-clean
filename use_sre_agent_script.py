#!/usr/bin/env python3
"""
Script to Use SRE ServiceNow Agent
Shows how to use the agent programmatically to manage incidents
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# Import the SRE agent
from sre_servicenow_agent_fixed import SREServiceNowAgent

# For real ServiceNow integration
import aiohttp
from servicenow_config_loader import load_servicenow_config

class SREAgentScript:
    """Script to interact with SRE ServiceNow Agent"""
    
    def __init__(self):
        self.agent = SREServiceNowAgent()
        self.servicenow_config = load_servicenow_config()
    
    async def create_incident_workflow(self):
        """Complete incident management workflow"""
        print("\n🚨 INCIDENT MANAGEMENT WORKFLOW")
        print("="*60)
        
        # Step 1: Create an incident
        print("\n1️⃣ Creating incident...")
        incident = await self.agent.respond_to_incident(
            description="Database connection pool exhausted - applications timing out",
            service="database-service",
            severity="HIGH",
            symptoms=[
                "Connection timeout errors",
                "Application response time > 10s",
                "Database CPU at 95%"
            ],
            detection_source="monitoring-alert"
        )
        
        incident_id = incident['incident_id']
        print(f"✅ Incident created: {incident_id}")
        print(f"   ServiceNow #: {incident['servicenow_number']}")
        print(f"   Severity: {incident['severity']}")
        print(f"   Initial Actions: {json.dumps(incident['initial_actions'], indent=2)}")
        
        # Step 2: Check SLO impact
        print("\n2️⃣ Checking SLO impact...")
        slo_check = await self.agent.calculate_error_budget("availability")
        print(f"   Error Budget Remaining: {slo_check['error_budget']['remaining']}")
        print(f"   Status: {slo_check['status']}")
        
        # Step 3: Execute runbook
        print("\n3️⃣ Executing runbook...")
        runbook_result = await self.agent.execute_runbook(
            "database_outage",
            incident_id=incident_id,
            parameters={"scale_factor": 2, "enable_read_replica": True}
        )
        print(f"✅ Runbook executed: {runbook_result['runbook']}")
        for i, step in enumerate(runbook_result['execution_log'], 1):
            print(f"   Step {i}: {step['description']} - {step['status']}")
        
        # Step 4: Update incident
        print("\n4️⃣ Updating incident status...")
        update = await self.agent.update_incident_status(
            incident_id=incident_id,
            status="in_progress",
            notes="Runbook executed successfully. Monitoring recovery.",
            actions_taken=[
                "Increased connection pool size",
                "Enabled read replicas",
                "Cleared stale connections"
            ]
        )
        print(f"✅ Status updated to: {update['status']}")
        
        # Step 5: Resolve incident
        await asyncio.sleep(1)  # Simulate some work
        print("\n5️⃣ Resolving incident...")
        resolution = await self.agent.update_incident_status(
            incident_id=incident_id,
            status="resolved",
            notes="Database connections restored. Performance back to normal.",
            actions_taken=["Verified metrics", "Confirmed user access restored"]
        )
        print(f"✅ Incident resolved")
        print(f"   Total Duration: {resolution['duration']}")
        
        # Step 6: Perform RCA
        print("\n6️⃣ Performing root cause analysis...")
        rca = await self.agent.perform_rca(
            incident_id=incident_id,
            contributing_factors=[
                "Sudden traffic spike from marketing campaign",
                "Connection pool size not auto-scaling",
                "No alerts configured for connection pool usage"
            ],
            root_cause="Connection pool exhausted due to unexpected traffic spike",
            timeline=[
                {"time": "14:00", "description": "Marketing campaign launched"},
                {"time": "14:15", "description": "Traffic increased 300%"},
                {"time": "14:20", "description": "Connection pool reached limit"},
                {"time": "14:22", "description": "Applications started timing out"},
                {"time": "14:25", "description": "Incident declared"},
                {"time": "14:40", "description": "Runbook executed"},
                {"time": "14:45", "description": "Service restored"}
            ]
        )
        print(f"✅ RCA completed")
        print(f"   Root Cause: {rca['root_cause']}")
        print(f"   Action Items: {rca['action_items']}")
        
        return incident_id
    
    async def monitor_service_health(self, service_name: str):
        """Monitor service health"""
        print(f"\n📊 MONITORING SERVICE: {service_name}")
        print("="*60)
        
        health = await self.agent.analyze_service_health(
            service_name=service_name,
            metrics=["availability", "latency", "error_rate", "throughput"]
        )
        
        print(f"Overall Health: {health['overall_health']}")
        print(f"SLO Compliance: {'✅' if health['slo_compliance'] else '❌'}")
        print(f"Active Incidents: {health['active_incidents']}")
        
        print("\nMetrics:")
        for metric, data in health['metrics'].items():
            print(f"\n{metric.upper()}:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        
        if health['recommendations']:
            print("\nRecommendations:")
            for rec in health['recommendations']:
                print(f"  • {rec}")
    
    async def create_real_servicenow_incident(self):
        """Create a real incident in ServiceNow"""
        print("\n🎫 CREATING REAL SERVICENOW INCIDENT")
        print("="*60)
        
        if not self.servicenow_config.is_configured:
            print("❌ ServiceNow not configured. Please check your .env file")
            return
        
        # Prepare incident data
        incident_data = {
            "short_description": "Test incident from SRE Agent Script",
            "description": "This is a test incident created by the SRE ServiceNow Agent automation script",
            "urgency": "3",  # Low
            "impact": "3",   # Low
            "category": "Software",
            "subcategory": "Application",
            "assignment_group": "Service Desk",
            "caller_id": "admin"
        }
        
        # Create incident via ServiceNow API
        headers = self.servicenow_config.get_auth_headers()
        url = f"{self.servicenow_config.api_endpoint}/table/incident"
        
        print(f"Connecting to: {self.servicenow_config.instance_url}")
        print(f"Creating incident with data:")
        print(json.dumps(incident_data, indent=2))
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=incident_data, headers=headers, ssl=True) as response:
                    if response.status == 201:
                        result = await response.json()
                        incident = result.get('result', {})
                        print(f"\n✅ Real ServiceNow incident created!")
                        print(f"   Number: {incident.get('number')}")
                        print(f"   Sys ID: {incident.get('sys_id')}")
                        print(f"   State: {incident.get('state')}")
                        print(f"   View at: {self.servicenow_config.instance_url}/nav_to.do?uri=incident.do?sys_id={incident.get('sys_id')}")
                        return incident
                    else:
                        print(f"❌ Failed to create incident: {response.status}")
                        print(await response.text())
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def bulk_incident_operations(self):
        """Demonstrate bulk incident operations"""
        print("\n📦 BULK INCIDENT OPERATIONS")
        print("="*60)
        
        incidents = []
        
        # Create multiple incidents
        print("Creating multiple incidents...")
        for i in range(3):
            incident = await self.agent.respond_to_incident(
                description=f"Test incident {i+1} for bulk operations",
                service=["web-service", "api-service", "database-service"][i],
                severity=["LOW", "MEDIUM", "HIGH"][i],
                symptoms=[f"Test symptom {i+1}"]
            )
            incidents.append(incident)
            print(f"  Created: {incident['incident_id']} - {incident['service']}")
        
        # Check all SLOs
        print("\nChecking all SLOs...")
        for slo_name in ["availability", "latency", "error_rate"]:
            budget = await self.agent.calculate_error_budget(slo_name)
            print(f"  {slo_name}: {budget['error_budget']['remaining']} remaining")
        
        # Update all incidents
        print("\nUpdating all incidents...")
        for incident in incidents:
            await self.agent.update_incident_status(
                incident_id=incident['incident_id'],
                status="resolved",
                notes="Bulk resolution test"
            )
            print(f"  Resolved: {incident['incident_id']}")

async def main():
    """Main function to run the script"""
    script = SREAgentScript()
    
    print("🤖 SRE ServiceNow Agent Script")
    print("This script demonstrates how to use the SRE agent programmatically")
    
    # Menu
    while True:
        print("\n" + "="*60)
        print("Choose an operation:")
        print("1. Run complete incident workflow")
        print("2. Monitor service health")
        print("3. Create real ServiceNow incident")
        print("4. Run bulk operations demo")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == "1":
            await script.create_incident_workflow()
        elif choice == "2":
            service = input("Enter service name (e.g., api-gateway): ")
            await script.monitor_service_health(service or "api-gateway")
        elif choice == "3":
            await script.create_real_servicenow_incident()
        elif choice == "4":
            await script.bulk_incident_operations()
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# Quick start examples
async def quick_incident_example():
    """Quick example: Create and resolve an incident"""
    agent = SREServiceNowAgent()
    
    # Create incident
    incident = await agent.respond_to_incident(
        description="API latency spike detected",
        service="api-gateway",
        severity="HIGH",
        symptoms=["Response time > 5s", "Queue depth increasing"]
    )
    print(f"Created incident: {incident['incident_id']}")
    
    # Resolve it
    await agent.update_incident_status(
        incident_id=incident['incident_id'],
        status="resolved",
        notes="Auto-scaling kicked in, latency normalized"
    )
    print("Incident resolved!")

async def quick_slo_check():
    """Quick example: Check SLO status"""
    agent = SREServiceNowAgent()
    
    for slo in ["availability", "latency", "error_rate"]:
        budget = await agent.calculate_error_budget(slo)
        print(f"{slo}: {budget['error_budget']['remaining']} budget remaining")

if __name__ == "__main__":
    # Run interactive menu
    asyncio.run(main())
    
    # Or run quick examples:
    # asyncio.run(quick_incident_example())
    # asyncio.run(quick_slo_check())
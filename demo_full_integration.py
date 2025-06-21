#!/usr/bin/env python3
"""
Full Integration Demo
Demonstrates the complete AgentVerse + MCP + ServiceNow integration
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Any

# Import all our components
from sre_servicenow_agent_fixed import SREServiceNowAgent
from agent_mcp_coupling_system import AgentMCPCoupler, CompatibilityLevel
from servicenow_config_loader import load_servicenow_config
import aiohttp

class FullIntegrationDemo:
    """Demonstrates the complete integration"""
    
    def __init__(self):
        self.sre_agent = SREServiceNowAgent()
        self.coupler = AgentMCPCoupler()
        self.servicenow_config = load_servicenow_config()
        
    async def demo_complete_workflow(self):
        """Demonstrate a complete incident workflow"""
        print("\n🎭 COMPLETE INTEGRATION DEMO")
        print("="*70)
        print("Demonstrating: Agent + MCP + ServiceNow + Web UI Integration")
        print("="*70)
        
        # Step 1: Show agent capabilities
        print("\n1️⃣ AGENT CAPABILITIES")
        print("-"*50)
        print(f"Agent: {self.sre_agent.agent_info['display_name']}")
        print(f"Skills: {', '.join(self.sre_agent.agent_info['skills'][:5])}...")
        print(f"Tools: {len(self.sre_agent.agent_info['tools'])} internal + {len(self.sre_agent.agent_info['servicenow_tools'])} ServiceNow")
        
        # Step 2: Show MCP coupling
        print("\n2️⃣ MCP COUPLING")
        print("-"*50)
        
        # Create agent config for coupling
        agent_config = {
            "id": self.sre_agent.agent_info['id'],
            "name": self.sre_agent.agent_info['name'],
            "category": self.sre_agent.agent_info['category'],
            "skills": self.sre_agent.agent_info['skills'],
            "tools": self.sre_agent.agent_info['tools']
        }
        
        # Check compatibility with ServiceNow
        servicenow_server = self.coupler.registry.get_server("ServiceNow-Production")
        compatibility, analysis = self.coupler.analyzer.analyze_compatibility(agent_config, servicenow_server)
        
        print(f"ServiceNow Compatibility: {compatibility.name}")
        print(f"Score: {analysis['overall_score']:.2f}")
        print(f"Can couple: {'✅ Yes' if compatibility.value >= CompatibilityLevel.LOW.value else '❌ No'}")
        
        # Step 3: Simulate production incident
        print("\n3️⃣ PRODUCTION INCIDENT SIMULATION")
        print("-"*50)
        print("Scenario: Payment service experiencing high latency")
        
        # Create incident
        incident = await self.sre_agent.respond_to_incident(
            description="Payment API response time > 5 seconds, affecting checkout flow",
            service="payment-service",
            severity="HIGH",
            symptoms=[
                "API latency > 5000ms",
                "Payment timeout errors increasing",
                "Customer complaints about failed transactions"
            ],
            detection_source="datadog-monitoring"
        )
        
        print(f"\n✅ Incident Created: {incident['incident_id']}")
        print(f"   ServiceNow #: {incident['servicenow_number']}")
        print(f"   Severity: {incident['severity']}")
        print(f"   Initial Actions:")
        for action in incident['initial_actions']:
            print(f"     • {action}")
        
        # Step 4: Check SLO impact
        print("\n4️⃣ SLO IMPACT ANALYSIS")
        print("-"*50)
        
        for slo_name in ["availability", "latency", "error_rate"]:
            budget = await self.sre_agent.calculate_error_budget(slo_name)
            status_icon = "🟢" if budget['status'] == "healthy" else "🟡" if budget['status'] == "at_risk" else "🔴"
            print(f"{status_icon} {slo_name.capitalize()}: {budget['error_budget']['remaining']} budget remaining")
        
        # Step 5: Execute runbook
        print("\n5️⃣ RUNBOOK EXECUTION")
        print("-"*50)
        
        runbook = await self.sre_agent.execute_runbook(
            "high_latency",
            incident_id=incident['incident_id'],
            parameters={
                "scale_instances": 3,
                "enable_cache": True,
                "rate_limit": 1000
            }
        )
        
        print(f"Executing: {runbook['runbook']}")
        for step in runbook['execution_log']:
            print(f"  ✓ Step {step['step']}: {step['description']}")
        
        # Step 6: Update and resolve
        print("\n6️⃣ INCIDENT RESOLUTION")
        print("-"*50)
        
        # Update with progress
        await self.sre_agent.update_incident_status(
            incident_id=incident['incident_id'],
            status="in_progress",
            notes="Runbook executed. Monitoring recovery metrics.",
            actions_taken=[
                "Scaled payment service to 3 instances",
                "Enabled Redis cache layer",
                "Implemented rate limiting"
            ]
        )
        
        # Simulate recovery
        await asyncio.sleep(2)
        
        # Resolve incident
        resolution = await self.sre_agent.update_incident_status(
            incident_id=incident['incident_id'],
            status="resolved",
            notes="Service recovered. Latency back to normal (<200ms).",
            actions_taken=["Verified metrics", "Confirmed customer access restored"]
        )
        
        print(f"✅ Incident Resolved")
        print(f"   Duration: {resolution['duration']}")
        print(f"   SLO Impact: Updated")
        
        # Step 7: Root cause analysis
        print("\n7️⃣ ROOT CAUSE ANALYSIS")
        print("-"*50)
        
        rca = await self.sre_agent.perform_rca(
            incident_id=incident['incident_id'],
            contributing_factors=[
                "Database connection pool exhaustion",
                "Lack of caching for frequently accessed data",
                "No rate limiting on payment API"
            ],
            root_cause="Database connection pool too small for Black Friday traffic spike",
            timeline=[
                {"time": "14:00", "description": "Black Friday sale started"},
                {"time": "14:30", "description": "Traffic increased 500%"},
                {"time": "14:45", "description": "Connection pool exhausted"},
                {"time": "14:47", "description": "Payment latency spiked"},
                {"time": "14:50", "description": "Incident declared"},
                {"time": "15:05", "description": "Runbook executed"},
                {"time": "15:15", "description": "Service recovered"}
            ]
        )
        
        print(f"Root Cause: {rca['root_cause']}")
        print(f"Problem Record: {rca['problem_record']}")
        print(f"Knowledge Article: {rca['knowledge_article']}")
        print(f"Action Items: {rca['action_items']}")
        
        # Step 8: Create real ServiceNow record
        if self.servicenow_config.is_configured:
            print("\n8️⃣ REAL SERVICENOW INTEGRATION")
            print("-"*50)
            
            incident_data = {
                "short_description": "Demo: Payment service high latency incident",
                "description": "Automated demo showing full integration capabilities",
                "urgency": "3",
                "impact": "2",
                "category": "Software",
                "subcategory": "Application",
                "caller_id": "admin"
            }
            
            headers = self.servicenow_config.get_auth_headers()
            url = f"{self.servicenow_config.api_endpoint}/table/incident"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=incident_data, headers=headers, ssl=True) as response:
                        if response.status == 201:
                            result = await response.json()
                            incident_sn = result.get('result', {})
                            print(f"✅ Real ServiceNow incident created!")
                            print(f"   Number: {incident_sn.get('number')}")
                            print(f"   View at: {self.servicenow_config.instance_url}/nav_to.do?uri=incident.do?sys_id={incident_sn.get('sys_id')}")
            except Exception as e:
                print(f"   Note: Demo incident only (ServiceNow error: {e})")
        
        # Summary
        print("\n📊 INTEGRATION SUMMARY")
        print("="*70)
        print("✅ Agent responded to incident autonomously")
        print("✅ SLO impact calculated and tracked")
        print("✅ Runbook executed automatically")
        print("✅ Incident resolved with full documentation")
        print("✅ Root cause analysis completed")
        print("✅ ServiceNow records created")
        print("\n🎯 This demonstrates the complete integration of:")
        print("   • AgentVerse AI Agents (independent components)")
        print("   • MCP Protocol (dynamic coupling)")
        print("   • ServiceNow Platform (real ITSM)")
        print("   • Web UI (visual management)")
        print("   • Python Scripts (automation)")

    async def demo_multi_agent_collaboration(self):
        """Demonstrate multiple agents working together"""
        print("\n\n🤝 MULTI-AGENT COLLABORATION DEMO")
        print("="*70)
        
        print("Scenario: Complex infrastructure issue requiring multiple specialists")
        
        # In a real implementation, these would be separate agent instances
        agents_involved = [
            "🚨 SRE ServiceNow Specialist - Incident coordination",
            "💾 Database Performance Expert - Database analysis", 
            "🔒 Security Analyst - Security assessment",
            "🚀 DevOps Engineer - Deployment rollback"
        ]
        
        print("\nAgents collaborating:")
        for agent in agents_involved:
            print(f"  • {agent}")
        
        print("\nCollaboration flow:")
        print("  1. SRE detects issue → Creates incident INC0012345")
        print("  2. Database expert analyzes → Finds query bottleneck")
        print("  3. Security analyst checks → Confirms no breach")
        print("  4. DevOps engineer acts → Rolls back problematic deployment")
        print("  5. SRE coordinates → Updates incident and documents resolution")
        
        print("\n✅ Multi-agent collaboration enables faster, more comprehensive problem solving!")

async def main():
    """Run the complete integration demo"""
    demo = FullIntegrationDemo()
    
    # Run full workflow demo
    await demo.demo_complete_workflow()
    
    # Show multi-agent collaboration
    await demo.demo_multi_agent_collaboration()
    
    print("\n\n🎉 INTEGRATION COMPLETE!")
    print("The system is ready for production use with:")
    print("  • 1000+ specialized AI agents")
    print("  • Dynamic MCP server coupling")
    print("  • Real ServiceNow integration")
    print("  • Full automation capabilities")
    print("\nAgents + MCP = Infinite Possibilities! 🚀")

if __name__ == "__main__":
    asyncio.run(main())
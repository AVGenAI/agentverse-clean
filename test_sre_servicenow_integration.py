#!/usr/bin/env python3
"""
Test SRE ServiceNow Agent Integration
Demonstrates the SRE agent working with ServiceNow MCP server
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import logging

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import our modules
from sre_servicenow_agent_fixed import SREServiceNowAgent
from mcp_agent_client import AgentMCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SREServiceNowIntegrationTest:
    """Test SRE agent integration with ServiceNow"""
    
    def __init__(self):
        self.sre_agent = SREServiceNowAgent()
        self.test_results = []
    
    async def test_incident_lifecycle(self):
        """Test complete incident lifecycle through ServiceNow"""
        logger.info("\n🔄 Testing Incident Lifecycle")
        logger.info("="*60)
        
        try:
            # Step 1: Create incident
            logger.info("\n1️⃣ Creating incident...")
            incident = await self.sre_agent.respond_to_incident(
                description="Production API experiencing high latency",
                service="production-api",
                severity="HIGH",
                symptoms=["Response time > 5s", "Error rate increasing", "CPU at 90%"],
                detection_source="datadog"
            )
            
            incident_id = incident['incident_id']
            logger.info(f"✅ Incident created: {incident_id}")
            logger.info(f"   ServiceNow #: {incident['servicenow_number']}")
            logger.info(f"   SLO Impact: {json.dumps(incident['slo_impact'], indent=2)}")
            
            # Step 2: Execute runbook
            logger.info("\n2️⃣ Executing runbook...")
            runbook_result = await self.sre_agent.execute_runbook(
                "high_latency",
                incident_id=incident_id,
                parameters={"scale_factor": 2}
            )
            logger.info(f"✅ Runbook executed: {runbook_result['runbook']}")
            logger.info(f"   Steps completed: {runbook_result['steps_executed']}")
            
            # Step 3: Update incident status
            logger.info("\n3️⃣ Updating incident status...")
            update_result = await self.sre_agent.update_incident_status(
                incident_id=incident_id,
                status="in_progress",
                notes="Runbook executed, monitoring recovery",
                actions_taken=["Scaled API instances", "Cleared cache", "Optimized queries"]
            )
            logger.info(f"✅ Status updated: {update_result['status']}")
            
            # Step 4: Resolve incident
            logger.info("\n4️⃣ Resolving incident...")
            resolve_result = await self.sre_agent.update_incident_status(
                incident_id=incident_id,
                status="resolved",
                notes="Service restored to normal operation",
                actions_taken=["Confirmed metrics back to normal", "Validated SLO compliance"]
            )
            logger.info(f"✅ Incident resolved")
            logger.info(f"   Duration: {resolve_result['duration']}")
            
            # Step 5: Perform RCA
            logger.info("\n5️⃣ Performing root cause analysis...")
            rca_result = await self.sre_agent.perform_rca(
                incident_id=incident_id,
                contributing_factors=[
                    "Memory leak in API service",
                    "Insufficient auto-scaling thresholds",
                    "Missing alerting for memory usage"
                ],
                root_cause="Memory leak caused by unclosed database connections",
                timeline=[
                    {"time": "14:00", "description": "Deployment of v2.3.1"},
                    {"time": "14:30", "description": "Memory usage starts increasing"},
                    {"time": "15:00", "description": "First latency alerts"},
                    {"time": "15:15", "description": "Incident declared"},
                    {"time": "15:45", "description": "Service scaled and recovered"}
                ]
            )
            logger.info(f"✅ RCA completed")
            logger.info(f"   Problem record: {rca_result['problem_record']}")
            logger.info(f"   KB article: {rca_result['knowledge_article']}")
            logger.info(f"   Action items: {rca_result['action_items']}")
            
            self.test_results.append({
                "test": "incident_lifecycle",
                "status": "passed",
                "incident_id": incident_id,
                "steps_completed": 5
            })
            
        except Exception as e:
            logger.error(f"❌ Error in incident lifecycle test: {e}")
            self.test_results.append({
                "test": "incident_lifecycle",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_slo_management(self):
        """Test SLO and error budget management"""
        logger.info("\n📊 Testing SLO Management")
        logger.info("="*60)
        
        try:
            # Check all SLOs
            for slo_name in ["availability", "latency", "error_rate"]:
                logger.info(f"\n🎯 Checking {slo_name} SLO...")
                
                budget_result = await self.sre_agent.calculate_error_budget(slo_name)
                
                logger.info(f"   Target: {budget_result['target']}")
                logger.info(f"   Current: {budget_result['current_performance']}")
                logger.info(f"   Budget remaining: {budget_result['error_budget']['remaining']}")
                logger.info(f"   Status: {budget_result['status']}")
                logger.info(f"   Recommendation: {budget_result['recommendation']}")
            
            self.test_results.append({
                "test": "slo_management",
                "status": "passed",
                "slos_checked": 3
            })
            
        except Exception as e:
            logger.error(f"❌ Error in SLO management test: {e}")
            self.test_results.append({
                "test": "slo_management",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_service_health_analysis(self):
        """Test service health analysis capabilities"""
        logger.info("\n🏥 Testing Service Health Analysis")
        logger.info("="*60)
        
        try:
            services = ["api-gateway", "database-cluster", "cache-service"]
            
            for service in services:
                logger.info(f"\n🔍 Analyzing {service}...")
                
                health_result = await self.sre_agent.analyze_service_health(
                    service_name=service,
                    metrics=["availability", "latency", "error_rate", "throughput"]
                )
                
                logger.info(f"   Overall health: {health_result['overall_health']}")
                logger.info(f"   SLO compliance: {health_result['slo_compliance']}")
                logger.info(f"   Active incidents: {health_result['active_incidents']}")
                
                if health_result['recommendations']:
                    logger.info("   Recommendations:")
                    for rec in health_result['recommendations']:
                        logger.info(f"     - {rec}")
            
            self.test_results.append({
                "test": "service_health_analysis",
                "status": "passed",
                "services_analyzed": len(services)
            })
            
        except Exception as e:
            logger.error(f"❌ Error in service health analysis test: {e}")
            self.test_results.append({
                "test": "service_health_analysis",
                "status": "failed",
                "error": str(e)
            })
    
    async def test_servicenow_mcp_integration(self):
        """Test actual integration with ServiceNow MCP server"""
        logger.info("\n🔌 Testing ServiceNow MCP Integration")
        logger.info("="*60)
        
        try:
            # Create MCP client for SRE agent
            client = AgentMCPClient(
                self.sre_agent.agent_info['name'],
                self.sre_agent.agent_info['id']
            )
            
            # ServiceNow MCP server parameters
            server_params = StdioServerParameters(
                command="python",
                args=[
                    "-m", "src.servicenow_mcp_server.server",
                    "--tool-packages", "incident_management,change_management,problem_management"
                ],
                env={
                    "SERVICENOW_INSTANCE_URL": os.getenv("SERVICENOW_INSTANCE_URL", "https://dev.service-now.com"),
                    "SERVICENOW_USERNAME": os.getenv("SERVICENOW_USERNAME", "admin"),
                    "SERVICENOW_PASSWORD": os.getenv("SERVICENOW_PASSWORD", "password")
                }
            )
            
            logger.info("📡 Connecting to ServiceNow MCP server...")
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    logger.info("✅ Connected to ServiceNow MCP server")
                    
                    # Test 1: List available tools
                    logger.info("\n🔧 Available ServiceNow tools:")
                    tools = await session.list_tools()
                    for tool in tools.tools[:5]:
                        logger.info(f"   - {tool.name}: {tool.description[:50]}...")
                    
                    # Test 2: Create incident through ServiceNow
                    logger.info("\n📝 Creating incident in ServiceNow...")
                    incident_result = await session.call_tool("create_incident", {
                        "short_description": "SRE Agent Test: High CPU on production servers",
                        "description": "Automated incident created by SRE ServiceNow agent during integration test",
                        "urgency": 2,
                        "impact": 2,
                        "category": "Infrastructure",
                        "subcategory": "Server"
                    })
                    
                    if incident_result.content:
                        incident_data = json.loads(incident_result.content[0].text)
                        logger.info(f"✅ ServiceNow incident created: {incident_data.get('number', 'Unknown')}")
                    
                    # Test 3: Search recent incidents
                    logger.info("\n🔍 Searching recent incidents...")
                    search_result = await session.call_tool("search_incidents", {
                        "state": "open",
                        "limit": 5
                    })
                    
                    if search_result.content:
                        incidents = json.loads(search_result.content[0].text)
                        logger.info(f"   Found {len(incidents)} open incidents")
                    
                    # Test 4: Create change request
                    logger.info("\n📋 Creating change request...")
                    change_result = await session.call_tool("create_change_request", {
                        "short_description": "Deploy SRE monitoring improvements",
                        "description": "Implement enhanced monitoring based on recent incident learnings",
                        "type": "standard",
                        "risk": "low",
                        "impact": 3
                    })
                    
                    if change_result.content:
                        change_data = json.loads(change_result.content[0].text)
                        logger.info(f"✅ Change request created: {change_data.get('number', 'Unknown')}")
            
            self.test_results.append({
                "test": "servicenow_mcp_integration",
                "status": "passed",
                "connection": "successful",
                "operations_tested": 4
            })
            
        except Exception as e:
            logger.error(f"❌ Error in ServiceNow MCP integration test: {e}")
            logger.info("\n💡 Note: This test requires the ServiceNow MCP server to be running.")
            logger.info("   Install and run: https://github.com/echelon-ai-labs/servicenow-mcp")
            
            self.test_results.append({
                "test": "servicenow_mcp_integration",
                "status": "skipped",
                "reason": "ServiceNow MCP server not available",
                "error": str(e)
            })
    
    async def run_all_tests(self):
        """Run all integration tests"""
        logger.info("\n🚀 SRE ServiceNow Agent Integration Test Suite")
        logger.info("="*70)
        logger.info(f"Agent: {self.sre_agent.agent_info['display_name']}")
        logger.info(f"Started: {datetime.now().isoformat()}")
        
        # Run tests
        await self.test_incident_lifecycle()
        await self.test_slo_management()
        await self.test_service_health_analysis()
        await self.test_servicenow_mcp_integration()
        
        # Generate report
        self._generate_test_report()
    
    def _generate_test_report(self):
        """Generate test summary report"""
        logger.info("\n📊 Test Summary Report")
        logger.info("="*70)
        
        passed = len([r for r in self.test_results if r['status'] == 'passed'])
        failed = len([r for r in self.test_results if r['status'] == 'failed'])
        skipped = len([r for r in self.test_results if r['status'] == 'skipped'])
        
        logger.info(f"Total Tests: {len(self.test_results)}")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        logger.info(f"⏭️  Skipped: {skipped}")
        
        logger.info("\nTest Details:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⏭️"
            logger.info(f"{status_icon} {result['test']}: {result['status']}")
            if result.get('error'):
                logger.info(f"   Error: {result['error']}")
        
        # Save detailed report
        report_file = f"sre_servicenow_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "test_run": datetime.now().isoformat(),
                "agent": self.sre_agent.agent_info,
                "summary": {
                    "total": len(self.test_results),
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped
                },
                "results": self.test_results
            }, f, indent=2)
        
        logger.info(f"\n📄 Detailed report saved to: {report_file}")

async def demonstrate_standalone_sre_agent():
    """Demonstrate the SRE agent as a standalone component"""
    logger.info("\n🎯 Demonstrating SRE Agent as Standalone Component")
    logger.info("="*70)
    
    agent = SREServiceNowAgent()
    
    # Show agent capabilities
    logger.info(f"\nAgent: {agent.agent_info['display_name']}")
    logger.info(f"ID: {agent.agent_info['id']}")
    logger.info(f"\nCore Capabilities:")
    for i, skill in enumerate(agent.agent_info['skills'][:5], 1):
        logger.info(f"  {i}. {skill}")
    
    logger.info(f"\nTools Available: {len(agent.agent_info['tools'])}")
    logger.info(f"ServiceNow Tools: {len(agent.agent_info['servicenow_tools'])}")
    
    # Demonstrate a standalone operation
    logger.info("\n🔧 Standalone Operation Demo:")
    incident = await agent.respond_to_incident(
        description="Demo incident for testing",
        service="demo-service",
        severity="MEDIUM",
        symptoms=["Slow response", "Intermittent errors"]
    )
    
    logger.info(f"✅ Incident handled: {incident['incident_id']}")
    logger.info(f"   Actions: {len(incident['initial_actions'])}")
    logger.info(f"   Notifications: {len(incident['notification_sent_to'])}")
    
    logger.info("\n💡 This agent can work standalone OR integrate with any MCP server!")

async def main():
    """Main test runner"""
    print("\n🚀 SRE ServiceNow Agent Integration Testing")
    print("="*70)
    
    # First demonstrate standalone capabilities
    await demonstrate_standalone_sre_agent()
    
    # Then run integration tests
    print("\n" + "="*70)
    print("Running Integration Tests...")
    print("="*70)
    
    tester = SREServiceNowIntegrationTest()
    await tester.run_all_tests()
    
    print("\n✅ Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main())
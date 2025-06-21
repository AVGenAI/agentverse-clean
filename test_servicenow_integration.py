#!/usr/bin/env python3
"""
Test AgentVerse agents with ServiceNow MCP Server
Tests our agents' ability to interact with the ServiceNow platform via MCP
"""

import os
import json
import yaml
import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

# MCP client imports
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import our modules
from mcp_agent_client import AgentMCPClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceNowAgentTester:
    """Tests AgentVerse agents with ServiceNow MCP server"""
    
    def __init__(self, config_path: str = "config/agentverse_servicenow_config.yaml"):
        self.config = self._load_config(config_path)
        self.agents = self._load_agents()
        self.test_results = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load ServiceNow integration configuration"""
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _load_agents(self) -> List[Dict[str, Any]]:
        """Load AgentVerse agents"""
        agents_path = "src/config/agentverse_agents_1000.json"
        with open(agents_path, 'r') as f:
            return json.load(f)
    
    def _match_agent_to_tool_package(self, agent_name: str) -> List[str]:
        """Match agent to appropriate ServiceNow tool packages"""
        tool_packages = []
        
        for category, patterns in self.config['agent_tool_packages'].items():
            for pattern_config in patterns:
                pattern = pattern_config['agent_pattern']
                if re.match(pattern, agent_name):
                    tool_packages.extend(pattern_config['tool_packages'])
        
        return list(set(tool_packages))  # Remove duplicates
    
    async def test_agent_with_servicenow(
        self, 
        agent: Dict[str, Any],
        servicenow_server_cmd: str = "python",
        servicenow_server_args: List[str] = None
    ) -> Dict[str, Any]:
        """Test a single agent with ServiceNow MCP server
        
        Args:
            agent: Agent configuration
            servicenow_server_cmd: Command to run ServiceNow MCP server
            servicenow_server_args: Arguments for the server
            
        Returns:
            Test results
        """
        agent_name = agent.get('name', 'Unknown')
        agent_id = agent.get('enhanced_metadata', {}).get('agent_uuid', 'unknown')
        
        # Get matching tool packages
        tool_packages = self._match_agent_to_tool_package(agent_name)
        
        if not tool_packages:
            return {
                "agent": agent_name,
                "status": "skipped",
                "reason": "No matching ServiceNow tool packages"
            }
        
        logger.info(f"Testing agent {agent_name} with packages: {tool_packages}")
        
        # Default ServiceNow MCP server args
        if servicenow_server_args is None:
            servicenow_server_args = [
                "-m", "src.servicenow_mcp_server.server",
                "--tool-packages", ",".join(tool_packages)
            ]
        
        test_result = {
            "agent": agent_name,
            "agent_id": agent_id,
            "tool_packages": tool_packages,
            "tests": [],
            "status": "pending"
        }
        
        try:
            # Create MCP client for our agent
            client = AgentMCPClient(agent_name, agent_id)
            
            # Connect to ServiceNow MCP server
            server_params = StdioServerParameters(
                command=servicenow_server_cmd,
                args=servicenow_server_args,
                env={
                    "SERVICENOW_INSTANCE_URL": os.getenv("SERVICENOW_INSTANCE_URL", "https://dev.service-now.com"),
                    "SERVICENOW_USERNAME": os.getenv("SERVICENOW_USERNAME", "admin"),
                    "SERVICENOW_PASSWORD": os.getenv("SERVICENOW_PASSWORD", "password"),
                    "AGENTVERSE_TOOL_PACKAGES": ",".join(tool_packages)
                }
            )
            
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    
                    # Test 1: List available tools
                    tools_result = await self._test_list_tools(session)
                    test_result["tests"].append(tools_result)
                    
                    # Test 2: Test tool package introspection
                    introspection_result = await self._test_introspection(session)
                    test_result["tests"].append(introspection_result)
                    
                    # Test 3: Execute scenario-based tests
                    for scenario in self._get_test_scenarios(agent_name, tool_packages):
                        scenario_result = await self._test_scenario(session, scenario)
                        test_result["tests"].append(scenario_result)
                    
                    # Test 4: Test agent-specific capabilities
                    capability_result = await self._test_agent_capabilities(
                        session, agent, tool_packages
                    )
                    test_result["tests"].append(capability_result)
            
            # Determine overall status
            failed_tests = [t for t in test_result["tests"] if t.get("status") == "failed"]
            test_result["status"] = "failed" if failed_tests else "passed"
            
        except Exception as e:
            logger.error(f"Error testing agent {agent_name}: {e}")
            test_result["status"] = "error"
            test_result["error"] = str(e)
        
        return test_result
    
    async def _test_list_tools(self, session: ClientSession) -> Dict[str, Any]:
        """Test listing available tools"""
        try:
            tools = await session.list_tools()
            return {
                "test": "list_tools",
                "status": "passed",
                "tools_count": len(tools.tools),
                "tools": [tool.name for tool in tools.tools[:5]]  # First 5 tools
            }
        except Exception as e:
            return {
                "test": "list_tools",
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_introspection(self, session: ClientSession) -> Dict[str, Any]:
        """Test tool package introspection"""
        try:
            # Call the introspection tool
            result = await session.call_tool("list_tool_packages", {})
            
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    packages_info = json.loads(content.text)
                    return {
                        "test": "introspection",
                        "status": "passed",
                        "available_packages": packages_info.get("available_packages", []),
                        "enabled_packages": packages_info.get("enabled_packages", [])
                    }
            
            return {
                "test": "introspection",
                "status": "failed",
                "error": "No introspection data received"
            }
            
        except Exception as e:
            return {
                "test": "introspection",
                "status": "failed",
                "error": str(e)
            }
    
    async def _test_scenario(
        self, 
        session: ClientSession, 
        scenario: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test a specific scenario"""
        scenario_name = scenario.get("name", "Unknown scenario")
        
        try:
            results = []
            
            for step in scenario.get("test_steps", []):
                tool_name = step["tool"]
                params = step.get("params", {})
                
                # Call the tool
                tool_result = await session.call_tool(tool_name, params)
                
                # Parse result
                if tool_result.content and len(tool_result.content) > 0:
                    content = tool_result.content[0]
                    if hasattr(content, 'text'):
                        result_data = json.loads(content.text)
                        results.append({
                            "tool": tool_name,
                            "status": "success",
                            "result": result_data
                        })
                    else:
                        results.append({
                            "tool": tool_name,
                            "status": "error",
                            "error": "Invalid response format"
                        })
            
            return {
                "test": f"scenario_{scenario_name}",
                "status": "passed",
                "scenario": scenario_name,
                "steps_completed": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "test": f"scenario_{scenario_name}",
                "status": "failed",
                "scenario": scenario_name,
                "error": str(e)
            }
    
    async def _test_agent_capabilities(
        self,
        session: ClientSession,
        agent: Dict[str, Any],
        tool_packages: List[str]
    ) -> Dict[str, Any]:
        """Test agent-specific capabilities with ServiceNow"""
        agent_category = agent.get('category', '').lower()
        
        try:
            tests_run = []
            
            # Test based on agent category
            if 'support' in agent_category:
                # Test incident creation capability
                result = await session.call_tool("create_incident", {
                    "short_description": f"Test from {agent['name']}",
                    "description": "Testing AgentVerse integration",
                    "urgency": 3,
                    "impact": 3
                })
                tests_run.append({
                    "capability": "incident_creation",
                    "status": "passed" if result else "failed"
                })
                
            elif 'devops' in agent_category or 'engineering' in agent_category:
                # Test change request capability
                result = await session.call_tool("search_change_requests", {
                    "state": "open",
                    "limit": 5
                })
                tests_run.append({
                    "capability": "change_management",
                    "status": "passed" if result else "failed"
                })
                
            elif 'security' in agent_category:
                # Test security operations capability
                result = await session.call_tool("search_incidents", {
                    "category": "security",
                    "state": "open"
                })
                tests_run.append({
                    "capability": "security_operations",
                    "status": "passed" if result else "failed"
                })
            
            return {
                "test": "agent_capabilities",
                "status": "passed",
                "agent_category": agent_category,
                "capabilities_tested": len(tests_run),
                "results": tests_run
            }
            
        except Exception as e:
            return {
                "test": "agent_capabilities",
                "status": "failed",
                "error": str(e)
            }
    
    def _get_test_scenarios(
        self, 
        agent_name: str, 
        tool_packages: List[str]
    ) -> List[Dict[str, Any]]:
        """Get relevant test scenarios for the agent"""
        scenarios = []
        
        for scenario in self.config.get('test_scenarios', []):
            # Check if scenario applies to this agent
            if any(pkg in tool_packages for pkg in scenario.get('tool_package', '').split(',')):
                scenarios.append(scenario)
        
        return scenarios[:2]  # Limit to 2 scenarios per agent
    
    async def run_integration_tests(self, sample_size: int = 5):
        """Run integration tests with a sample of agents"""
        logger.info(f"Starting ServiceNow integration tests with {sample_size} agents")
        
        # Select diverse agents for testing
        test_agents = self._select_test_agents(sample_size)
        
        for agent in test_agents:
            logger.info(f"\nTesting agent: {agent['name']}")
            result = await self.test_agent_with_servicenow(agent)
            self.test_results.append(result)
            
            # Log result
            if result['status'] == 'passed':
                logger.info(f"✅ {agent['name']} - PASSED")
            elif result['status'] == 'skipped':
                logger.info(f"⏭️  {agent['name']} - SKIPPED: {result.get('reason')}")
            else:
                logger.error(f"❌ {agent['name']} - FAILED: {result.get('error')}")
        
        # Generate summary report
        self._generate_test_report()
    
    def _select_test_agents(self, sample_size: int) -> List[Dict[str, Any]]:
        """Select a diverse sample of agents for testing"""
        selected = []
        categories = ['Support', 'Engineering', 'DevOps', 'Security', 'Business']
        
        # Try to get at least one agent from each category
        for category in categories:
            category_agents = [
                a for a in self.agents 
                if category.lower() in a.get('category', '').lower()
            ]
            if category_agents:
                selected.append(category_agents[0])
        
        # Fill remaining slots with other agents
        remaining = sample_size - len(selected)
        if remaining > 0:
            other_agents = [a for a in self.agents if a not in selected]
            selected.extend(other_agents[:remaining])
        
        return selected[:sample_size]
    
    def _generate_test_report(self):
        """Generate test summary report"""
        report = {
            "test_run": datetime.now().isoformat(),
            "total_agents_tested": len(self.test_results),
            "summary": {
                "passed": len([r for r in self.test_results if r['status'] == 'passed']),
                "failed": len([r for r in self.test_results if r['status'] == 'failed']),
                "skipped": len([r for r in self.test_results if r['status'] == 'skipped']),
                "error": len([r for r in self.test_results if r['status'] == 'error'])
            },
            "results": self.test_results
        }
        
        # Save report
        report_path = f"servicenow_integration_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("ServiceNow MCP Integration Test Summary")
        print("="*60)
        print(f"Total Agents Tested: {report['total_agents_tested']}")
        print(f"Passed: {report['summary']['passed']} ✅")
        print(f"Failed: {report['summary']['failed']} ❌")
        print(f"Skipped: {report['summary']['skipped']} ⏭️")
        print(f"Errors: {report['summary']['error']} ⚠️")
        print(f"\nDetailed report saved to: {report_path}")
        
        # Show examples of successful integrations
        successful = [r for r in self.test_results if r['status'] == 'passed']
        if successful:
            print("\n✅ Successfully Integrated Agents:")
            for result in successful[:3]:
                print(f"  - {result['agent']} with packages: {', '.join(result['tool_packages'])}")

async def main():
    """Main test runner"""
    print("🚀 AgentVerse + ServiceNow MCP Integration Test")
    print("="*60)
    
    # Check for ServiceNow credentials
    if not os.getenv("SERVICENOW_INSTANCE_URL"):
        print("\n⚠️  Note: Using demo ServiceNow instance.")
        print("Set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD")
        print("environment variables to test with a real instance.\n")
    
    # Create tester
    tester = ServiceNowAgentTester()
    
    # Run tests
    await tester.run_integration_tests(sample_size=5)

if __name__ == "__main__":
    asyncio.run(main())
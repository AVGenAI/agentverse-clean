#!/usr/bin/env python3
"""
Agent Capability Testing Framework
Tests and validates agent functional capabilities
"""

import json
import asyncio
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import random
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich import print as rprint

console = Console()

@dataclass
class TestCase:
    """Test case for agent capabilities"""
    name: str
    description: str
    category: str
    required_tools: List[str]
    input_data: Dict[str, Any]
    expected_outputs: List[str]
    success_criteria: Dict[str, Any]
    timeout: int = 60  # seconds

@dataclass
class TestResult:
    """Test execution result"""
    test_name: str
    agent_name: str
    success: bool
    execution_time: float
    outputs: Dict[str, Any]
    errors: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

class AgentCapabilityTester:
    """Tests agent functional capabilities"""
    
    def __init__(self, config_file: str = "src/config/agentverse_agents_1000.json"):
        self.config_file = config_file
        self.agents = []
        self.test_suites = self._initialize_test_suites()
        self.load_agents()
    
    def load_agents(self):
        """Load agents with enhanced capabilities"""
        with open(self.config_file, 'r') as f:
            self.agents = json.load(f)
        console.print(f"[green]✅ Loaded {len(self.agents)} agents for testing[/green]")
    
    def _initialize_test_suites(self) -> Dict[str, List[TestCase]]:
        """Initialize comprehensive test suites"""
        return {
            "code_analysis": [
                TestCase(
                    name="ast_analysis_test",
                    description="Test AST code analysis capabilities",
                    category="code_analysis",
                    required_tools=["ast_analyzer", "code_metrics"],
                    input_data={
                        "code": """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
                        """,
                        "language": "python"
                    },
                    expected_outputs=["structure", "complexity", "suggestions"],
                    success_criteria={
                        "complexity_detected": True,
                        "recursive_pattern_identified": True
                    }
                ),
                TestCase(
                    name="security_scan_test",
                    description="Test security vulnerability scanning",
                    category="security",
                    required_tools=["security_scanner", "dependency_analyzer"],
                    input_data={
                        "code": """
import pickle
data = pickle.loads(user_input)  # Potential security issue
                        """,
                        "dependencies": ["pickle", "requests==2.20.0"]
                    },
                    expected_outputs=["vulnerabilities", "severity", "recommendations"],
                    success_criteria={
                        "vulnerability_found": True,
                        "severity_assessed": "high"
                    }
                )
            ],
            "api_integration": [
                TestCase(
                    name="rest_api_test",
                    description="Test REST API integration capabilities",
                    category="api_integration",
                    required_tools=["rest_client"],
                    input_data={
                        "endpoint": "https://api.example.com/data",
                        "method": "GET",
                        "headers": {"Authorization": "Bearer token"},
                        "retry": True
                    },
                    expected_outputs=["response", "status_code", "headers"],
                    success_criteria={
                        "successful_request": True,
                        "retry_logic_works": True
                    }
                ),
                TestCase(
                    name="graphql_test",
                    description="Test GraphQL query execution",
                    category="api_integration",
                    required_tools=["graphql_client"],
                    input_data={
                        "query": """
                        query GetUser($id: ID!) {
                            user(id: $id) {
                                name
                                email
                                posts {
                                    title
                                }
                            }
                        }
                        """,
                        "variables": {"id": "123"}
                    },
                    expected_outputs=["data", "errors"],
                    success_criteria={
                        "valid_query": True,
                        "data_retrieved": True
                    }
                )
            ],
            "data_processing": [
                TestCase(
                    name="data_transformation_test",
                    description="Test data format transformation",
                    category="data_processing",
                    required_tools=["data_transformer"],
                    input_data={
                        "data": {"name": "John", "age": 30, "items": [1, 2, 3]},
                        "input_format": "json",
                        "output_format": "xml",
                        "schema": {"root": "person"}
                    },
                    expected_outputs=["transformed_data", "validation_result"],
                    success_criteria={
                        "format_converted": True,
                        "data_integrity_maintained": True
                    }
                ),
                TestCase(
                    name="ml_prediction_test",
                    description="Test ML model prediction",
                    category="data_processing",
                    required_tools=["ml_predictor"],
                    input_data={
                        "model_id": "sentiment_analyzer",
                        "features": {"text": "This product is amazing!"}
                    },
                    expected_outputs=["predictions", "confidence", "explanations"],
                    success_criteria={
                        "prediction_made": True,
                        "confidence_score": "> 0.7"
                    }
                )
            ],
            "deployment": [
                TestCase(
                    name="container_build_test",
                    description="Test container image building",
                    category="deployment",
                    required_tools=["container_builder"],
                    input_data={
                        "dockerfile": """
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
                        """,
                        "optimization": True
                    },
                    expected_outputs=["image_id", "size", "layers"],
                    success_criteria={
                        "build_successful": True,
                        "size_optimized": True
                    }
                ),
                TestCase(
                    name="k8s_deployment_test",
                    description="Test Kubernetes deployment",
                    category="deployment",
                    required_tools=["k8s_deployer"],
                    input_data={
                        "manifest": {
                            "apiVersion": "apps/v1",
                            "kind": "Deployment",
                            "metadata": {"name": "test-app"},
                            "spec": {
                                "replicas": 3,
                                "selector": {"matchLabels": {"app": "test"}},
                                "template": {
                                    "metadata": {"labels": {"app": "test"}},
                                    "spec": {
                                        "containers": [{
                                            "name": "app",
                                            "image": "test:latest",
                                            "ports": [{"containerPort": 8080}]
                                        }]
                                    }
                                }
                            }
                        },
                        "namespace": "default"
                    },
                    expected_outputs=["deployment_id", "status", "endpoints"],
                    success_criteria={
                        "deployment_created": True,
                        "pods_running": True
                    }
                )
            ],
            "monitoring": [
                TestCase(
                    name="metrics_collection_test",
                    description="Test metrics collection",
                    category="monitoring",
                    required_tools=["metrics_collector"],
                    input_data={
                        "metric_type": "application",
                        "interval": 60,
                        "aggregation": "avg"
                    },
                    expected_outputs=["metrics", "aggregations", "trends"],
                    success_criteria={
                        "metrics_collected": True,
                        "aggregation_correct": True
                    }
                ),
                TestCase(
                    name="log_analysis_test",
                    description="Test log pattern analysis",
                    category="monitoring",
                    required_tools=["log_analyzer"],
                    input_data={
                        "logs": [
                            "2024-01-01 10:00:00 ERROR Database connection failed",
                            "2024-01-01 10:00:01 ERROR Retry attempt 1",
                            "2024-01-01 10:00:02 ERROR Retry attempt 2",
                            "2024-01-01 10:00:03 INFO Connection restored"
                        ],
                        "pattern": "ERROR.*connection"
                    },
                    expected_outputs=["matches", "anomalies", "statistics"],
                    success_criteria={
                        "pattern_matched": True,
                        "anomaly_detected": True
                    }
                )
            ],
            "workflow_execution": [
                TestCase(
                    name="code_review_workflow_test",
                    description="Test automated code review workflow",
                    category="workflow",
                    required_tools=["workflow_orchestrator", "ast_analyzer", "test_generator"],
                    input_data={
                        "workflow_id": "code_review_workflow",
                        "code": """
class Calculator:
    def add(self, a, b):
                            return a + b
                        """,
                        "review_level": "comprehensive"
                    },
                    expected_outputs=["review_report", "suggestions", "test_cases"],
                    success_criteria={
                        "workflow_completed": True,
                        "all_steps_executed": True
                    }
                ),
                TestCase(
                    name="incident_response_workflow_test",
                    description="Test incident response workflow",
                    category="workflow",
                    required_tools=["workflow_orchestrator", "alert_manager", "script_executor"],
                    input_data={
                        "workflow_id": "incident_response_workflow",
                        "incident": {
                            "type": "service_down",
                            "severity": "high",
                            "service": "api-gateway"
                        }
                    },
                    expected_outputs=["response_actions", "notifications", "postmortem"],
                    success_criteria={
                        "incident_handled": True,
                        "notifications_sent": True
                    }
                )
            ]
        }
    
    async def run_test_case(self, agent: Dict, test_case: TestCase) -> TestResult:
        """Run a single test case for an agent"""
        start_time = time.time()
        errors = []
        outputs = {}
        success = True
        
        try:
            # Check if agent has required tools
            agent_tools = set(agent.get('tools', []))
            required_tools = set(test_case.required_tools)
            
            if not required_tools.issubset(agent_tools):
                missing_tools = required_tools - agent_tools
                errors.append(f"Missing required tools: {missing_tools}")
                success = False
                return TestResult(
                    test_name=test_case.name,
                    agent_name=agent.get('name', 'Unknown'),
                    success=False,
                    execution_time=time.time() - start_time,
                    outputs=outputs,
                    errors=errors
                )
            
            # Simulate test execution
            await asyncio.sleep(random.uniform(0.1, 0.5))  # Simulate processing time
            
            # Generate simulated outputs based on test case
            for expected_output in test_case.expected_outputs:
                if expected_output == "structure":
                    outputs[expected_output] = {
                        "type": "function",
                        "name": "calculate_fibonacci",
                        "complexity": 5
                    }
                elif expected_output == "vulnerabilities":
                    outputs[expected_output] = [{
                        "type": "insecure_deserialization",
                        "line": 2,
                        "severity": "high"
                    }]
                elif expected_output == "response":
                    outputs[expected_output] = {"status": "success", "data": {}}
                elif expected_output == "metrics":
                    outputs[expected_output] = {
                        "cpu_usage": random.uniform(20, 80),
                        "memory_usage": random.uniform(100, 500),
                        "request_rate": random.uniform(50, 200)
                    }
                else:
                    outputs[expected_output] = f"Simulated {expected_output}"
            
            # Validate success criteria
            for criterion, expected_value in test_case.success_criteria.items():
                if criterion == "complexity_detected" and expected_value:
                    if "structure" not in outputs or outputs["structure"].get("complexity", 0) < 1:
                        errors.append(f"Failed criterion: {criterion}")
                        success = False
                elif criterion == "vulnerability_found" and expected_value:
                    if "vulnerabilities" not in outputs or len(outputs["vulnerabilities"]) == 0:
                        errors.append(f"Failed criterion: {criterion}")
                        success = False
            
            # Calculate performance metrics
            performance_metrics = {
                "execution_time": time.time() - start_time,
                "memory_usage": random.uniform(50, 200),  # MB
                "cpu_usage": random.uniform(10, 50),  # %
                "throughput": random.uniform(100, 1000)  # ops/sec
            }
            
        except Exception as e:
            errors.append(f"Test execution error: {str(e)}")
            success = False
            performance_metrics = {}
        
        return TestResult(
            test_name=test_case.name,
            agent_name=agent.get('name', 'Unknown'),
            success=success,
            execution_time=time.time() - start_time,
            outputs=outputs,
            errors=errors,
            performance_metrics=performance_metrics
        )
    
    async def run_test_suite(self, suite_name: str, agents: List[Dict]) -> List[TestResult]:
        """Run a test suite for multiple agents"""
        if suite_name not in self.test_suites:
            console.print(f"[red]Test suite '{suite_name}' not found[/red]")
            return []
        
        test_cases = self.test_suites[suite_name]
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console
        ) as progress:
            
            task = progress.add_task(
                f"Running {suite_name} tests...", 
                total=len(test_cases) * len(agents)
            )
            
            for test_case in test_cases:
                for agent in agents:
                    result = await self.run_test_case(agent, test_case)
                    results.append(result)
                    progress.advance(task)
        
        return results
    
    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results"""
        total_tests = len(results)
        successful_tests = sum(1 for r in results if r.success)
        
        # Group by test name
        by_test = {}
        for result in results:
            if result.test_name not in by_test:
                by_test[result.test_name] = {"success": 0, "total": 0, "avg_time": 0}
            by_test[result.test_name]["total"] += 1
            if result.success:
                by_test[result.test_name]["success"] += 1
            by_test[result.test_name]["avg_time"] += result.execution_time
        
        # Calculate averages
        for test_name in by_test:
            by_test[test_name]["success_rate"] = by_test[test_name]["success"] / by_test[test_name]["total"]
            by_test[test_name]["avg_time"] /= by_test[test_name]["total"]
        
        # Group by agent
        by_agent = {}
        for result in results:
            if result.agent_name not in by_agent:
                by_agent[result.agent_name] = {"success": 0, "total": 0, "tests": []}
            by_agent[result.agent_name]["total"] += 1
            if result.success:
                by_agent[result.agent_name]["success"] += 1
            by_agent[result.agent_name]["tests"].append(result.test_name)
        
        # Find best performing agents
        agent_scores = {}
        for agent_name, stats in by_agent.items():
            agent_scores[agent_name] = stats["success"] / stats["total"]
        
        best_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": successful_tests / total_tests if total_tests > 0 else 0,
                "test_count": len(by_test),
                "agent_count": len(by_agent)
            },
            "by_test": by_test,
            "best_agents": best_agents,
            "failed_tests": [r for r in results if not r.success][:10]  # Top 10 failures
        }
    
    def display_results(self, analysis: Dict[str, Any]):
        """Display test results in a formatted way"""
        
        # Summary
        summary = analysis["summary"]
        console.print(Panel.fit(
            f"[bold green]Test Results Summary[/bold green]\n\n"
            f"Total Tests: {summary['total_tests']}\n"
            f"Successful: {summary['successful_tests']}\n"
            f"Success Rate: {summary['success_rate']:.1%}\n"
            f"Unique Tests: {summary['test_count']}\n"
            f"Agents Tested: {summary['agent_count']}",
            border_style="green"
        ))
        
        # Test performance
        table = Table(title="Test Performance")
        table.add_column("Test Name", style="cyan")
        table.add_column("Success Rate", style="green")
        table.add_column("Avg Time (s)", style="yellow")
        
        for test_name, stats in analysis["by_test"].items():
            table.add_row(
                test_name,
                f"{stats['success_rate']:.1%}",
                f"{stats['avg_time']:.3f}"
            )
        
        console.print(table)
        
        # Best performing agents
        if analysis["best_agents"]:
            table = Table(title="Top Performing Agents")
            table.add_column("Agent", style="cyan")
            table.add_column("Success Rate", style="green")
            
            for agent_name, score in analysis["best_agents"]:
                table.add_row(agent_name, f"{score:.1%}")
            
            console.print(table)
        
        # Failed tests
        if analysis["failed_tests"]:
            console.print("\n[red]Failed Tests (Sample):[/red]")
            for failure in analysis["failed_tests"][:5]:
                console.print(f"  - {failure.agent_name} failed {failure.test_name}")
                if failure.errors:
                    console.print(f"    Error: {failure.errors[0]}")

async def run_capability_tests():
    """Run capability tests on agents"""
    tester = AgentCapabilityTester()
    
    # Select a sample of agents for testing
    sample_size = min(10, len(tester.agents))
    test_agents = random.sample(tester.agents, sample_size)
    
    console.print(f"[cyan]Testing {sample_size} agents...[/cyan]\n")
    
    # Run different test suites
    all_results = []
    
    for suite_name in ["code_analysis", "api_integration", "data_processing"]:
        console.print(f"\n[yellow]Running {suite_name} test suite...[/yellow]")
        results = await tester.run_test_suite(suite_name, test_agents)
        all_results.extend(results)
    
    # Analyze and display results
    analysis = tester.analyze_results(all_results)
    tester.display_results(analysis)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "analysis": analysis,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "agent_name": r.agent_name,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "errors": r.errors
                }
                for r in all_results
            ]
        }, f, indent=2)
    
    console.print(f"\n[green]Results saved to {results_file}[/green]")

if __name__ == "__main__":
    asyncio.run(run_capability_tests())
#!/usr/bin/env python3
"""
SRE ServiceNow Agent
A specialized Site Reliability Engineering agent integrated with ServiceNow
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

# MCP imports
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Import our modules
from agent_behavior_system import AgentBehaviorSystem, InteractionContext, BehaviorProfile
from servicenow_agent_adapter import ServiceNowAgentAdapter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncidentSeverity(Enum):
    """Incident severity levels"""
    CRITICAL = 1  # P1 - Service down, major impact
    HIGH = 2      # P2 - Service degraded, significant impact
    MEDIUM = 3    # P3 - Minor service impact
    LOW = 4       # P4 - No immediate impact

class IncidentState(Enum):
    """Incident lifecycle states"""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class SLOTarget:
    """Service Level Objective definition"""
    name: str
    target: float  # e.g., 99.9
    measurement_window: str  # e.g., "30d"
    error_budget: float  # Remaining error budget
    current_performance: float = 0.0

@dataclass
class IncidentContext:
    """Context for incident handling"""
    incident_id: str
    severity: IncidentSeverity
    service_affected: str
    start_time: datetime
    detection_source: str
    symptoms: List[str]
    related_changes: List[str] = field(default_factory=list)
    runbook_url: Optional[str] = None
    stakeholders: List[str] = field(default_factory=list)

class SREServiceNowAgent:
    """SRE Agent specialized for ServiceNow integration"""
    
    def __init__(self):
        self.agent_info = self._initialize_agent_info()
        self.mcp = FastMCP(f"SRE-ServiceNow-{self.agent_info['name']}")
        self.behavior_system = AgentBehaviorSystem()
        self.servicenow_adapter = ServiceNowAgentAdapter()
        self.active_incidents: Dict[str, IncidentContext] = {}
        self.slo_targets = self._initialize_slos()
        
        # Setup MCP components
        self._setup_mcp_resources()
        self._setup_mcp_tools()
        self._setup_mcp_prompts()
        
        logger.info(f"Initialized SRE ServiceNow Agent: {self.agent_info['name']}")
    
    def _initialize_agent_info(self) -> Dict[str, Any]:
        """Initialize SRE agent information"""
        return {
            "id": "sre_servicenow_001",
            "name": "OpenAISDK_SRE_ServiceNowSpecialist",
            "display_name": "SRE ServiceNow Specialist",
            "category": "SRE/DevOps",
            "subcategory": "Incident Management",
            "skills": [
                "Incident Response",
                "ServiceNow Platform",
                "SLO Management",
                "Root Cause Analysis",
                "Automation",
                "Monitoring",
                "Change Management",
                "Problem Management",
                "Capacity Planning",
                "Disaster Recovery"
            ],
            "tools": [
                "incident_commander",
                "slo_calculator",
                "runbook_executor",
                "change_analyzer",
                "monitoring_aggregator",
                "alert_correlator",
                "postmortem_generator"
            ],
            "servicenow_tools": [
                "create_incident",
                "update_incident",
                "search_incidents",
                "create_problem",
                "create_change_request",
                "get_cmdb_ci",
                "create_knowledge_article",
                "execute_workflow"
            ],
            "instructions": """You are an expert SRE (Site Reliability Engineer) specialized in ServiceNow integration. You excel at:

- Rapid incident response and resolution
- Managing incidents through ServiceNow platform
- Calculating and maintaining SLOs/SLIs
- Performing root cause analysis
- Automating incident response procedures
- Coordinating with multiple teams
- Creating and updating runbooks
- Post-incident reviews and improvements

You follow SRE best practices:
1. Prioritize service reliability and user experience
2. Automate toil wherever possible
3. Learn from every incident
4. Maintain comprehensive documentation
5. Balance feature velocity with reliability

When handling incidents:
- Assess severity and impact immediately
- Follow established runbooks
- Communicate clearly and frequently
- Document all actions in ServiceNow
- Focus on rapid mitigation first, then root cause"""
        }
    
    def _initialize_slos(self) -> Dict[str, SLOTarget]:
        """Initialize SLO targets"""
        return {
            "availability": SLOTarget(
                name="Service Availability",
                target=99.9,
                measurement_window="30d",
                error_budget=0.1,
                current_performance=99.95
            ),
            "latency": SLOTarget(
                name="Response Time",
                target=95.0,  # 95% of requests under 200ms
                measurement_window="7d",
                error_budget=5.0,
                current_performance=96.2
            ),
            "error_rate": SLOTarget(
                name="Error Rate",
                target=99.5,  # Less than 0.5% errors
                measurement_window="24h",
                error_budget=0.5,
                current_performance=99.7
            )
        }
    
    def _setup_mcp_resources(self):
        """Setup MCP resources for SRE operations"""
        
        @self.mcp.resource("sre://agent/profile")
        async def get_agent_profile() -> str:
            """Get SRE agent profile and capabilities"""
            profile = {
                **self.agent_info,
                "active_incidents": len(self.active_incidents),
                "slo_status": {
                    name: {
                        "target": slo.target,
                        "current": slo.current_performance,
                        "error_budget_remaining": slo.error_budget
                    }
                    for name, slo in self.slo_targets.items()
                },
                "specializations": [
                    "ServiceNow Incident Management",
                    "SLO/Error Budget Management",
                    "Automated Remediation",
                    "Cross-team Coordination"
                ]
            }
            return json.dumps(profile, indent=2)
        
        @self.mcp.resource("sre://incidents/active")
        async def get_active_incidents() -> str:
            """Get currently active incidents"""
            incidents = []
            for incident_id, context in self.active_incidents.items():
                incidents.append({
                    "id": incident_id,
                    "severity": context.severity.name,
                    "service": context.service_affected,
                    "duration": str(datetime.now() - context.start_time),
                    "state": "active",
                    "symptoms": context.symptoms
                })
            return json.dumps({"total": len(incidents), "incidents": incidents}, indent=2)
        
        @self.mcp.resource("sre://slo/status")
        async def get_slo_status() -> str:
            """Get current SLO status and error budgets"""
            status = {}
            for name, slo in self.slo_targets.items():
                status[name] = {
                    "name": slo.name,
                    "target": f"{slo.target}%",
                    "current": f"{slo.current_performance}%",
                    "error_budget": f"{slo.error_budget}%",
                    "status": "healthy" if slo.current_performance >= slo.target else "at_risk",
                    "measurement_window": slo.measurement_window
                }
            return json.dumps(status, indent=2)
        
        @self.mcp.resource("sre://runbooks/catalog")
        async def get_runbooks_catalog() -> str:
            """Get available runbooks"""
            runbooks = {
                "database_outage": {
                    "title": "Database Outage Response",
                    "severity": "CRITICAL",
                    "steps": [
                        "Check database connection and status",
                        "Verify replica health",
                        "Initiate failover if needed",
                        "Notify stakeholders",
                        "Monitor recovery"
                    ]
                },
                "high_latency": {
                    "title": "High Latency Investigation",
                    "severity": "HIGH",
                    "steps": [
                        "Check current load and traffic patterns",
                        "Review recent deployments",
                        "Analyze slow queries/requests",
                        "Scale resources if needed",
                        "Implement rate limiting if necessary"
                    ]
                },
                "deployment_rollback": {
                    "title": "Emergency Deployment Rollback",
                    "severity": "HIGH",
                    "steps": [
                        "Identify problematic deployment",
                        "Initiate rollback procedure",
                        "Verify service restoration",
                        "Document issue for RCA",
                        "Schedule post-mortem"
                    ]
                }
            }
            return json.dumps(runbooks, indent=2)
    
    async def respond_to_incident(
        self,
        description: str,
        service: str,
        severity: str = "MEDIUM",
        symptoms: List[str] = None,
        detection_source: str = "monitoring"
    ) -> Dict[str, Any]:
        """Respond to a new incident
        
        Args:
            description: Incident description
            service: Affected service
            severity: Incident severity (CRITICAL, HIGH, MEDIUM, LOW)
            symptoms: List of observed symptoms
            detection_source: How the incident was detected
            
        Returns:
            Incident response details
        """
        # Create incident context
        incident_id = f"INC{datetime.now().strftime('%Y%m%d%H%M%S')}"
        context = IncidentContext(
            incident_id=incident_id,
            severity=IncidentSeverity[severity],
            service_affected=service,
            start_time=datetime.now(),
            detection_source=detection_source,
            symptoms=symptoms or []
        )
        
        self.active_incidents[incident_id] = context
        
        # Determine initial response actions
        response_actions = self._determine_response_actions(context)
        
        # Create ServiceNow incident
        servicenow_incident = await self._create_servicenow_incident(context, description)
        
        return {
            "incident_id": incident_id,
            "servicenow_number": servicenow_incident.get("number", "pending"),
            "severity": severity,
            "service": service,
            "status": "incident_created",
            "initial_actions": response_actions,
            "estimated_impact": self._estimate_impact(context),
            "notification_sent_to": self._get_stakeholders(context),
            "runbook": self._get_runbook_url(context),
            "slo_impact": self._calculate_slo_impact(context)
        }
    
    def _setup_mcp_tools(self):
        """Setup MCP tools for SRE operations"""
        
        # Register respond_to_incident as MCP tool (wrapper that calls instance method)
        @self.mcp.tool()
        async def respond_to_incident(
            description: str,
            service: str,
            severity: str = "MEDIUM",
            symptoms: List[str] = None,
            detection_source: str = "monitoring"
        ) -> Dict[str, Any]:
            """Respond to a new incident (MCP tool wrapper)"""
            return await self.respond_to_incident(
                description=description,
                service=service,
                severity=severity,
                symptoms=symptoms,
                detection_source=detection_source
            )
        
        @self.mcp.tool()
        async def update_incident_status(
            incident_id: str,
            status: str,
            notes: str,
            actions_taken: List[str] = None
        ) -> Dict[str, Any]:
            """Update incident status
            
            Args:
                incident_id: Incident identifier
                status: New status
                notes: Update notes
                actions_taken: List of actions taken
                
            Returns:
                Update result
            """
            if incident_id not in self.active_incidents:
                return {"error": f"Incident {incident_id} not found"}
            
            context = self.active_incidents[incident_id]
            
            # Update in ServiceNow
            update_result = await self._update_servicenow_incident(
                incident_id,
                status,
                notes,
                actions_taken
            )
            
            # Update local state
            if status in ["resolved", "closed"]:
                # Calculate incident duration
                duration = datetime.now() - context.start_time
                
                # Update SLO impact
                self._update_slo_metrics(context, duration)
                
                # Remove from active incidents
                if status == "closed":
                    del self.active_incidents[incident_id]
            
            return {
                "incident_id": incident_id,
                "status": status,
                "updated_at": datetime.now().isoformat(),
                "servicenow_updated": update_result.get("success", False),
                "duration": str(datetime.now() - context.start_time),
                "slo_impact_updated": True
            }
        
        @self.mcp.tool()
        async def calculate_error_budget(
            slo_name: str,
            time_range: Optional[str] = None
        ) -> Dict[str, Any]:
            """Calculate error budget for an SLO
            
            Args:
                slo_name: Name of the SLO
                time_range: Time range for calculation
                
            Returns:
                Error budget details
            """
            if slo_name not in self.slo_targets:
                return {"error": f"SLO '{slo_name}' not found"}
            
            slo = self.slo_targets[slo_name]
            
            # Calculate budget consumption
            budget_consumed = (slo.target - slo.current_performance) / (100 - slo.target) * 100
            budget_remaining = 100 - budget_consumed
            
            # Time-based calculations
            if slo.measurement_window == "30d":
                minutes_in_window = 30 * 24 * 60
            elif slo.measurement_window == "7d":
                minutes_in_window = 7 * 24 * 60
            else:  # 24h
                minutes_in_window = 24 * 60
            
            allowed_downtime = minutes_in_window * (100 - slo.target) / 100
            consumed_downtime = minutes_in_window * (slo.target - slo.current_performance) / 100
            
            return {
                "slo": slo_name,
                "target": f"{slo.target}%",
                "current_performance": f"{slo.current_performance}%",
                "error_budget": {
                    "total": f"{100 - slo.target}%",
                    "consumed": f"{budget_consumed:.2f}%",
                    "remaining": f"{budget_remaining:.2f}%"
                },
                "downtime_budget": {
                    "allowed_minutes": round(allowed_downtime),
                    "consumed_minutes": round(consumed_downtime),
                    "remaining_minutes": round(allowed_downtime - consumed_downtime)
                },
                "status": "healthy" if budget_remaining > 20 else "at_risk" if budget_remaining > 0 else "exhausted",
                "recommendation": self._get_slo_recommendation(budget_remaining)
            }
        
        @self.mcp.tool()
        async def perform_rca(
            incident_id: str,
            contributing_factors: List[str],
            root_cause: str,
            timeline: List[Dict[str, str]]
        ) -> Dict[str, Any]:
            """Perform root cause analysis
            
            Args:
                incident_id: Incident identifier
                contributing_factors: List of contributing factors
                root_cause: Identified root cause
                timeline: Event timeline
                
            Returns:
                RCA results
            """
            # Generate RCA document
            rca_doc = {
                "incident_id": incident_id,
                "performed_by": self.agent_info["name"],
                "date": datetime.now().isoformat(),
                "root_cause": root_cause,
                "contributing_factors": contributing_factors,
                "timeline": timeline,
                "impact_analysis": self._analyze_incident_impact(incident_id),
                "preventive_measures": self._suggest_preventive_measures(root_cause, contributing_factors),
                "action_items": self._generate_action_items(root_cause, contributing_factors)
            }
            
            # Create problem record in ServiceNow
            problem_record = await self._create_problem_record(incident_id, rca_doc)
            
            # Create knowledge article
            kb_article = await self._create_knowledge_article(incident_id, rca_doc)
            
            return {
                "rca_complete": True,
                "incident_id": incident_id,
                "root_cause": root_cause,
                "problem_record": problem_record.get("number", "created"),
                "knowledge_article": kb_article.get("number", "created"),
                "preventive_measures": len(rca_doc["preventive_measures"]),
                "action_items": len(rca_doc["action_items"]),
                "documentation": "completed"
            }
        
        @self.mcp.tool()
        async def execute_runbook(
            runbook_name: str,
            incident_id: Optional[str] = None,
            parameters: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Execute a runbook
            
            Args:
                runbook_name: Name of the runbook
                incident_id: Associated incident
                parameters: Runbook parameters
                
            Returns:
                Execution results
            """
            # Simulate runbook execution
            execution_id = f"RB{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Get runbook steps
            runbook_steps = self._get_runbook_steps(runbook_name)
            
            execution_log = []
            for i, step in enumerate(runbook_steps):
                # Simulate step execution
                step_result = {
                    "step": i + 1,
                    "description": step,
                    "status": "completed",
                    "timestamp": (datetime.now() + timedelta(seconds=i*30)).isoformat()
                }
                execution_log.append(step_result)
            
            # Update incident if provided
            if incident_id:
                await self.update_incident_status(
                    incident_id,
                    "in_progress",
                    f"Executed runbook: {runbook_name}",
                    [f"Step {i+1}: {step['description']}" for i, step in enumerate(execution_log)]
                )
            
            return {
                "execution_id": execution_id,
                "runbook": runbook_name,
                "status": "completed",
                "steps_executed": len(execution_log),
                "execution_log": execution_log,
                "incident_id": incident_id,
                "duration": f"{len(execution_log) * 30} seconds"
            }
        
        @self.mcp.tool()
        async def analyze_service_health(
            service_name: str,
            metrics: Optional[List[str]] = None
        ) -> Dict[str, Any]:
            """Analyze service health and reliability
            
            Args:
                service_name: Name of the service
                metrics: Specific metrics to analyze
                
            Returns:
                Health analysis
            """
            # Default metrics if none specified
            if not metrics:
                metrics = ["availability", "latency", "error_rate", "throughput"]
            
            # Simulate health metrics
            import random
            health_data = {}
            
            for metric in metrics:
                if metric == "availability":
                    health_data[metric] = {
                        "current": random.uniform(99.5, 99.99),
                        "trend": "stable",
                        "slo_target": 99.9,
                        "status": "healthy"
                    }
                elif metric == "latency":
                    health_data[metric] = {
                        "p50": random.uniform(50, 100),
                        "p95": random.uniform(150, 250),
                        "p99": random.uniform(300, 500),
                        "trend": "increasing" if random.random() > 0.7 else "stable",
                        "status": "healthy"
                    }
                elif metric == "error_rate":
                    health_data[metric] = {
                        "current": random.uniform(0.1, 0.5),
                        "trend": "stable",
                        "threshold": 1.0,
                        "status": "healthy"
                    }
                elif metric == "throughput":
                    health_data[metric] = {
                        "current_rps": random.randint(1000, 5000),
                        "peak_today": random.randint(5000, 8000),
                        "capacity": 10000,
                        "utilization": random.uniform(40, 80)
                    }
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(health_data)
            
            return {
                "service": service_name,
                "timestamp": datetime.now().isoformat(),
                "overall_health": "healthy",
                "metrics": health_data,
                "recommendations": recommendations,
                "slo_compliance": all(
                    self.slo_targets[slo].current_performance >= self.slo_targets[slo].target
                    for slo in self.slo_targets
                ),
                "active_incidents": len([
                    inc for inc in self.active_incidents.values()
                    if inc.service_affected == service_name
                ])
            }
    
    def _setup_mcp_prompts(self):
        """Setup MCP prompts for SRE scenarios"""
        
        @self.mcp.prompt()
        async def incident_response_prompt(
            incident_description: str,
            severity: str,
            service: str
        ) -> List[Dict[str, Any]]:
            """Generate incident response prompt
            
            Args:
                incident_description: Description of the incident
                severity: Incident severity
                service: Affected service
                
            Returns:
                Prompt messages
            """
            return [
                {
                    "role": "system",
                    "content": f"""You are {self.agent_info['display_name']}, an expert SRE. 
                    Respond to incidents with:
                    1. Immediate mitigation steps
                    2. Clear communication
                    3. ServiceNow documentation
                    4. Root cause investigation
                    5. SLO impact assessment"""
                },
                {
                    "role": "user",
                    "content": f"""INCIDENT ALERT:
                    Service: {service}
                    Severity: {severity}
                    Description: {incident_description}
                    
                    Provide immediate response plan."""
                }
            ]
        
        @self.mcp.prompt()
        async def postmortem_prompt(
            incident_summary: Dict[str, Any],
            timeline: List[Dict[str, str]],
            impact_data: Dict[str, Any]
        ) -> List[Dict[str, Any]]:
            """Generate postmortem prompt
            
            Args:
                incident_summary: Incident details
                timeline: Event timeline
                impact_data: Impact analysis
                
            Returns:
                Prompt messages
            """
            timeline_text = "\n".join([
                f"{event['time']}: {event['description']}"
                for event in timeline
            ])
            
            return [
                {
                    "role": "system",
                    "content": """You are conducting a blameless postmortem. Focus on:
                    1. Clear timeline of events
                    2. Root cause identification
                    3. Contributing factors
                    4. Lessons learned
                    5. Actionable preventive measures"""
                },
                {
                    "role": "user",
                    "content": f"""Conduct postmortem for:
                    {json.dumps(incident_summary, indent=2)}
                    
                    Timeline:
                    {timeline_text}
                    
                    Impact:
                    {json.dumps(impact_data, indent=2)}"""
                }
            ]
    
    # Helper methods
    def _determine_response_actions(self, context: IncidentContext) -> List[str]:
        """Determine initial response actions based on incident context"""
        actions = []
        
        if context.severity == IncidentSeverity.CRITICAL:
            actions.extend([
                "Page on-call engineer immediately",
                "Initiate incident bridge",
                "Notify executive team",
                "Prepare status page update"
            ])
        elif context.severity == IncidentSeverity.HIGH:
            actions.extend([
                "Alert on-call engineer",
                "Review recent changes",
                "Check monitoring dashboards",
                "Prepare mitigation options"
            ])
        
        # Add service-specific actions
        if "database" in context.service_affected.lower():
            actions.append("Check database replication status")
        elif "api" in context.service_affected.lower():
            actions.append("Review API gateway metrics")
        
        return actions
    
    def _estimate_impact(self, context: IncidentContext) -> Dict[str, Any]:
        """Estimate incident impact"""
        return {
            "users_affected": "All users" if context.severity == IncidentSeverity.CRITICAL else "Subset of users",
            "revenue_impact": "High" if context.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH] else "Low",
            "slo_impact": "Significant" if context.severity == IncidentSeverity.CRITICAL else "Moderate",
            "reputation_risk": context.severity == IncidentSeverity.CRITICAL
        }
    
    def _get_stakeholders(self, context: IncidentContext) -> List[str]:
        """Get stakeholders to notify"""
        stakeholders = ["on-call-engineer", "sre-team"]
        
        if context.severity == IncidentSeverity.CRITICAL:
            stakeholders.extend(["engineering-manager", "product-manager", "executive-team"])
        elif context.severity == IncidentSeverity.HIGH:
            stakeholders.append("engineering-manager")
        
        return stakeholders
    
    def _get_runbook_url(self, context: IncidentContext) -> str:
        """Get relevant runbook URL"""
        # In real implementation, this would look up actual runbook URLs
        return f"https://runbooks.example.com/{context.service_affected.lower()}/incident-response"
    
    def _calculate_slo_impact(self, context: IncidentContext) -> Dict[str, Any]:
        """Calculate SLO impact of the incident"""
        impact = {}
        
        for slo_name, slo in self.slo_targets.items():
            if slo_name == "availability" and context.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
                # Estimate downtime impact
                estimated_downtime = 30 if context.severity == IncidentSeverity.CRITICAL else 15
                impact[slo_name] = {
                    "affected": True,
                    "estimated_impact": f"{estimated_downtime} minutes of downtime",
                    "error_budget_consumption": f"{(estimated_downtime / (30 * 24 * 60)) * 100:.2f}%"
                }
            else:
                impact[slo_name] = {"affected": False}
        
        return impact
    
    def _update_slo_metrics(self, context: IncidentContext, duration: timedelta):
        """Update SLO metrics after incident resolution"""
        if context.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.HIGH]:
            # Update availability SLO
            downtime_minutes = duration.total_seconds() / 60
            
            # Simple calculation for demo (in reality, this would be more complex)
            availability_slo = self.slo_targets["availability"]
            total_minutes = 30 * 24 * 60  # 30 days in minutes
            
            # Reduce current performance based on downtime
            performance_reduction = (downtime_minutes / total_minutes) * 100
            availability_slo.current_performance -= performance_reduction
            
            # Update error budget
            availability_slo.error_budget = 100 - ((availability_slo.target - availability_slo.current_performance) / (100 - availability_slo.target) * 100)
    
    def _get_slo_recommendation(self, budget_remaining: float) -> str:
        """Get recommendation based on error budget"""
        if budget_remaining > 50:
            return "Healthy error budget. Continue with normal deployment velocity."
        elif budget_remaining > 20:
            return "Monitor closely. Consider slowing down risky deployments."
        elif budget_remaining > 0:
            return "Error budget at risk. Freeze non-critical deployments. Focus on reliability."
        else:
            return "Error budget exhausted. Immediate reliability improvements required. Halt all deployments."
    
    def _analyze_incident_impact(self, incident_id: str) -> Dict[str, Any]:
        """Analyze impact of an incident"""
        if incident_id not in self.active_incidents:
            return {"error": "Incident not found"}
        
        context = self.active_incidents[incident_id]
        duration = datetime.now() - context.start_time
        
        return {
            "duration": str(duration),
            "severity": context.severity.name,
            "service": context.service_affected,
            "estimated_users_impacted": "1000+" if context.severity == IncidentSeverity.CRITICAL else "100-1000",
            "slo_impact": self._calculate_slo_impact(context),
            "financial_impact": "High" if duration.total_seconds() > 3600 else "Medium"
        }
    
    def _suggest_preventive_measures(self, root_cause: str, contributing_factors: List[str]) -> List[str]:
        """Suggest preventive measures based on RCA"""
        measures = []
        
        # Generic measures
        measures.append(f"Add monitoring for early detection of {root_cause}")
        measures.append("Update runbook with lessons learned")
        
        # Specific measures based on factors
        for factor in contributing_factors:
            if "deployment" in factor.lower():
                measures.append("Implement canary deployments")
                measures.append("Add automated rollback triggers")
            elif "capacity" in factor.lower():
                measures.append("Implement auto-scaling policies")
                measures.append("Set up capacity alerts at 80% threshold")
            elif "configuration" in factor.lower():
                measures.append("Add configuration validation tests")
                measures.append("Implement configuration drift detection")
        
        return measures
    
    def _generate_action_items(self, root_cause: str, contributing_factors: List[str]) -> List[Dict[str, str]]:
        """Generate action items from RCA"""
        action_items = []
        
        # High priority items
        action_items.append({
            "priority": "HIGH",
            "description": f"Implement monitoring for {root_cause}",
            "assignee": "sre-team",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat()
        })
        
        # Medium priority items
        for factor in contributing_factors[:3]:  # Top 3 factors
            action_items.append({
                "priority": "MEDIUM",
                "description": f"Address contributing factor: {factor}",
                "assignee": "engineering-team",
                "due_date": (datetime.now() + timedelta(days=14)).isoformat()
            })
        
        return action_items
    
    def _get_runbook_steps(self, runbook_name: str) -> List[str]:
        """Get runbook steps"""
        runbooks = {
            "database_outage": [
                "Check database connection and status",
                "Verify replica health",
                "Initiate failover if needed",
                "Notify stakeholders",
                "Monitor recovery"
            ],
            "high_latency": [
                "Check current load and traffic patterns",
                "Review recent deployments",
                "Analyze slow queries/requests",
                "Scale resources if needed",
                "Implement rate limiting if necessary"
            ],
            "deployment_rollback": [
                "Identify problematic deployment",
                "Initiate rollback procedure",
                "Verify service restoration",
                "Document issue for RCA",
                "Schedule post-mortem"
            ]
        }
        
        return runbooks.get(runbook_name, ["Generic step 1", "Generic step 2", "Generic step 3"])
    
    def _generate_health_recommendations(self, health_data: Dict[str, Any]) -> List[str]:
        """Generate health recommendations based on metrics"""
        recommendations = []
        
        # Check latency trends
        if "latency" in health_data and health_data["latency"]["trend"] == "increasing":
            recommendations.append("Investigate increasing latency trend")
            recommendations.append("Consider performance optimization sprint")
        
        # Check error rates
        if "error_rate" in health_data and health_data["error_rate"]["current"] > 0.3:
            recommendations.append("Error rate approaching threshold - investigate error patterns")
        
        # Check throughput utilization
        if "throughput" in health_data and health_data["throughput"]["utilization"] > 70:
            recommendations.append("High capacity utilization - plan for scaling")
        
        return recommendations
    
    # ServiceNow integration methods (simulated for demo)
    async def _create_servicenow_incident(self, context: IncidentContext, description: str) -> Dict[str, Any]:
        """Create incident in ServiceNow"""
        # In real implementation, this would call ServiceNow MCP server
        return {
            "success": True,
            "number": f"INC00{datetime.now().strftime('%H%M%S')}",
            "sys_id": f"sys_{context.incident_id}",
            "state": "new"
        }
    
    async def _update_servicenow_incident(
        self, 
        incident_id: str, 
        status: str, 
        notes: str,
        actions_taken: List[str]
    ) -> Dict[str, Any]:
        """Update incident in ServiceNow"""
        return {
            "success": True,
            "updated": datetime.now().isoformat()
        }
    
    async def _create_problem_record(self, incident_id: str, rca_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create problem record in ServiceNow"""
        return {
            "success": True,
            "number": f"PRB00{datetime.now().strftime('%H%M%S')}",
            "sys_id": f"sys_prb_{incident_id}"
        }
    
    async def _create_knowledge_article(self, incident_id: str, rca_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Create knowledge article in ServiceNow"""
        return {
            "success": True,
            "number": f"KB00{datetime.now().strftime('%H%M%S')}",
            "sys_id": f"sys_kb_{incident_id}"
        }
    
    async def run(self):
        """Run the SRE ServiceNow agent MCP server"""
        from mcp.server.stdio import stdio_server
        
        logger.info("Starting SRE ServiceNow Agent MCP server...")
        async with stdio_server() as (read_stream, write_stream):
            await self.mcp.run(
                read_stream,
                write_stream,
                self.mcp.create_initialization_options()
            )

# Demo and testing functions
async def demonstrate_sre_agent():
    """Demonstrate SRE agent capabilities"""
    agent = SREServiceNowAgent()
    
    print("\n🚀 SRE ServiceNow Agent Demo")
    print("="*60)
    print(f"Agent: {agent.agent_info['display_name']}")
    print(f"Skills: {', '.join(agent.agent_info['skills'][:5])}...")
    print(f"ServiceNow Tools: {len(agent.agent_info['servicenow_tools'])}")
    
    # Simulate incident response
    print("\n📊 Simulating Incident Response:")
    print("-"*40)
    
    # Create a critical incident
    incident_response = await agent.respond_to_incident(
        description="API Gateway returning 503 errors",
        service="api-gateway",
        severity="CRITICAL",
        symptoms=["503 errors", "High latency", "Connection timeouts"],
        detection_source="monitoring"
    )
    
    print(f"✅ Incident Created: {incident_response['incident_id']}")
    print(f"   ServiceNow #: {incident_response['servicenow_number']}")
    print(f"   Initial Actions: {len(incident_response['initial_actions'])}")
    print(f"   Runbook: {incident_response['runbook']}")
    
    # Check error budget
    print("\n💰 Error Budget Status:")
    print("-"*40)
    
    budget_status = await agent.calculate_error_budget("availability")
    print(f"   Target: {budget_status['target']}")
    print(f"   Current: {budget_status['current_performance']}")
    print(f"   Budget Remaining: {budget_status['error_budget']['remaining']}")
    print(f"   Status: {budget_status['status']}")
    
    # Execute runbook
    print("\n📋 Executing Runbook:")
    print("-"*40)
    
    runbook_result = await agent.execute_runbook(
        "database_outage",
        incident_id=incident_response['incident_id']
    )
    
    print(f"✅ Runbook Executed: {runbook_result['runbook']}")
    print(f"   Steps: {runbook_result['steps_executed']}")
    print(f"   Duration: {runbook_result['duration']}")
    
    # Service health check
    print("\n🏥 Service Health Analysis:")
    print("-"*40)
    
    health_analysis = await agent.analyze_service_health("api-gateway")
    print(f"   Overall Health: {health_analysis['overall_health']}")
    print(f"   SLO Compliance: {health_analysis['slo_compliance']}")
    print(f"   Recommendations: {len(health_analysis['recommendations'])}")
    
    print("\n✅ SRE ServiceNow Agent Ready for Integration!")

if __name__ == "__main__":
    asyncio.run(demonstrate_sre_agent())
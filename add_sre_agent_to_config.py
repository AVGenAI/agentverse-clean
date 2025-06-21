#!/usr/bin/env python3
"""
Add SRE ServiceNow Agent to the agents configuration
"""

import json
import uuid
from datetime import datetime

# Load existing agents
with open('src/config/agentverse_agents_1000.json', 'r') as f:
    agents = json.load(f)

# Create SRE ServiceNow Agent configuration
sre_agent = {
    "name": "OpenAISDK_SRE_ServiceNowSpecialist",
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
- Focus on rapid mitigation first, then root cause""",
    "enhanced_metadata": {
        "agent_uuid": "sre_servicenow_001",
        "canonical_name": "agentverse.sre.servicenow_specialist",
        "display_name": "SRE ServiceNow Specialist",
        "avatar_emoji": "🚨",
        "category": "SRE/DevOps",
        "subcategory": "Incident Management",
        "capabilities": {
            "primary_expertise": [
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
            "tools_mastery": {
                "incident_commander": "expert",
                "slo_calculator": "expert",
                "runbook_executor": "expert",
                "change_analyzer": "expert",
                "monitoring_aggregator": "expert",
                "alert_correlator": "expert",
                "postmortem_generator": "expert",
                "create_incident": "expert",
                "update_incident": "expert",
                "search_incidents": "expert",
                "create_problem": "expert",
                "create_change_request": "expert",
                "get_cmdb_ci": "advanced",
                "create_knowledge_article": "expert",
                "execute_workflow": "advanced"
            },
            "workflows": {
                "incident_response": {
                    "description": "Rapid incident detection, triage, and resolution",
                    "complexity": "high"
                },
                "slo_monitoring": {
                    "description": "Track and maintain service level objectives",
                    "complexity": "medium"
                },
                "root_cause_analysis": {
                    "description": "Investigate and document incident root causes",
                    "complexity": "high"
                },
                "change_management": {
                    "description": "Plan and execute safe production changes",
                    "complexity": "high"
                }
            }
        },
        "collaboration": {
            "style": ["proactive", "systematic", "communicative"],
            "prefers_team_size": "flexible",
            "communication_style": "clear and urgent when needed"
        },
        "performance": {
            "success_rate": 98,
            "avg_response_time": "0.5s",
            "completed_tasks": 5000,
            "specialization_score": 0.99
        },
        "quality": {
            "accuracy_score": 0.98,
            "consistency_score": 0.99,
            "reliability_score": 0.99,
            "trust_score": 0.98
        },
        "network": {
            "frequent_collaborators": [
                "agentverse.devops.*",
                "agentverse.monitoring.*",
                "agentverse.security.*",
                "agentverse.database.*"
            ],
            "upstream": ["agentverse.monitoring.*", "agentverse.alerting.*"],
            "downstream": ["agentverse.support.*", "agentverse.engineering.*"]
        },
        "discovery": {
            "keywords": ["sre", "incident", "servicenow", "slo", "monitoring", "reliability"],
            "problem_domains": ["incident management", "service reliability", "monitoring", "alerting"],
            "use_cases": [
                "Incident response and management",
                "SLO tracking and reporting",
                "ServiceNow automation",
                "Post-incident reviews",
                "Runbook automation"
            ]
        },
        "version": "1.0.0",
        "created_at": datetime.now().isoformat()
    }
}

# Add to the beginning of the agents list (so it's easy to find)
agents.insert(0, sre_agent)

# Also add a few more SRE/DevOps agents for variety
additional_sre_agents = [
    {
        "name": "OpenAISDK_DevOps_IncidentCommander",
        "instructions": "You are an Incident Commander specializing in coordinating response efforts during critical incidents.",
        "enhanced_metadata": {
            "agent_uuid": str(uuid.uuid4()),
            "canonical_name": "agentverse.devops.incident_commander",
            "display_name": "Incident Commander",
            "avatar_emoji": "🎯",
            "category": "DevOps",
            "subcategory": "Incident Management",
            "capabilities": {
                "primary_expertise": [
                    "Incident Command",
                    "Crisis Management",
                    "Team Coordination",
                    "Communication",
                    "Decision Making"
                ],
                "tools_mastery": {
                    "incident_commander": "expert",
                    "alert_manager": "expert",
                    "notification_sender": "expert",
                    "team_collaborator": "expert"
                }
            }
        }
    },
    {
        "name": "OpenAISDK_Support_ServiceNowAdmin",
        "instructions": "You are a ServiceNow Administrator expert in configuring and managing ServiceNow instances.",
        "enhanced_metadata": {
            "agent_uuid": str(uuid.uuid4()),
            "canonical_name": "agentverse.support.servicenow_admin",
            "display_name": "ServiceNow Administrator",
            "avatar_emoji": "⚙️",
            "category": "Support",
            "subcategory": "Platform Administration",
            "capabilities": {
                "primary_expertise": [
                    "ServiceNow Administration",
                    "ITSM Configuration",
                    "Workflow Design",
                    "Platform Customization",
                    "User Management"
                ],
                "tools_mastery": {
                    "create_incident": "expert",
                    "update_incident": "expert",
                    "workflow_orchestrator": "expert",
                    "config_manager": "expert"
                }
            }
        }
    }
]

# Add additional agents
for agent in additional_sre_agents:
    # Complete the metadata
    metadata = agent["enhanced_metadata"]
    metadata.update({
        "collaboration": {
            "style": ["collaborative", "detail-oriented"],
            "prefers_team_size": "medium",
            "communication_style": "professional"
        },
        "performance": {
            "success_rate": 95,
            "avg_response_time": "1.0s",
            "completed_tasks": 1000,
            "specialization_score": 0.90
        },
        "quality": {
            "accuracy_score": 0.95,
            "consistency_score": 0.96,
            "reliability_score": 0.97,
            "trust_score": 0.95
        },
        "network": {
            "frequent_collaborators": ["agentverse.sre.*", "agentverse.devops.*"],
            "upstream": ["agentverse.monitoring.*"],
            "downstream": ["agentverse.support.*"]
        },
        "discovery": {
            "keywords": metadata["display_name"].lower().split(),
            "problem_domains": ["incident management", "platform administration"],
            "use_cases": ["ServiceNow operations", "Incident handling"]
        },
        "version": "1.0.0",
        "created_at": datetime.now().isoformat()
    })
    agents.insert(1, agent)

# Save the updated configuration
with open('src/config/agentverse_agents_1000.json', 'w') as f:
    json.dump(agents, f, indent=2)

print(f"✅ Added SRE ServiceNow Specialist and {len(additional_sre_agents)} related agents")
print(f"Total agents now: {len(agents)}")
print("\nAdded agents:")
print("1. SRE ServiceNow Specialist - Expert in incident management with ServiceNow")
print("2. Incident Commander - Coordinates incident response efforts")
print("3. ServiceNow Administrator - Manages ServiceNow platform")
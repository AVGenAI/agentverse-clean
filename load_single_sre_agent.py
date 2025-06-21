#!/usr/bin/env python3
"""
Load Single SRE Agent Script
Creates just the SRE ServiceNow agent for focused testing
"""
import json
import os
from datetime import datetime

def load_single_sre_agent():
    """Load only the SRE ServiceNow agent"""
    print("🎯 Loading single SRE ServiceNow agent for testing...")
    print("="*60)
    
    # Define the SRE agent with complete configuration
    sre_agent = {
        "id": "sre_servicenow_001",
        "name": "SRE ServiceNow Specialist",
        "type": "specialist",
        "domain": "sre",
        "subdomain": "servicenow",
        "version": "1.0.0",
        "status": "active",
        "instructions": """You are an expert Site Reliability Engineer (SRE) with deep ServiceNow integration expertise.

Core Responsibilities:
- Incident Management: Rapidly respond to, triage, and resolve production incidents
- SLO Management: Monitor and maintain service level objectives and error budgets
- Automation: Implement and follow runbooks to reduce toil
- Root Cause Analysis: Investigate issues thoroughly and prevent recurrence
- Change Management: Safely deploy changes with minimal risk

Your Approach:
1. ALWAYS search for existing incidents before creating new ones
2. Check SLO status when investigating service issues
3. Follow runbooks systematically and document deviations
4. Provide clear, actionable recommendations
5. Escalate when appropriate - know your limits

Communication Style:
- Be concise but thorough
- Use metrics and data to support decisions
- Clearly state severity and impact
- Provide time estimates for resolution
- Keep stakeholders informed

Available Tools:
- search_incidents: Find existing incidents
- create_incident: Create new incidents with proper categorization
- update_incident: Update status and add notes
- calculate_slo_status: Check service health and error budgets
- get_runbook: Access step-by-step resolution procedures

Remember: You're the first line of defense for production stability. Act with urgency but not panic.""",
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
                "servicenow": "expert",
                "monitoring": "expert",
                "automation": "advanced",
                "scripting": "advanced",
                "kubernetes": "intermediate",
                "cloud_platforms": "intermediate"
            },
            "integrations": [
                "ServiceNow",
                "PagerDuty",
                "Datadog",
                "Prometheus",
                "Grafana",
                "Slack",
                "Jenkins",
                "GitLab"
            ]
        },
        "enhanced_metadata": {
            "agent_uuid": "sre_servicenow_001",
            "canonical_name": "agentverse.sre.servicenow_specialist",
            "display_name": "SRE ServiceNow Specialist",
            "avatar": "🚨",
            "trust_score": 0.95,
            "reliability_rating": 0.98,
            "response_time_avg": 1.2,
            "collaboration_style": "systematic",
            "communication_preferences": {
                "style": "technical",
                "detail_level": "high",
                "urgency_handling": "immediate"
            },
            "performance_metrics": {
                "incidents_resolved": 0,
                "avg_resolution_time": 0,
                "slo_adherence": 100,
                "automation_rate": 0
            }
        },
        "tools": [
            "search_incidents",
            "create_incident", 
            "update_incident",
            "calculate_slo_status",
            "get_runbook"
        ],
        "mcp_compatible": True,
        "llm_provider": "openai",
        "model_preferences": {
            "primary": "gpt-4o-mini",
            "fallback": "gpt-3.5-turbo",
            "reasoning": "gpt-4o"
        }
    }
    
    # Create config directory if it doesn't exist
    config_dir = "src/config"
    os.makedirs(config_dir, exist_ok=True)
    
    # Save to all relevant config files
    config_files = {
        "agentverse_agents_1000.json": [sre_agent],
        "agents_config.json": [sre_agent],
        "agent_catalog.json": [sre_agent],
        "test_agent_sre_only.json": [sre_agent]
    }
    
    for filename, content in config_files.items():
        filepath = os.path.join(config_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        print(f"✅ Saved SRE agent to: {filename}")
    
    # Create a test tracking file
    test_info = {
        "agent_id": "sre_servicenow_001",
        "loaded_at": datetime.now().isoformat(),
        "purpose": "Single agent testing with OpenAI provider",
        "expected_tools": [
            "search_incidents",
            "create_incident",
            "update_incident", 
            "calculate_slo_status",
            "get_runbook"
        ],
        "test_scenarios": [
            "Search for critical incidents",
            "Create a new incident",
            "Update incident status",
            "Check SLO status for payment service",
            "Get runbook for high latency"
        ]
    }
    
    test_file = os.path.join(config_dir, "sre_agent_test_info.json")
    with open(test_file, 'w') as f:
        json.dump(test_info, f, indent=2)
    
    print(f"\n📋 Test tracking saved to: sre_agent_test_info.json")
    print("\n✨ SRE ServiceNow Specialist loaded successfully!")
    print(f"   Agent ID: {sre_agent['id']}")
    print(f"   Display Name: {sre_agent['enhanced_metadata']['display_name']}")
    print(f"   Tools: {', '.join(sre_agent['tools'])}")
    print(f"   Model: {sre_agent['model_preferences']['primary']}")
    
    print("\n🧪 Test Scenarios to Try:")
    for i, scenario in enumerate(test_info['test_scenarios'], 1):
        print(f"   {i}. {scenario}")
    
    print("\n💡 Next Steps:")
    print("1. Restart the API server to load the single agent")
    print("2. Test each tool function")
    print("3. Verify OpenAI integration is working")
    print("4. Check tool execution in agent responses")
    
    return sre_agent

if __name__ == "__main__":
    try:
        agent = load_single_sre_agent()
        print(f"\n🎯 Ready for focused testing with agent: {agent['id']}")
    except Exception as e:
        print(f"\n❌ Error loading SRE agent: {e}")
        import traceback
        traceback.print_exc()
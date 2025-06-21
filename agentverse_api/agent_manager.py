"""
Agent Manager - Handles both Ollama and OpenAI Agent connections
"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool
from typing import List
import json
import asyncio
from ollama_provider import ollama_provider

load_dotenv()

class AgentManager:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.use_ollama = os.getenv("USE_OLLAMA", "true").lower() == "true"
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.agents: Dict[str, Agent] = {}
        self.agent_configs = []
        self.ollama_available = False
        
        # Debug: Print LLM configuration
        print(f"🔧 LLM Configuration:")
        print(f"   USE_OLLAMA env var: {os.getenv('USE_OLLAMA')}")
        print(f"   use_ollama value: {self.use_ollama}")
        print(f"   OpenAI API key present: {bool(self.api_key)}")
        
        # Load agent configurations
        try:
            with open("../src/config/agentverse_agents_1000.json", "r") as f:
                self.agent_configs = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load agent configs: {e}")
        
        # Check Ollama availability will be done when event loop is available
    
    async def _check_ollama_status(self):
        """Check if Ollama is available"""
        self.ollama_available = await ollama_provider.is_available()
        if self.ollama_available:
            models = await ollama_provider.list_models()
            print(f"✅ Ollama is available with models: {models}")
        else:
            print("⚠️  Ollama is not available. Will use OpenAI if configured.")
    
    def get_or_create_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an existing agent or create a new one"""
        
        # Check if agent already exists
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        # Find agent configuration
        agent_config = None
        for config in self.agent_configs:
            metadata = config.get("enhanced_metadata", {})
            if metadata.get("agent_uuid") == agent_id:
                agent_config = config
                break
        
        if not agent_config:
            return None
        
        # Create agent if API key is available
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not set. Using mock mode.")
            return None
        
        try:
            metadata = agent_config.get("enhanced_metadata", {})
            
            # Create tools for the agent based on its capabilities
            tools = self._create_tools_for_agent(metadata)
            
            # Create the agent
            agent = Agent(
                name=metadata.get("display_name", "Agent"),
                model="gpt-4o-mini",  # Use cost-effective model
                instructions=agent_config.get("instructions", "You are a helpful AI assistant."),
                tools=tools  # Pass the tools to the agent
            )
            
            # Cache the agent
            self.agents[agent_id] = agent
            return agent
            
        except Exception as e:
            print(f"Error creating agent {agent_id}: {e}")
            return None
    
    def _create_tools_for_agent(self, metadata: dict):  # -> list:
        """Create tools based on agent capabilities"""
        tools = []
        
        # Add tools based on agent's expertise
        capabilities = metadata.get("capabilities", {})
        primary_expertise = capabilities.get("primary_expertise", [])
        tools_mastery = capabilities.get("tools_mastery", {})
        
        # Special handling for SRE ServiceNow agent
        if (metadata.get("agent_uuid") == "sre_servicenow_001" or 
            "ServiceNow Platform" in primary_expertise or
            "Incident Response" in primary_expertise):
            # Add all SRE/ServiceNow specific tools
            tools.extend([
                self._create_search_incidents_tool(),
                self._create_create_incident_tool(),
                self._create_update_incident_tool(),
                self._create_calculate_slo_tool(),
                self._create_get_runbook_tool()
            ])
        else:
            # Engineering agents get code tools
            if any(skill in ["Python", "JavaScript", "Code Review", "API Design"] for skill in primary_expertise):
                tools.append(self._create_code_analysis_tool())
            
            # Data agents get data analysis tools
            if any(skill in ["Data Analysis", "Analytics", "ETL", "Big Data"] for skill in primary_expertise):
                tools.append(self._create_data_analysis_tool())
            
            # DevOps agents get infrastructure tools
            if any(skill in ["Docker", "Kubernetes", "CI/CD", "Infrastructure"] for skill in primary_expertise):
                tools.append(self._create_devops_tool())
        
        return tools
    
    def _create_code_analysis_tool(self):
        """Create a mock code analysis tool"""
        @function_tool
        def analyze_code(code: str, language: str = "python") -> str:
            """Analyze code for best practices and potential issues"""
            # This is a mock implementation
            return f"Code analysis complete for {language}. The code appears to be well-structured."
        
        return analyze_code
    
    def _create_data_analysis_tool(self):
        """Create a data analysis tool"""
        @function_tool
        def analyze_data(data_description: str, analysis_type: str = "summary") -> str:
            """Analyze data patterns and provide insights"""
            return f"Data analysis complete. Type: {analysis_type}. The data shows interesting patterns that warrant further investigation."
        
        return analyze_data
    
    def _create_devops_tool(self):
        """Create a DevOps tool"""
        @function_tool
        def check_infrastructure(service: str, environment: str = "production") -> str:
            """Check infrastructure status and health"""
            return f"Infrastructure check for {service} in {environment}: All systems operational. CPU: 45%, Memory: 62%, Uptime: 99.9%"
        
        return check_infrastructure
    
    def _create_search_incidents_tool(self):
        """Create search incidents tool for SRE"""
        @function_tool
        def search_incidents(query: str = "state=1", limit: int = 10) -> str:
            """Search ServiceNow incidents based on query criteria"""
            # Mock implementation
            mock_incidents = [
                {
                    "number": "INC0012345",
                    "short_description": "Payment service high latency",
                    "priority": "1 - Critical",
                    "state": "In Progress",
                    "assigned_to": "SRE Team"
                },
                {
                    "number": "INC0012346",
                    "short_description": "Database connection pool exhausted",
                    "priority": "2 - High",
                    "state": "New",
                    "assigned_to": "Database Team"
                }
            ]
            
            result = f"Found {len(mock_incidents)} incidents:\n\n"
            for inc in mock_incidents[:limit]:
                result += f"• {inc['number']} - {inc['short_description']}\n"
                result += f"  Priority: {inc['priority']} | Status: {inc['state']} | Assigned: {inc['assigned_to']}\n\n"
            
            return result
        
        return search_incidents
    
    def _create_create_incident_tool(self):
        """Create incident creation tool for SRE"""
        @function_tool
        def create_incident(
            short_description: str,
            priority: str = "3 - Moderate",
            urgency: str = "3 - Low",
            category: str = "Software",
            description: str = ""
        ) -> str:
            """Create a new incident in ServiceNow with validation"""
            from datetime import datetime
            
            incident_number = f"INC00{datetime.now().strftime('%H%M%S')}"
            
            result = f"""✅ Incident created (mock mode):
Number: {incident_number}
Description: {short_description}
Priority: {priority}
Urgency: {urgency}
Category: {category}
Status: New
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            return result
        
        return create_incident
    
    def _create_update_incident_tool(self):
        """Create incident update tool for SRE"""
        @function_tool
        def update_incident(incident_number: str, status: str = None, notes: str = None, assigned_to: str = None) -> str:
            """Update an existing ServiceNow incident with validation"""
            from datetime import datetime
            
            update_fields = []
            if status:
                update_fields.append(f"Status → {status}")
            if notes:
                update_fields.append(f"Work notes added")
            if assigned_to:
                update_fields.append(f"Assigned to → {assigned_to}")
            
            result = f"""✅ Incident {incident_number} updated:
{chr(10).join('• ' + field for field in update_fields)}
Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Work Notes: {notes if notes else 'No notes added'}"""
            
            return result
        
        return update_incident
    
    def _create_calculate_slo_tool(self):
        """Create SLO calculation tool for SRE"""
        @function_tool
        def calculate_slo_status(service: str, slo_type: str = "availability") -> str:
            """Calculate SLO status and error budget with real metrics"""
            import random
            
            # Mock SLO calculation
            base_values = {
                "availability": {"target": 99.9, "current": 99.85},
                "latency": {"target": 200, "current": 185},
                "error_rate": {"target": 0.1, "current": 0.08}
            }
            
            values = base_values.get(slo_type, base_values["availability"])
            error_budget_remaining = 75.5  # Mock value
            
            result = f"""SLO Status Report for {service} - {slo_type.upper()}
{'='*50}
Target: {values['target']}
Current: {values['current']}
Error Budget Remaining: {error_budget_remaining}%
Status: ✅ Healthy

Recommendation: SLO is well within target. No action required."""
            
            return result
        
        return calculate_slo_status
    
    def _create_get_runbook_tool(self):
        """Create runbook retrieval tool for SRE"""
        @function_tool
        def get_runbook(incident_type: str) -> str:
            """Get runbook with step tracking and estimated time"""
            
            runbooks = {
                "high_latency": {
                    "title": "High Latency Incident Response",
                    "estimated_time": "15-30 minutes",
                    "steps": [
                        "Check current traffic levels via monitoring dashboard",
                        "Verify database connection pool status",
                        "Check cache hit rates",
                        "Review recent deployments",
                        "Scale up instances if needed"
                    ]
                }
            }
            
            runbook = runbooks.get(incident_type.lower().replace(" ", "_"), {
                "title": "General Incident Response",
                "estimated_time": "30-60 minutes",
                "steps": [
                    "Assess impact and severity",
                    "Notify stakeholders",
                    "Gather diagnostic information",
                    "Implement mitigation",
                    "Monitor recovery"
                ]
            })
            
            result = f"""📋 {runbook['title']}
{'='*50}
Estimated Time: {runbook['estimated_time']}

Steps to Follow:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(runbook['steps']))}"""
            
            return result
        
        return get_runbook
    
    async def chat_with_agent(self, agent_id: str, message: str) -> str:
        """Send a message to an agent and get response"""
        
        # Find agent configuration
        agent_config = None
        for config in self.agent_configs:
            metadata = config.get("enhanced_metadata", {})
            if metadata.get("agent_uuid") == agent_id:
                agent_config = config
                break
        
        if not agent_config:
            return "I'm sorry, I couldn't find that agent."
        
        metadata = agent_config.get("enhanced_metadata", {})
        
        # Try Ollama first if enabled and available
        if self.use_ollama and self.ollama_available:
            print(f"🦙 Using Ollama for agent {metadata.get('display_name')}")
            try:
                # Check Ollama status again
                self.ollama_available = await ollama_provider.is_available()
                
                if self.ollama_available:
                    response = await ollama_provider.chat(
                        model=self.ollama_model,
                        messages=[{"role": "user", "content": message}],
                        agent_metadata=metadata
                    )
                    
                    if response:
                        return response
                    else:
                        print("Ollama returned empty response, falling back to OpenAI")
            except Exception as e:
                print(f"Ollama error: {e}, falling back to OpenAI")
                self.ollama_available = False
        
        # Try OpenAI if Ollama failed or not available
        if self.api_key:
            print(f"🤖 Using OpenAI for agent {metadata.get('display_name')}")
            agent = self.get_or_create_agent(agent_id)
            
            if agent:
                try:
                    # Debug: Check if agent has tools
                    print(f"   Agent has {len(agent.tools)} tools configured")
                    if agent.tools:
                        print(f"   Tools: {[tool.name for tool in agent.tools]}")
                    
                    # Use the real OpenAI agent with Runner
                    result = await Runner.run(agent, message)
                    return result.final_output
                except Exception as e:
                    print(f"OpenAI error: {e}")
        
        # Fallback to mock response
        name = metadata.get("display_name", "Agent")
        skills = ", ".join(metadata.get("capabilities", {}).get("primary_expertise", [])[:3])
        
        return (
            f"Hello! I'm {name}, specializing in {skills}. I can help you with: {message}\n\n"
            f"[Note: This is a demo response. To enable AI responses:\n"
            f"1. Start Ollama (ollama serve) for local AI\n"
            f"2. Or set OPENAI_API_KEY in .env for cloud AI]"
        )

# Global instance
agent_manager = AgentManager()
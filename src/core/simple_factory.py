"""
Simplified agent factory that works with the openai-agents library API
"""
from agents import Agent, function_tool, set_default_openai_key
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
import json
import os


@dataclass
class SimpleAgentConfig:
    """Configuration for creating an agent"""
    name: str
    instructions: str
    model: str = "gpt-4o-mini"
    tools: List[Callable] = field(default_factory=list)
    handoffs: List[str] = field(default_factory=list)  # Names of agents to handoff to
    metadata: Dict[str, Any] = field(default_factory=dict)


class SimpleAgentFactory:
    """Factory for creating and managing agents"""
    
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._configs: Dict[str, SimpleAgentConfig] = {}
        self._tools: Dict[str, Callable] = {}
        
        # Set up OpenAI key if available
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            set_default_openai_key(api_key)
    
    def register_tool(self, name: str, func: Callable) -> None:
        """Register a reusable tool"""
        self._tools[name] = func
    
    def create_agent(self, config: SimpleAgentConfig) -> Agent:
        """Create an agent from configuration"""
        # Resolve handoff agents
        handoff_agents = []
        for handoff_name in config.handoffs:
            if handoff_name in self._agents:
                handoff_agents.append(self._agents[handoff_name])
        
        # Create the agent
        agent = Agent(
            name=config.name,
            instructions=config.instructions,
            model=config.model,
            tools=config.tools,
            handoffs=handoff_agents
        )
        
        # Store agent and config
        self._agents[config.name] = agent
        self._configs[config.name] = config
        
        return agent
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self._agents.get(name)
    
    def list_agents(self) -> List[str]:
        """List all registered agent names"""
        return list(self._agents.keys())
    
    def load_from_file(self, filepath: str) -> List[Agent]:
        """Load agents from a JSON configuration file"""
        with open(filepath, 'r') as f:
            configs = json.load(f)
        
        agents = []
        # First pass: create all agents without handoffs
        for config_dict in configs:
            # Skip handoffs in first pass
            handoffs = config_dict.pop('handoffs', [])
            config = SimpleAgentConfig(**config_dict)
            agent = self.create_agent(config)
            agents.append(agent)
        
        # Second pass: update handoffs
        for config_dict, agent in zip(configs, agents):
            if 'handoffs' in config_dict:
                handoff_agents = [
                    self._agents[name] 
                    for name in config_dict['handoffs'] 
                    if name in self._agents
                ]
                if handoff_agents:
                    agent.handoffs = handoff_agents
        
        return agents
    
    def export_config(self, agent_name: str) -> Dict[str, Any]:
        """Export agent configuration as dictionary"""
        if agent_name not in self._configs:
            return {}
        
        config = self._configs[agent_name]
        return {
            "name": config.name,
            "instructions": config.instructions,
            "model": config.model,
            "handoffs": config.handoffs,
            "metadata": config.metadata
        }
    
    def export_all_configs(self) -> List[Dict[str, Any]]:
        """Export all agent configurations"""
        return [self.export_config(name) for name in self.list_agents()]


# Convenience function to create common tools
def create_calculator_tool():
    """Create a calculator tool"""
    import math
    
    @function_tool
    def calculate(expression: str) -> str:
        """Evaluate a mathematical expression"""
        try:
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return f"The result is: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    return calculate


def create_file_reader_tool():
    """Create a file reader tool"""
    @function_tool
    def read_file(filepath: str) -> str:
        """Read contents of a file"""
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    return read_file
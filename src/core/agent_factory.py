from agents import Agent, function_tool
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from ..providers import BaseLLMProvider, ProviderConfig, OpenAIProvider, OllamaProvider
import json


@dataclass
class AgentConfig:
    name: str
    instructions: str
    provider: str = "openai"
    model: str = "gpt-4"
    tools: List[Callable] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tools is None:
            self.tools = []
        if self.metadata is None:
            self.metadata = {}


class AgentFactory:
    PROVIDER_MAPPING = {
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
    }

    def __init__(self):
        self._providers: Dict[str, BaseLLMProvider] = {}
        self._agents: Dict[str, Agent] = {}

    def register_provider(self, name: str, config: ProviderConfig) -> None:
        provider_class = self.PROVIDER_MAPPING.get(config.name)
        if not provider_class:
            raise ValueError(f"Unknown provider: {config.name}")
        
        provider = provider_class(config)
        provider.initialize()
        self._providers[name] = provider

    def create_agent(self, config: AgentConfig) -> Agent:
        provider = self._providers.get(config.provider)
        if not provider:
            raise ValueError(f"Provider {config.provider} not registered")

        client = provider.get_client()
        model_params = provider.get_model_params()
        
        # Override model if specified in agent config
        if config.model != model_params.get("model"):
            model_params["model"] = config.model

        # Agent doesn't take client parameter, model is set differently
        agent = Agent(
            name=config.name,
            instructions=config.instructions,
            tools=config.tools if config.tools else [],
            model=config.model
        )

        self._agents[config.name] = agent
        return agent

    def get_agent(self, name: str) -> Optional[Agent]:
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())

    def load_agents_from_file(self, filepath: str) -> List[Agent]:
        with open(filepath, 'r') as f:
            configs = json.load(f)
        
        agents = []
        for config_dict in configs:
            config = AgentConfig(**config_dict)
            agent = self.create_agent(config)
            agents.append(agent)
        
        return agents
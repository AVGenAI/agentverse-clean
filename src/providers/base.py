from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ProviderConfig:
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    extra_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


class BaseLLMProvider(ABC):
    def __init__(self, config: ProviderConfig):
        self.config = config
        self._client = None

    @abstractmethod
    def initialize(self):
        pass

    @abstractmethod
    def get_client(self):
        pass

    @abstractmethod
    def get_model_params(self) -> Dict[str, Any]:
        pass
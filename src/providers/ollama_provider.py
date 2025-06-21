from openai import OpenAI
from typing import Dict, Any
from .base import BaseLLMProvider, ProviderConfig


class OllamaProvider(BaseLLMProvider):
    def initialize(self):
        base_url = self.config.base_url or "http://localhost:11434/v1"
        self._client = OpenAI(
            api_key="ollama",  # Ollama doesn't need a real API key
            base_url=base_url
        )

    def get_client(self):
        if not self._client:
            self.initialize()
        return self._client

    def get_model_params(self) -> Dict[str, Any]:
        params = {
            "model": self.config.model,
            "temperature": self.config.temperature,
        }
        if self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens
        
        params.update(self.config.extra_params)
        return params
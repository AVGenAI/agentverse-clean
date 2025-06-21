"""
Ollama Provider - Local LLM support for AgentVerse
"""
import os
import httpx
from typing import Optional, Dict, Any
import json

class OllamaProvider:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("OLLAMA_MODEL", "llama2")
        self.timeout = 30.0
        
    async def is_available(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=2.0)
                return response.status_code == 200
        except:
            return False
    
    async def list_models(self) -> list:
        """List available Ollama models"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    return [model["name"] for model in data.get("models", [])]
        except:
            pass
        return []
    
    async def chat(self, model: str, messages: list, agent_metadata: dict = None) -> Optional[str]:
        """Send chat request to Ollama"""
        try:
            # Format messages for Ollama
            formatted_messages = []
            
            # Add system message with agent personality
            if agent_metadata:
                system_prompt = self._create_system_prompt(agent_metadata)
                formatted_messages.append({
                    "role": "system",
                    "content": system_prompt
                })
            
            # Add conversation messages
            for msg in messages:
                formatted_messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
            
            # Prepare request
            request_data = {
                "model": model or self.default_model,
                "messages": formatted_messages,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                }
            }
            
            # Send request to Ollama
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("message", {}).get("content", "")
                else:
                    print(f"Ollama error: {response.status_code} - {response.text}")
                    
        except httpx.ConnectError:
            print("Ollama is not running. Please start Ollama to use local models.")
        except httpx.ReadTimeout:
            print("Ollama request timed out. The model might be loading.")
        except Exception as e:
            print(f"Ollama error: {e}")
        
        return None
    
    def _create_system_prompt(self, metadata: dict) -> str:
        """Create a system prompt based on agent metadata"""
        name = metadata.get("display_name", "AI Assistant")
        expertise = metadata.get("capabilities", {}).get("primary_expertise", [])
        
        prompt = f"You are {name}, an AI agent specializing in {', '.join(expertise[:3])}."
        
        # Add role-specific instructions
        if "Python" in expertise or "JavaScript" in expertise:
            prompt += " You provide helpful code examples and technical guidance."
        elif "Data" in expertise or "Analytics" in expertise:
            prompt += " You help analyze data patterns and provide insights."
        elif "DevOps" in expertise or "Infrastructure" in expertise:
            prompt += " You assist with deployment, infrastructure, and operations."
        
        prompt += " Be helpful, concise, and professional."
        
        return prompt

# Global instance
ollama_provider = OllamaProvider()
#!/usr/bin/env python3
"""
ServiceNow Configuration Loader
Loads ServiceNow configuration from environment variables
"""

import os
from typing import Dict, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class ServiceNowConfig:
    """ServiceNow configuration settings"""
    instance_url: str
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    api_token: Optional[str] = None
    api_version: str = "v2"
    timeout: int = 30
    max_retries: int = 3
    mcp_port: int = 8080
    
    @property
    def auth_method(self) -> str:
        """Determine authentication method"""
        if self.api_token:
            return "token"
        elif self.client_id and self.client_secret:
            return "oauth"
        elif self.username and self.password:
            return "basic"
        else:
            return "none"
    
    @property
    def is_configured(self) -> bool:
        """Check if ServiceNow is properly configured"""
        return bool(self.instance_url) and self.auth_method != "none"
    
    @property
    def api_endpoint(self) -> str:
        """Get the API endpoint URL"""
        if not self.instance_url:
            return ""
        url = self.instance_url.rstrip('/')
        return f"{url}/api/now/{self.api_version}"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers based on auth method"""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        if self.auth_method == "token":
            headers["Authorization"] = f"Bearer {self.api_token}"
        elif self.auth_method == "basic":
            import base64
            credentials = f"{self.username}:{self.password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        return headers
    
    def to_mcp_env(self) -> Dict[str, str]:
        """Convert to environment variables for MCP server"""
        env = {
            "SERVICENOW_INSTANCE_URL": self.instance_url or "",
            "SERVICENOW_API_VERSION": self.api_version,
            "SERVICENOW_TIMEOUT": str(self.timeout),
            "SERVICENOW_MAX_RETRIES": str(self.max_retries),
            "SERVICENOW_MCP_PORT": str(self.mcp_port)
        }
        
        if self.username:
            env["SERVICENOW_USERNAME"] = self.username
        if self.password:
            env["SERVICENOW_PASSWORD"] = self.password
        if self.client_id:
            env["SERVICENOW_CLIENT_ID"] = self.client_id
        if self.client_secret:
            env["SERVICENOW_CLIENT_SECRET"] = self.client_secret
        if self.api_token:
            env["SERVICENOW_API_TOKEN"] = self.api_token
        
        return env

def load_servicenow_config() -> ServiceNowConfig:
    """Load ServiceNow configuration from environment variables"""
    return ServiceNowConfig(
        instance_url=os.getenv("SERVICENOW_INSTANCE_URL", ""),
        username=os.getenv("SERVICENOW_USERNAME"),
        password=os.getenv("SERVICENOW_PASSWORD"),
        client_id=os.getenv("SERVICENOW_CLIENT_ID"),
        client_secret=os.getenv("SERVICENOW_CLIENT_SECRET"),
        api_token=os.getenv("SERVICENOW_API_TOKEN"),
        api_version=os.getenv("SERVICENOW_API_VERSION", "v2"),
        timeout=int(os.getenv("SERVICENOW_TIMEOUT", "30")),
        max_retries=int(os.getenv("SERVICENOW_MAX_RETRIES", "3")),
        mcp_port=int(os.getenv("SERVICENOW_MCP_PORT", "8080"))
    )

def validate_config() -> tuple[bool, str]:
    """Validate ServiceNow configuration"""
    config = load_servicenow_config()
    
    if not config.instance_url:
        return False, "SERVICENOW_INSTANCE_URL is not set"
    
    if not config.instance_url.startswith(("http://", "https://")):
        return False, "SERVICENOW_INSTANCE_URL must start with http:// or https://"
    
    if config.auth_method == "none":
        return False, "No authentication method configured. Set either username/password, OAuth credentials, or API token"
    
    return True, f"ServiceNow configured with {config.auth_method} authentication"

# Example usage
if __name__ == "__main__":
    config = load_servicenow_config()
    
    print("ServiceNow Configuration Status:")
    print("-" * 50)
    
    if config.is_configured:
        print(f"✅ Instance URL: {config.instance_url}")
        print(f"✅ Auth Method: {config.auth_method}")
        print(f"✅ API Endpoint: {config.api_endpoint}")
        print(f"✅ API Version: {config.api_version}")
        print(f"✅ MCP Port: {config.mcp_port}")
    else:
        print("❌ ServiceNow is not configured")
        print("\nPlease set the following in your .env file:")
        print("  SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com")
        print("  And one of:")
        print("    - SERVICENOW_USERNAME and SERVICENOW_PASSWORD")
        print("    - SERVICENOW_CLIENT_ID and SERVICENOW_CLIENT_SECRET")
        print("    - SERVICENOW_API_TOKEN")
    
    # Validate configuration
    valid, message = validate_config()
    print(f"\nValidation: {'✅' if valid else '❌'} {message}")
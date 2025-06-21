"""
Environment variable loader for ServiceNow and other configurations.
Loads variables from .env file and provides easy access to configuration values.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class EnvConfig:
    """Configuration loader for environment variables."""
    
    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize the environment configuration loader.
        
        Args:
            env_file: Path to .env file. If None, looks for .env in current directory.
        """
        if env_file:
            load_dotenv(env_file)
        else:
            # Look for .env file in the same directory as this script
            env_path = Path(__file__).parent / '.env'
            if env_path.exists():
                load_dotenv(env_path)
            else:
                # Try loading from current working directory
                load_dotenv()
    
    # AI Provider Configuration
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key."""
        return os.getenv('OPENAI_API_KEY')
    
    @property
    def ollama_base_url(self) -> str:
        """Get Ollama base URL."""
        return os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    @property
    def vllm_base_url(self) -> str:
        """Get VLLM base URL."""
        return os.getenv('VLLM_BASE_URL', 'http://localhost:8000')
    
    @property
    def mcp_server_url(self) -> str:
        """Get MCP server URL."""
        return os.getenv('MCP_SERVER_URL', 'http://localhost:3000')
    
    # ServiceNow Configuration
    @property
    def servicenow_instance(self) -> Optional[str]:
        """Get ServiceNow instance name."""
        return os.getenv('SERVICENOW_INSTANCE')
    
    @property
    def servicenow_username(self) -> Optional[str]:
        """Get ServiceNow username."""
        return os.getenv('SERVICENOW_USERNAME')
    
    @property
    def servicenow_password(self) -> Optional[str]:
        """Get ServiceNow password."""
        return os.getenv('SERVICENOW_PASSWORD')
    
    @property
    def servicenow_api_endpoint(self) -> Optional[str]:
        """Get ServiceNow API endpoint."""
        endpoint = os.getenv('SERVICENOW_API_ENDPOINT')
        if endpoint and '${SERVICENOW_INSTANCE}' in endpoint and self.servicenow_instance:
            # Replace placeholder with actual instance name
            endpoint = endpoint.replace('${SERVICENOW_INSTANCE}', self.servicenow_instance)
        return endpoint
    
    @property
    def servicenow_api_version(self) -> str:
        """Get ServiceNow API version."""
        return os.getenv('SERVICENOW_API_VERSION', 'v1')
    
    # ServiceNow OAuth
    @property
    def servicenow_client_id(self) -> Optional[str]:
        """Get ServiceNow OAuth client ID."""
        return os.getenv('SERVICENOW_CLIENT_ID')
    
    @property
    def servicenow_client_secret(self) -> Optional[str]:
        """Get ServiceNow OAuth client secret."""
        return os.getenv('SERVICENOW_CLIENT_SECRET')
    
    # ServiceNow Tables
    @property
    def servicenow_incident_table(self) -> str:
        """Get ServiceNow incident table name."""
        return os.getenv('SERVICENOW_INCIDENT_TABLE', 'incident')
    
    @property
    def servicenow_user_table(self) -> str:
        """Get ServiceNow user table name."""
        return os.getenv('SERVICENOW_USER_TABLE', 'sys_user')
    
    @property
    def servicenow_cmdb_table(self) -> str:
        """Get ServiceNow CMDB table name."""
        return os.getenv('SERVICENOW_CMDB_TABLE', 'cmdb_ci')
    
    # Other Settings
    @property
    def servicenow_timeout(self) -> int:
        """Get ServiceNow request timeout in seconds."""
        return int(os.getenv('SERVICENOW_TIMEOUT', '30'))
    
    @property
    def servicenow_max_retries(self) -> int:
        """Get ServiceNow maximum retry attempts."""
        return int(os.getenv('SERVICENOW_MAX_RETRIES', '3'))
    
    @property
    def servicenow_log_level(self) -> str:
        """Get ServiceNow log level."""
        return os.getenv('SERVICENOW_LOG_LEVEL', 'INFO')
    
    def get_servicenow_config(self) -> Dict[str, Any]:
        """
        Get all ServiceNow configuration as a dictionary.
        
        Returns:
            Dictionary containing all ServiceNow configuration values.
        """
        return {
            'instance': self.servicenow_instance,
            'username': self.servicenow_username,
            'password': self.servicenow_password,
            'api_endpoint': self.servicenow_api_endpoint,
            'api_version': self.servicenow_api_version,
            'client_id': self.servicenow_client_id,
            'client_secret': self.servicenow_client_secret,
            'tables': {
                'incident': self.servicenow_incident_table,
                'user': self.servicenow_user_table,
                'cmdb': self.servicenow_cmdb_table
            },
            'timeout': self.servicenow_timeout,
            'max_retries': self.servicenow_max_retries,
            'log_level': self.servicenow_log_level
        }
    
    def validate_servicenow_config(self) -> tuple[bool, list[str]]:
        """
        Validate that required ServiceNow configuration is present.
        
        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []
        
        # Check required fields
        if not self.servicenow_instance:
            missing_fields.append('SERVICENOW_INSTANCE')
        if not self.servicenow_username:
            missing_fields.append('SERVICENOW_USERNAME')
        if not self.servicenow_password:
            missing_fields.append('SERVICENOW_PASSWORD')
        
        return len(missing_fields) == 0, missing_fields
    
    def __repr__(self) -> str:
        """String representation of the configuration."""
        return f"EnvConfig(servicenow_instance={self.servicenow_instance})"


# Convenience function for quick access
def load_env_config(env_file: Optional[str] = None) -> EnvConfig:
    """
    Load environment configuration.
    
    Args:
        env_file: Optional path to .env file.
    
    Returns:
        EnvConfig instance with loaded configuration.
    """
    return EnvConfig(env_file)


# Example usage
if __name__ == "__main__":
    # Load configuration
    config = load_env_config()
    
    # Check if ServiceNow is configured
    is_valid, missing = config.validate_servicenow_config()
    
    if is_valid:
        print("ServiceNow configuration is valid!")
        print(f"Instance: {config.servicenow_instance}")
        print(f"API Endpoint: {config.servicenow_api_endpoint}")
        print(f"Timeout: {config.servicenow_timeout} seconds")
    else:
        print("ServiceNow configuration is incomplete.")
        print(f"Missing fields: {', '.join(missing)}")
        print("\nPlease copy .env.example to .env and fill in the required values.")
    
    # Display all ServiceNow config
    print("\nServiceNow Configuration:")
    for key, value in config.get_servicenow_config().items():
        if key == 'password' and value:
            print(f"  {key}: ***hidden***")
        else:
            print(f"  {key}: {value}")
#!/usr/bin/env python3
"""
Example script demonstrating how to use the environment variable loader
for ServiceNow integration.
"""

from env_loader import load_env_config
import requests
from requests.auth import HTTPBasicAuth


def test_servicenow_connection():
    """Test connection to ServiceNow using loaded configuration."""
    # Load configuration
    config = load_env_config()
    
    # Validate configuration
    is_valid, missing = config.validate_servicenow_config()
    if not is_valid:
        print(f"Error: Missing required configuration: {', '.join(missing)}")
        print("Please copy .env.example to .env and fill in the required values.")
        return
    
    print(f"Connecting to ServiceNow instance: {config.servicenow_instance}")
    
    # Example: Get incidents from ServiceNow
    try:
        # Build the URL
        url = f"{config.servicenow_api_endpoint}/now/table/{config.servicenow_incident_table}"
        
        # Set up authentication
        auth = HTTPBasicAuth(config.servicenow_username, config.servicenow_password)
        
        # Set headers
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Make request with timeout
        response = requests.get(
            url,
            auth=auth,
            headers=headers,
            timeout=config.servicenow_timeout,
            params={'sysparm_limit': 1}  # Just get one record for testing
        )
        
        if response.status_code == 200:
            print("Successfully connected to ServiceNow!")
            data = response.json()
            print(f"Found {len(data.get('result', []))} incident(s)")
        else:
            print(f"Failed to connect: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def display_configuration():
    """Display current configuration (with sensitive data hidden)."""
    config = load_env_config()
    
    print("\nCurrent Configuration:")
    print("-" * 50)
    
    # AI Provider config
    print("\nAI Providers:")
    print(f"  OpenAI API Key: {'***' + config.openai_api_key[-4:] if config.openai_api_key else 'Not set'}")
    print(f"  Ollama URL: {config.ollama_base_url}")
    print(f"  VLLM URL: {config.vllm_base_url}")
    print(f"  MCP Server URL: {config.mcp_server_url}")
    
    # ServiceNow config
    print("\nServiceNow:")
    servicenow_config = config.get_servicenow_config()
    for key, value in servicenow_config.items():
        if key in ['password', 'client_secret'] and value:
            print(f"  {key}: ***hidden***")
        elif key == 'tables' and isinstance(value, dict):
            print(f"  {key}:")
            for table_key, table_value in value.items():
                print(f"    {table_key}: {table_value}")
        else:
            print(f"  {key}: {value}")


if __name__ == "__main__":
    print("Environment Variable Loader Example")
    print("=" * 50)
    
    # Display current configuration
    display_configuration()
    
    # Test ServiceNow connection (uncomment to test)
    # print("\n\nTesting ServiceNow Connection:")
    # print("-" * 50)
    # test_servicenow_connection()
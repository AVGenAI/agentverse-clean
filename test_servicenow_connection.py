#!/usr/bin/env python3
"""
Test ServiceNow Connection
Verifies that the ServiceNow credentials are working
"""

import asyncio
import aiohttp
import json
from servicenow_config_loader import load_servicenow_config

async def test_servicenow_connection():
    """Test connection to ServiceNow instance"""
    config = load_servicenow_config()
    
    print("🔌 Testing ServiceNow Connection")
    print("="*50)
    
    # Check configuration
    if not config.is_configured:
        print("❌ ServiceNow is not properly configured")
        return False
    
    print(f"Instance: {config.instance_url}")
    print(f"Auth Method: {config.auth_method}")
    print(f"Username: {config.username}")
    print(f"API Endpoint: {config.api_endpoint}")
    
    # Test API connection
    print("\n🔍 Testing API Connection...")
    
    try:
        # Test with a simple API call - get incidents table info
        test_url = f"{config.api_endpoint}/table/incident?sysparm_limit=1"
        headers = config.get_auth_headers()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(test_url, headers=headers, ssl=True) as response:
                print(f"Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Successfully connected to ServiceNow!")
                    print(f"✅ Retrieved {len(data.get('result', []))} incident(s)")
                    return True
                elif response.status == 401:
                    print("❌ Authentication failed - check username/password")
                    return False
                else:
                    text = await response.text()
                    print(f"❌ Connection failed with status {response.status}")
                    print(f"Response: {text[:200]}...")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_servicenow_tables():
    """Test access to common ServiceNow tables"""
    config = load_servicenow_config()
    
    if not config.is_configured:
        return
    
    print("\n📊 Testing Table Access...")
    print("-"*50)
    
    tables_to_test = [
        ("incident", "Incident Management"),
        ("change_request", "Change Management"),
        ("problem", "Problem Management"),
        ("kb_knowledge", "Knowledge Base"),
        ("sys_user", "User Table")
    ]
    
    headers = config.get_auth_headers()
    
    async with aiohttp.ClientSession() as session:
        for table, description in tables_to_test:
            try:
                url = f"{config.api_endpoint}/table/{table}?sysparm_limit=1"
                async with session.get(url, headers=headers, ssl=True) as response:
                    if response.status == 200:
                        print(f"✅ {description} ({table}): Accessible")
                    else:
                        print(f"❌ {description} ({table}): Status {response.status}")
            except Exception as e:
                print(f"❌ {description} ({table}): Error - {str(e)[:50]}")

async def main():
    """Main test function"""
    # Test connection
    success = await test_servicenow_connection()
    
    if success:
        # Test table access
        await test_servicenow_tables()
        
        print("\n✨ ServiceNow configuration is working correctly!")
        print("You can now use the ServiceNow MCP server with your agents.")
    else:
        print("\n⚠️  Please check your ServiceNow credentials in the .env file")

if __name__ == "__main__":
    asyncio.run(main())
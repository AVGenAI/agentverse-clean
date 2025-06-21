#!/usr/bin/env python3
"""
Test script for Pipeline API
"""
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_pipeline_api():
    print("Testing Pipeline API...")
    
    # 1. Get node types
    print("\n1. Getting node types...")
    response = requests.get(f"{API_URL}/api/pipeline/node-types")
    if response.status_code == 200:
        node_types = response.json()
        print(f"✓ Found {len(node_types['node_types'])} node types")
        for nt in node_types['node_types']:
            print(f"  - {nt['type']}: {nt['label']}")
    else:
        print(f"✗ Failed to get node types: {response.status_code}")
        return
    
    # 2. Create a pipeline
    print("\n2. Creating a test pipeline...")
    pipeline_data = {
        "name": "Test Pipeline",
        "description": "A simple test pipeline",
        "nodes": [
            {
                "id": "input-1",
                "type": "input",
                "label": "User Input",
                "position": {"x": 100, "y": 200},
                "config": {}
            },
            {
                "id": "text-1",
                "type": "text",
                "label": "Text Processor",
                "position": {"x": 300, "y": 200},
                "config": {"operation": "uppercase"}
            },
            {
                "id": "output-1",
                "type": "output",
                "label": "Result",
                "position": {"x": 500, "y": 200},
                "config": {}
            }
        ],
        "connections": [
            {"from": "input-1", "to": "text-1"},
            {"from": "text-1", "to": "output-1"}
        ]
    }
    
    response = requests.post(f"{API_URL}/api/pipeline/pipelines", json=pipeline_data)
    if response.status_code == 200:
        pipeline = response.json()
        pipeline_id = pipeline['id']
        print(f"✓ Created pipeline: {pipeline_id}")
    else:
        print(f"✗ Failed to create pipeline: {response.status_code}")
        print(response.text)
        return
    
    # 3. Validate pipeline
    print("\n3. Validating pipeline...")
    response = requests.post(f"{API_URL}/api/pipeline/pipelines/{pipeline_id}/validate")
    if response.status_code == 200:
        validation = response.json()
        if validation['valid']:
            print("✓ Pipeline is valid")
        else:
            print(f"✗ Pipeline has issues: {validation['issues']}")
    else:
        print(f"✗ Failed to validate pipeline: {response.status_code}")
    
    # 4. Execute pipeline
    print("\n4. Executing pipeline...")
    execute_data = {
        "input_data": "hello world",
        "config": {}
    }
    
    response = requests.post(f"{API_URL}/api/pipeline/pipelines/{pipeline_id}/execute", json=execute_data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Pipeline executed successfully")
        print(f"  Input: hello world")
        print(f"  Output: {result.get('output')}")
        print(f"  Status: {result.get('status')}")
    else:
        print(f"✗ Failed to execute pipeline: {response.status_code}")
        print(response.text)
    
    # 5. List pipelines
    print("\n5. Listing pipelines...")
    response = requests.get(f"{API_URL}/api/pipeline/pipelines")
    if response.status_code == 200:
        pipelines = response.json()
        print(f"✓ Found {len(pipelines['pipelines'])} pipelines")
        for p in pipelines['pipelines']:
            print(f"  - {p['name']} ({p['id']})")
    else:
        print(f"✗ Failed to list pipelines: {response.status_code}")
    
    print("\n✅ Pipeline API test completed!")

if __name__ == "__main__":
    test_pipeline_api()
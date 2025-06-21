"""
Pipeline API Router
Handles pipeline creation, execution, and management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sys
import os
from datetime import datetime

# Try to import pipeline_engine, but handle import errors gracefully
try:
    # Add parent directory to path
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from pipeline_engine import PipelineEngine, Pipeline, PipelineNode, NodeType
    PIPELINE_ENGINE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import pipeline_engine: {e}")
    PIPELINE_ENGINE_AVAILABLE = False
    # Create dummy classes to prevent router from failing
    class NodeType:
        INPUT = "input"
        OUTPUT = "output"
        AGENT = "agent"
        MCP_SERVER = "mcp_server"
        DATABASE = "database"
        API = "api"
        TEXT_PROCESSOR = "text"
        MEMORY = "memory"
        CHAT = "chat"
        PIPELINE = "pipeline"

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])

# Global pipeline engine instance
if PIPELINE_ENGINE_AVAILABLE:
    pipeline_engine = PipelineEngine()
else:
    pipeline_engine = None


class NodeCreate(BaseModel):
    id: str
    type: str
    label: str
    position: Dict[str, float]
    config: Optional[Dict[str, Any]] = {}


class ConnectionCreate(BaseModel):
    from_id: str = None
    to_id: str = None
    
    class Config:
        fields = {
            "from_id": "from",
            "to_id": "to"
        }


class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    nodes: List[NodeCreate]
    connections: List[Dict[str, str]]


class PipelineUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[NodeCreate]] = None
    connections: Optional[List[Dict[str, str]]] = None


class PipelineExecute(BaseModel):
    input_data: Any
    config: Optional[Dict[str, Any]] = {}


@router.get("/pipelines")
async def list_pipelines():
    """List all pipelines"""
    if not PIPELINE_ENGINE_AVAILABLE or not pipeline_engine:
        raise HTTPException(
            status_code=503, 
            detail="Pipeline engine is not available. Check server logs for import errors."
        )
    return {
        "pipelines": pipeline_engine.list_pipelines()
    }


@router.post("/pipelines")
async def create_pipeline(pipeline_data: PipelineCreate):
    """Create a new pipeline"""
    try:
        # Create pipeline
        pipeline = pipeline_engine.create_pipeline(
            name=pipeline_data.name,
            description=pipeline_data.description
        )
        
        # Add nodes
        for node_data in pipeline_data.nodes:
            node = PipelineNode(
                node_id=node_data.id,
                node_type=NodeType(node_data.type),
                config=node_data.config
            )
            node.position = node_data.position
            node.label = node_data.label
            pipeline.add_node(node)
        
        # Add connections
        for conn in pipeline_data.connections:
            pipeline.add_connection(conn["from"], conn["to"])
        
        # Save pipeline
        pipeline_engine.save_pipeline(pipeline)
        
        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "description": pipeline.description,
            "created_at": pipeline.created_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pipelines/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    """Get pipeline details"""
    pipeline = pipeline_engine.get_pipeline(pipeline_id)
    if not pipeline:
        # Try loading from storage
        pipeline = pipeline_engine.load_pipeline(pipeline_id)
        
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return pipeline.to_dict()


@router.put("/pipelines/{pipeline_id}")
async def update_pipeline(pipeline_id: str, update_data: PipelineUpdate):
    """Update an existing pipeline"""
    pipeline = pipeline_engine.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    try:
        # Update basic info
        if update_data.name:
            pipeline.name = update_data.name
        if update_data.description is not None:
            pipeline.description = update_data.description
        
        # Update nodes if provided
        if update_data.nodes is not None:
            pipeline.nodes.clear()
            for node_data in update_data.nodes:
                node = PipelineNode(
                    node_id=node_data.id,
                    node_type=NodeType(node_data.type),
                    config=node_data.config
                )
                node.position = node_data.position
                node.label = node_data.label
                pipeline.add_node(node)
        
        # Update connections if provided
        if update_data.connections is not None:
            pipeline.connections.clear()
            # Reset node connections
            for node in pipeline.nodes.values():
                node.inputs.clear()
                node.outputs.clear()
            # Add new connections
            for conn in update_data.connections:
                pipeline.add_connection(conn["from"], conn["to"])
        
        # Save updated pipeline
        pipeline_engine.save_pipeline(pipeline)
        
        return {
            "id": pipeline.id,
            "name": pipeline.name,
            "description": pipeline.description,
            "updated_at": pipeline.updated_at.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/pipelines/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Delete a pipeline"""
    if pipeline_id not in pipeline_engine.pipelines:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    del pipeline_engine.pipelines[pipeline_id]
    
    # Delete from storage
    try:
        os.remove(f"pipelines/{pipeline_id}.json")
    except FileNotFoundError:
        pass
    
    return {"message": "Pipeline deleted successfully"}


@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str, 
    execute_data: PipelineExecute,
    background_tasks: BackgroundTasks
):
    """Execute a pipeline"""
    pipeline = pipeline_engine.get_pipeline(pipeline_id)
    if not pipeline:
        # Try loading from storage
        pipeline = pipeline_engine.load_pipeline(pipeline_id)
        
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    try:
        # Execute pipeline (for now synchronously, can be made async with background tasks)
        execution = await pipeline_engine.execute_pipeline(
            pipeline_id,
            execute_data.input_data
        )
        
        return execution
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution(execution_id: str):
    """Get execution details"""
    execution = pipeline_engine.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return execution


@router.post("/pipelines/{pipeline_id}/validate")
async def validate_pipeline(pipeline_id: str):
    """Validate a pipeline configuration"""
    pipeline = pipeline_engine.get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    issues = []
    
    # Check for input nodes
    input_nodes = [n for n in pipeline.nodes.values() if n.type == NodeType.INPUT]
    if not input_nodes:
        issues.append("Pipeline has no input nodes")
    
    # Check for output nodes
    output_nodes = [n for n in pipeline.nodes.values() if n.type == NodeType.OUTPUT]
    if not output_nodes:
        issues.append("Pipeline has no output nodes")
    
    # Check for disconnected nodes
    for node_id, node in pipeline.nodes.items():
        if node.type != NodeType.INPUT and not node.inputs:
            issues.append(f"Node {node.label} has no inputs")
        if node.type != NodeType.OUTPUT and not node.outputs:
            issues.append(f"Node {node.label} has no outputs")
    
    # Check for cycles
    try:
        pipeline.get_execution_order()
    except RecursionError:
        issues.append("Pipeline contains cycles")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues
    }


@router.get("/node-types")
async def get_node_types():
    """Get available node types and their configurations"""
    return {
        "node_types": [
            {
                "type": "input",
                "label": "Input",
                "description": "Pipeline input node",
                "icon": "Upload",
                "color": "text-green-400",
                "bgColor": "bg-green-600/20",
                "config_schema": {}
            },
            {
                "type": "output",
                "label": "Output",
                "description": "Pipeline output node",
                "icon": "Download",
                "color": "text-red-400",
                "bgColor": "bg-red-600/20",
                "config_schema": {}
            },
            {
                "type": "agent",
                "label": "AI Agent",
                "description": "AgentVerse AI agent",
                "icon": "Brain",
                "color": "text-purple-400",
                "bgColor": "bg-purple-600/20",
                "config_schema": {
                    "agent_id": {
                        "type": "string",
                        "required": True,
                        "description": "Agent ID to use"
                    },
                    "model": {
                        "type": "string",
                        "required": False,
                        "description": "LLM model override"
                    }
                }
            },
            {
                "type": "mcp_server",
                "label": "MCP Server",
                "description": "Model Context Protocol server",
                "icon": "Server",
                "color": "text-orange-400",
                "bgColor": "bg-orange-600/20",
                "config_schema": {
                    "server_name": {
                        "type": "string",
                        "required": True,
                        "description": "MCP server name"
                    },
                    "tool_name": {
                        "type": "string",
                        "required": True,
                        "description": "Tool to execute"
                    }
                }
            },
            {
                "type": "database",
                "label": "Database",
                "description": "Database query node",
                "icon": "Database",
                "color": "text-blue-400",
                "bgColor": "bg-blue-600/20",
                "config_schema": {
                    "query": {
                        "type": "string",
                        "required": True,
                        "description": "SQL query to execute"
                    }
                }
            },
            {
                "type": "text",
                "label": "Text Processor",
                "description": "Text transformation node",
                "icon": "FileText",
                "color": "text-yellow-400",
                "bgColor": "bg-yellow-600/20",
                "config_schema": {
                    "operation": {
                        "type": "enum",
                        "required": True,
                        "options": ["uppercase", "lowercase", "reverse", "word_count"],
                        "description": "Text operation"
                    }
                }
            },
            {
                "type": "api",
                "label": "API Call",
                "description": "External API call",
                "icon": "Globe",
                "color": "text-cyan-400",
                "bgColor": "bg-cyan-600/20",
                "config_schema": {
                    "endpoint": {
                        "type": "string",
                        "required": True,
                        "description": "API endpoint URL"
                    },
                    "method": {
                        "type": "enum",
                        "required": True,
                        "options": ["GET", "POST", "PUT", "DELETE"],
                        "description": "HTTP method"
                    }
                }
            },
            {
                "type": "code",
                "label": "Code Execution",
                "description": "Execute custom Python code",
                "icon": "Code",
                "color": "text-pink-400",
                "bgColor": "bg-pink-600/20",
                "config_schema": {
                    "code": {
                        "type": "string",
                        "required": True,
                        "description": "Python code to execute"
                    }
                }
            }
        ]
    }
"""
Pipeline Engine for AgentVerse
Executes visual pipelines with agents, MCP servers, and tools
"""
import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
import logging

from agent_manager import AgentManager
from integrated_agent_manager import IntegratedAgentManager
from agent_mcp_coupling_system import AgentMCPCoupler

logger = logging.getLogger(__name__)


class NodeType(Enum):
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
    SECURITY = "security"
    CODE = "code"


class PipelineNode:
    def __init__(self, node_id: str, node_type: NodeType, config: Dict[str, Any]):
        self.id = node_id
        self.type = node_type
        self.config = config
        self.position = config.get("position", {"x": 0, "y": 0})
        self.label = config.get("label", node_type.value)
        self.inputs = []
        self.outputs = []
        self.result = None
        
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """Execute this node with given input"""
        logger.info(f"Executing node {self.id} ({self.type.value})")
        
        if self.type == NodeType.INPUT:
            return input_data
            
        elif self.type == NodeType.AGENT:
            # Execute agent with input
            agent_id = self.config.get("agent_id")
            if not agent_id:
                raise ValueError(f"Node {self.id} missing agent_id")
                
            agent_manager = context.get("agent_manager")
            if not agent_manager:
                agent_manager = IntegratedAgentManager()
                
            # Create session and send message
            session_id = f"pipeline_{uuid.uuid4()}"
            response = await agent_manager.send_message(
                agent_id=agent_id,
                message=str(input_data),
                session_id=session_id
            )
            return response
            
        elif self.type == NodeType.MCP_SERVER:
            # Connect to MCP server and execute tool
            server_name = self.config.get("server_name")
            tool_name = self.config.get("tool_name")
            
            if not server_name or not tool_name:
                raise ValueError(f"Node {self.id} missing server_name or tool_name")
                
            # TODO: Execute MCP tool
            return f"MCP Result from {server_name}.{tool_name}: {input_data}"
            
        elif self.type == NodeType.TEXT_PROCESSOR:
            # Process text
            operation = self.config.get("operation", "uppercase")
            text = str(input_data)
            
            if operation == "uppercase":
                return text.upper()
            elif operation == "lowercase":
                return text.lower()
            elif operation == "reverse":
                return text[::-1]
            elif operation == "word_count":
                return len(text.split())
            else:
                return text
                
        elif self.type == NodeType.DATABASE:
            # Simulate database query
            query = self.config.get("query", "SELECT * FROM data")
            return f"DB Result for '{query}': {input_data}"
            
        elif self.type == NodeType.API:
            # Simulate API call
            endpoint = self.config.get("endpoint", "/api/data")
            method = self.config.get("method", "GET")
            return f"API {method} {endpoint}: {input_data}"
            
        elif self.type == NodeType.CODE:
            # Execute Python code (sandboxed in real implementation)
            code = self.config.get("code", "return input_data")
            # WARNING: This is unsafe, use proper sandboxing in production
            local_vars = {"input_data": input_data}
            exec(f"result = {code}", {}, local_vars)
            return local_vars.get("result", input_data)
            
        elif self.type == NodeType.OUTPUT:
            return input_data
            
        else:
            # Default passthrough
            return input_data


class Pipeline:
    def __init__(self, pipeline_id: str, name: str, description: str = ""):
        self.id = pipeline_id
        self.name = name
        self.description = description
        self.nodes: Dict[str, PipelineNode] = {}
        self.connections: List[Dict[str, str]] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def add_node(self, node: PipelineNode):
        """Add a node to the pipeline"""
        self.nodes[node.id] = node
        
    def add_connection(self, from_id: str, to_id: str):
        """Add a connection between nodes"""
        if from_id not in self.nodes or to_id not in self.nodes:
            raise ValueError("Invalid node IDs for connection")
            
        self.connections.append({"from": from_id, "to": to_id})
        self.nodes[from_id].outputs.append(to_id)
        self.nodes[to_id].inputs.append(from_id)
        
    def get_execution_order(self) -> List[str]:
        """Get nodes in topological order for execution"""
        visited = set()
        order = []
        
        def visit(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            node = self.nodes[node_id]
            for input_id in node.inputs:
                visit(input_id)
            order.append(node_id)
            
        # Start with output nodes
        for node_id, node in self.nodes.items():
            if node.type == NodeType.OUTPUT:
                visit(node_id)
                
        return order
        
    async def execute(self, input_data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute the pipeline with given input"""
        if context is None:
            context = {}
            
        execution_order = self.get_execution_order()
        results = {}
        
        logger.info(f"Executing pipeline {self.name} with {len(execution_order)} nodes")
        
        for node_id in execution_order:
            node = self.nodes[node_id]
            
            # Get input for this node
            if node.type == NodeType.INPUT:
                node_input = input_data
            elif len(node.inputs) == 0:
                node_input = None
            elif len(node.inputs) == 1:
                node_input = results.get(node.inputs[0])
            else:
                # Multiple inputs - combine them
                node_input = [results.get(input_id) for input_id in node.inputs]
                
            # Execute node
            try:
                result = await node.execute(node_input, context)
                results[node_id] = result
                node.result = result
                logger.info(f"Node {node_id} completed successfully")
            except Exception as e:
                logger.error(f"Node {node_id} failed: {e}")
                raise
                
        # Return output from output nodes
        output_nodes = [n for n in self.nodes.values() if n.type == NodeType.OUTPUT]
        if output_nodes:
            return results.get(output_nodes[0].id)
        return results
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type.value,
                    "label": node.label,
                    "position": node.position,
                    "config": node.config
                }
                for node in self.nodes.values()
            ],
            "connections": self.connections,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pipeline":
        """Create pipeline from dictionary"""
        pipeline = cls(
            pipeline_id=data["id"],
            name=data["name"],
            description=data.get("description", "")
        )
        
        # Add nodes
        for node_data in data["nodes"]:
            node = PipelineNode(
                node_id=node_data["id"],
                node_type=NodeType(node_data["type"]),
                config=node_data.get("config", {})
            )
            node.position = node_data.get("position", {"x": 0, "y": 0})
            node.label = node_data.get("label", node.type.value)
            pipeline.add_node(node)
            
        # Add connections
        for conn in data["connections"]:
            pipeline.add_connection(conn["from"], conn["to"])
            
        return pipeline


class PipelineEngine:
    def __init__(self):
        self.pipelines: Dict[str, Pipeline] = {}
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.agent_manager = IntegratedAgentManager()
        self.coupler = AgentMCPCoupler()
        
    def create_pipeline(self, name: str, description: str = "") -> Pipeline:
        """Create a new pipeline"""
        pipeline_id = str(uuid.uuid4())
        pipeline = Pipeline(pipeline_id, name, description)
        self.pipelines[pipeline_id] = pipeline
        return pipeline
        
    def get_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Get pipeline by ID"""
        return self.pipelines.get(pipeline_id)
        
    def save_pipeline(self, pipeline: Pipeline) -> str:
        """Save pipeline to storage"""
        self.pipelines[pipeline.id] = pipeline
        pipeline.updated_at = datetime.utcnow()
        
        # Save to file (in production, use database)
        with open(f"pipelines/{pipeline.id}.json", "w") as f:
            json.dump(pipeline.to_dict(), f, indent=2)
            
        return pipeline.id
        
    def load_pipeline(self, pipeline_id: str) -> Optional[Pipeline]:
        """Load pipeline from storage"""
        try:
            with open(f"pipelines/{pipeline_id}.json", "r") as f:
                data = json.load(f)
                pipeline = Pipeline.from_dict(data)
                self.pipelines[pipeline_id] = pipeline
                return pipeline
        except FileNotFoundError:
            return None
            
    async def execute_pipeline(self, pipeline_id: str, input_data: Any) -> Dict[str, Any]:
        """Execute a pipeline and track the execution"""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")
            
        execution_id = str(uuid.uuid4())
        execution = {
            "id": execution_id,
            "pipeline_id": pipeline_id,
            "status": "running",
            "started_at": datetime.utcnow(),
            "input": input_data,
            "output": None,
            "error": None,
            "node_results": {}
        }
        
        self.executions[execution_id] = execution
        
        try:
            # Create context with our services
            context = {
                "agent_manager": self.agent_manager,
                "coupler": self.coupler,
                "execution_id": execution_id
            }
            
            # Execute pipeline
            result = await pipeline.execute(input_data, context)
            
            execution["output"] = result
            execution["status"] = "completed"
            execution["completed_at"] = datetime.utcnow()
            
            # Collect node results
            for node_id, node in pipeline.nodes.items():
                execution["node_results"][node_id] = {
                    "type": node.type.value,
                    "label": node.label,
                    "result": node.result
                }
                
        except Exception as e:
            execution["status"] = "failed"
            execution["error"] = str(e)
            execution["completed_at"] = datetime.utcnow()
            logger.error(f"Pipeline execution failed: {e}")
            raise
            
        return execution
        
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution details"""
        return self.executions.get(execution_id)
        
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all pipelines"""
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "node_count": len(p.nodes),
                "created_at": p.created_at.isoformat(),
                "updated_at": p.updated_at.isoformat()
            }
            for p in self.pipelines.values()
        ]


# Example usage
async def example_pipeline():
    engine = PipelineEngine()
    
    # Create a pipeline
    pipeline = engine.create_pipeline(
        name="Customer Support Pipeline",
        description="Process customer inquiries through AI agent"
    )
    
    # Add nodes
    input_node = PipelineNode("1", NodeType.INPUT, {})
    agent_node = PipelineNode("2", NodeType.AGENT, {
        "agent_id": "sre_servicenow_001",
        "model": "gpt-4"
    })
    output_node = PipelineNode("3", NodeType.OUTPUT, {})
    
    pipeline.add_node(input_node)
    pipeline.add_node(agent_node)
    pipeline.add_node(output_node)
    
    # Connect nodes
    pipeline.add_connection("1", "2")
    pipeline.add_connection("2", "3")
    
    # Save pipeline
    engine.save_pipeline(pipeline)
    
    # Execute pipeline
    result = await engine.execute_pipeline(
        pipeline.id,
        "Help! My database is down!"
    )
    
    print(f"Pipeline result: {result}")


if __name__ == "__main__":
    asyncio.run(example_pipeline())
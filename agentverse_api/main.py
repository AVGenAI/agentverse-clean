"""
AgentVerse API - FastAPI Backend
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio
from datetime import datetime
import uuid
from agentverse_api.agent_manager import agent_manager

# Import routers
from agentverse_api.routers import mcp_router, pipeline_router

app = FastAPI(
    title="AgentVerse API",
    description="Backend API for AgentVerse - Where 1000 AI Agents Collaborate",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load agents data
AGENTS_DATA = []
try:
    import os
    # Try different paths to find the config file
    config_paths = [
        "../src/config/agentverse_agents_1000.json",
        "src/config/agentverse_agents_1000.json",
        "/Users/vallu/z_AV_Labs_Gemini_June2025/aiagents/src/config/agentverse_agents_1000.json"
    ]
    
    for path in config_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                AGENTS_DATA = json.load(f)
                print(f"✅ Loaded {len(AGENTS_DATA)} agents from: {path}")
                break
    else:
        print(f"Warning: Could not find agents data in any of the paths: {config_paths}")
except Exception as e:
    print(f"Warning: Could not load agents data: {e}")

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Active chat sessions
chat_sessions: Dict[str, Dict] = {}


# Pydantic models
class AgentQuery(BaseModel):
    domain: Optional[str] = None
    skill: Optional[str] = None
    limit: int = 20
    offset: int = 0


class ChatMessage(BaseModel):
    agent_id: str
    message: str
    session_id: Optional[str] = None


class TeamRequest(BaseModel):
    project_type: str
    requirements: List[str]
    team_size: int = 5


class AgentCreateRequest(BaseModel):
    name: str
    instructions: str
    domain: str
    subdomain: str
    skills: List[str]
    tools: List[str] = []


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to AgentVerse API",
        "version": "1.0.0",
        "total_agents": len(AGENTS_DATA),
        "endpoints": {
            "agents": "/agents",
            "domains": "/domains",
            "search": "/search",
            "team": "/team/assemble",
            "chat": "/chat",
            "ws": "/ws/{client_id}",
            "mcp": {
                "servers": "/api/mcp/servers",
                "tools": "/api/mcp/servers/{server_id}/tools",
                "execute": "/api/mcp/execute"
            },
            "pipeline": {
                "list": "/api/pipeline/pipelines",
                "create": "/api/pipeline/pipelines",
                "get": "/api/pipeline/pipelines/{pipeline_id}",
                "update": "/api/pipeline/pipelines/{pipeline_id}",
                "delete": "/api/pipeline/pipelines/{pipeline_id}",
                "execute": "/api/pipeline/pipelines/{pipeline_id}/execute",
                "validate": "/api/pipeline/pipelines/{pipeline_id}/validate",
                "node_types": "/api/pipeline/node-types",
                "executions": "/api/pipeline/executions/{execution_id}"
            }
        }
    }


# Get all domains
@app.get("/domains")
async def get_domains():
    domains = {}
    
    for agent in AGENTS_DATA:
        canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "")
        if "." in canonical:
            parts = canonical.split(".")
            domain = parts[1]
            subdomain = parts[2] if len(parts) > 2 else "general"
            
            if domain not in domains:
                domains[domain] = {
                    "name": domain,
                    "agent_count": 0,
                    "subdomains": {}
                }
            
            domains[domain]["agent_count"] += 1
            
            if subdomain not in domains[domain]["subdomains"]:
                domains[domain]["subdomains"][subdomain] = 0
            domains[domain]["subdomains"][subdomain] += 1
    
    return {"domains": domains, "total_domains": len(domains)}


# Get agents with filtering
@app.post("/agents")
async def get_agents(query: AgentQuery):
    filtered_agents = AGENTS_DATA
    
    # Filter by domain
    if query.domain:
        filtered_agents = [
            a for a in filtered_agents 
            if query.domain.lower() in a.get("enhanced_metadata", {}).get("canonical_name", "").lower()
        ]
    
    # Filter by skill
    if query.skill:
        filtered_agents = [
            a for a in filtered_agents
            if any(query.skill.lower() in skill.lower() 
                   for skill in a.get("enhanced_metadata", {}).get("capabilities", {}).get("primary_expertise", []))
        ]
    
    # Pagination
    total = len(filtered_agents)
    start = query.offset
    end = query.offset + query.limit
    paginated = filtered_agents[start:end]
    
    # Format response
    agents = []
    for agent in paginated:
        metadata = agent.get("enhanced_metadata", {})
        
        # Extract domain and type from canonical name
        canonical_parts = metadata.get("canonical_name", "").split(".")
        domain = canonical_parts[1] if len(canonical_parts) > 1 else "general"
        agent_type = canonical_parts[2] if len(canonical_parts) > 2 else "specialist"
        
        agents.append({
            "id": metadata.get("agent_uuid"),
            "canonical_name": metadata.get("canonical_name"),
            "display_name": metadata.get("display_name"),
            "name": metadata.get("display_name"),  # For backward compatibility
            "avatar": metadata.get("avatar_emoji"),
            "skills": metadata.get("capabilities", {}).get("primary_expertise", []),
            "tools": list(metadata.get("capabilities", {}).get("tools_mastery", {}).keys()),
            "collaboration_style": metadata.get("collaboration", {}).get("style", []),
            "trust_score": metadata.get("quality", {}).get("trust_score", 0.95),
            # Enhanced fields for EnhancedAgentCard
            "enhanced_metadata": metadata,
            "domain": domain,
            "type": agent_type,
            "capabilities": metadata.get("capabilities", {}),
            "instructions": agent.get("instructions", ""),
            "version": metadata.get("version", "1.0.0"),
            "model_preferences": metadata.get("model_preferences", {"primary": "gpt-4o-mini"}),
            "mcp_server": metadata.get("mcp_coupling", {}).get("server_name"),
            "status": "active"  # Default status - in production this would be dynamic
        })
    
    return {
        "agents": agents,
        "total": total,
        "offset": query.offset,
        "limit": query.limit
    }


# Search agents
@app.get("/search")
async def search_agents(q: str, limit: int = 10):
    if not q:
        raise HTTPException(status_code=400, detail="Search query required")
    
    results = []
    query_lower = q.lower()
    
    for agent in AGENTS_DATA:
        metadata = agent.get("enhanced_metadata", {})
        
        # Search in various fields
        searchable = [
            metadata.get("display_name", ""),
            metadata.get("canonical_name", ""),
            " ".join(metadata.get("capabilities", {}).get("primary_expertise", [])),
            " ".join(metadata.get("discovery", {}).get("keywords", [])),
            " ".join(metadata.get("discovery", {}).get("problem_domains", []))
        ]
        
        if any(query_lower in field.lower() for field in searchable):
            results.append({
                "id": metadata.get("agent_uuid"),
                "canonical_name": metadata.get("canonical_name"),
                "display_name": metadata.get("display_name"),
                "avatar": metadata.get("avatar_emoji"),
                "skills": metadata.get("capabilities", {}).get("primary_expertise", []),
                "relevance_score": sum(1 for field in searchable if query_lower in field.lower())
            })
    
    # Sort by relevance
    results.sort(key=lambda x: x["relevance_score"], reverse=True)
    
    return {
        "query": q,
        "results": results[:limit],
        "total_found": len(results)
    }


# Get specific agent
@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    for agent in AGENTS_DATA:
        metadata = agent.get("enhanced_metadata", {})
        if metadata.get("agent_uuid") == agent_id or metadata.get("canonical_name") == agent_id:
            # Extract domain and subdomain from canonical name
            canonical_parts = metadata.get("canonical_name", "").split(".")
            domain = canonical_parts[1] if len(canonical_parts) > 1 else "unknown"
            subdomain = canonical_parts[2] if len(canonical_parts) > 2 else "general"
            
            return {
                "agent": {
                    "id": metadata.get("agent_uuid"),
                    "canonical_name": metadata.get("canonical_name"),
                    "display_name": metadata.get("display_name"),
                    "avatar": metadata.get("avatar_emoji"),
                    "instructions": agent.get("instructions", ""),
                    "domain": domain,
                    "subdomain": subdomain,
                    "capabilities": metadata.get("capabilities", {}),
                    "collaboration": metadata.get("collaboration", {}),
                    "collaboration_style": metadata.get("collaboration", {}).get("style", []),
                    "performance_metrics": {
                        "success_rate": metadata.get("performance", {}).get("success_rate", 95),
                        "reliability": metadata.get("quality", {}).get("reliability_score", 0.98) * 100,
                        "avg_response_time": metadata.get("performance", {}).get("avg_response_time", "1.2s"),
                        "tasks_completed": f"{metadata.get('performance', {}).get('completed_tasks', 2847):,}"
                    },
                    "network": metadata.get("network", {}),
                    "quality": metadata.get("quality", {}),
                    "trust_score": metadata.get("quality", {}).get("trust_score", 0.95),
                    "version": metadata.get("version", "1.0.0"),
                    "created_at": metadata.get("created_at", "June 2025"),
                    "skills": metadata.get("capabilities", {}).get("primary_expertise", [])
                }
            }
    
    raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")


# Find collaborators for an agent
@app.get("/agents/{agent_id}/collaborators")
async def get_collaborators(agent_id: str):
    # Find the agent
    target_agent = None
    for agent in AGENTS_DATA:
        metadata = agent.get("enhanced_metadata", {})
        if metadata.get("agent_uuid") == agent_id:
            target_agent = agent
            break
    
    if not target_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Find collaborators
    collaborators = []
    target_metadata = target_agent.get("enhanced_metadata", {})
    
    for pattern in target_metadata.get("network", {}).get("upstream", []):
        if "." in pattern:
            domain = pattern.split(".")[1]
            
            # Find agents matching the pattern
            for agent in AGENTS_DATA[:20]:  # Limit for demo
                agent_canonical = agent.get("enhanced_metadata", {}).get("canonical_name", "")
                if domain in agent_canonical and agent != target_agent:
                    metadata = agent.get("enhanced_metadata", {})
                    collaborators.append({
                        "id": metadata.get("agent_uuid"),
                        "canonical_name": metadata.get("canonical_name"),
                        "display_name": metadata.get("display_name"),
                        "avatar": metadata.get("avatar_emoji"),
                        "skills": metadata.get("capabilities", {}).get("primary_expertise", []),
                        "reason": f"{domain} specialist"
                    })
    
    return {
        "agent_id": agent_id,
        "collaborators": collaborators[:10],  # Limit to 10
        "total": len(collaborators)
    }


# Assemble a team
@app.post("/team/assemble")
async def assemble_team(request: TeamRequest):
    team = []
    
    # Define role mappings based on project type
    role_mappings = {
        "ecommerce": {
            "Frontend Developer": ["React", "UI/UX", "E-commerce"],
            "Backend Developer": ["Python", "API Design", "Database"],
            "Payment Specialist": ["Payment", "Security", "Integration"],
            "DevOps Engineer": ["Docker", "Kubernetes", "CI/CD"]
        },
        "mobile": {
            "Mobile Developer": ["React Native", "iOS", "Android"],
            "Backend Developer": ["API Design", "Security", "Scalability"],
            "UI/UX Designer": ["Mobile", "Design", "User Experience"],
            "QA Engineer": ["Testing", "Mobile", "Automation"]
        },
        "data": {
            "Data Engineer": ["ETL", "Data Pipeline", "Big Data"],
            "Data Scientist": ["Machine Learning", "Analytics", "Python"],
            "Backend Developer": ["API Design", "Python", "Database"],
            "DevOps Engineer": ["Cloud", "Infrastructure", "Monitoring"]
        }
    }
    
    # Get roles for project type
    roles = role_mappings.get(request.project_type.lower(), role_mappings["ecommerce"])
    
    # Add custom requirements
    if request.requirements:
        roles["Specialist"] = request.requirements
    
    # Find best agents for each role
    for role, keywords in list(roles.items())[:request.team_size]:
        best_agent = None
        best_score = 0
        
        for agent in AGENTS_DATA:
            metadata = agent.get("enhanced_metadata", {})
            skills = " ".join(metadata.get("capabilities", {}).get("primary_expertise", [])).lower()
            
            score = sum(2 if keyword.lower() in skills else 0 for keyword in keywords)
            
            if score > best_score:
                best_score = score
                best_agent = agent
        
        if best_agent:
            metadata = best_agent.get("enhanced_metadata", {})
            team.append({
                "role": role,
                "agent": {
                    "id": metadata.get("agent_uuid"),
                    "canonical_name": metadata.get("canonical_name"),
                    "display_name": metadata.get("display_name"),
                    "avatar": metadata.get("avatar_emoji"),
                    "skills": metadata.get("capabilities", {}).get("primary_expertise", []),
                    "match_score": best_score
                }
            })
    
    return {
        "project_type": request.project_type,
        "team": team,
        "team_size": len(team)
    }


# Create a chat session
@app.post("/chat/session")
async def create_chat_session(agent_id: str):
    session_id = str(uuid.uuid4())
    
    # Find agent
    agent = None
    for a in AGENTS_DATA:
        if a.get("enhanced_metadata", {}).get("agent_uuid") == agent_id:
            agent = a
            break
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create session
    chat_sessions[session_id] = {
        "id": session_id,
        "agent_id": agent_id,
        "agent": agent,
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "session_id": session_id,
        "agent_id": agent_id,
        "status": "created"
    }


# Send chat message (with OpenAI integration)
@app.post("/chat/message")
async def send_message(message: ChatMessage):
    if message.session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chat_sessions[message.session_id]
    
    # Add user message
    session["messages"].append({
        "role": "user",
        "content": message.message,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get response from real agent via agent_manager
    agent_id = session["agent_id"]
    
    try:
        # Use the agent manager to get a real response
        response = await agent_manager.chat_with_agent(agent_id, message.message)
    except Exception as e:
        print(f"Error getting agent response: {e}")
        # Fallback response
        agent_metadata = session["agent"].get("enhanced_metadata", {})
        agent_name = agent_metadata.get("display_name", "Agent")
        response = f"I'm {agent_name}. I encountered an error processing your request. Please make sure the OPENAI_API_KEY is set correctly."
    
    # Add agent response
    session["messages"].append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().isoformat()
    })
    
    return {
        "response": response,
        "session_id": message.session_id
    }


# WebSocket for real-time chat
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    active_connections[client_id] = websocket
    
    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to AgentVerse WebSocket",
            "client_id": client_id
        })
        
        while True:
            data = await websocket.receive_json()
            
            # Handle different message types
            if data.get("type") == "chat":
                # Process chat message
                response = {
                    "type": "chat_response",
                    "message": f"Received: {data.get('message')}",
                    "timestamp": datetime.now().isoformat()
                }
                await websocket.send_json(response)
            
            elif data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        del active_connections[client_id]
    except Exception as e:
        print(f"WebSocket error: {e}")
        if client_id in active_connections:
            del active_connections[client_id]


# Include routers
app.include_router(mcp_router.router)
app.include_router(pipeline_router.router)

# Health check
@app.get("/health")
async def health_check():
    # Check Ollama status
    await agent_manager._check_ollama_status()
    
    return {
        "status": "healthy",
        "agents_loaded": len(AGENTS_DATA),
        "active_connections": len(active_connections),
        "active_sessions": len(chat_sessions),
        "llm_providers": {
            "ollama": {
                "available": agent_manager.ollama_available,
                "enabled": agent_manager.use_ollama,
                "model": agent_manager.ollama_model
            },
            "openai": {
                "available": bool(agent_manager.api_key),
                "model": "gpt-4o-mini"
            }
        },
        "active_agents": len(agent_manager.agents)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
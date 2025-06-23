-- AgentVerse PostgreSQL Schema
-- Scalable database design for 1 million+ agents

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Main agents table
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    subdomain VARCHAR(100),
    version VARCHAR(20) DEFAULT '1.0.0',
    status VARCHAR(50) DEFAULT 'active',
    instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes separately
CREATE INDEX idx_agents_domain ON agents (domain);
CREATE INDEX idx_agents_subdomain ON agents (subdomain);
CREATE INDEX idx_agents_status ON agents (status);
CREATE INDEX idx_agents_type ON agents (type);

-- Agent metadata table (for enhanced metadata)
CREATE TABLE agent_metadata (
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    canonical_name VARCHAR(500) UNIQUE NOT NULL,
    display_name VARCHAR(255) NOT NULL,
    avatar VARCHAR(10),
    trust_score DECIMAL(3,2) DEFAULT 0.80,
    reliability_rating DECIMAL(3,2) DEFAULT 0.80,
    response_time_avg DECIMAL(5,2) DEFAULT 2.0,
    collaboration_style VARCHAR(50),
    
    PRIMARY KEY (agent_id)
);

CREATE INDEX idx_metadata_trust ON agent_metadata (trust_score);
CREATE INDEX idx_metadata_canonical ON agent_metadata (canonical_name);

-- Agent capabilities table
CREATE TABLE agent_capabilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    capability_type VARCHAR(50) NOT NULL, -- 'expertise', 'tool', 'integration'
    capability_name VARCHAR(255) NOT NULL,
    capability_level VARCHAR(50), -- 'expert', 'advanced', 'intermediate', 'basic'
    
    UNIQUE (agent_id, capability_type, capability_name)
);

-- Create indexes for agent_capabilities
CREATE INDEX idx_capabilities_agent ON agent_capabilities (agent_id);
CREATE INDEX idx_capabilities_type ON agent_capabilities (capability_type);

-- Agent tools table
CREATE TABLE agent_tools (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    tool_description TEXT,
    tool_config JSONB, -- Store tool-specific configuration
    is_active BOOLEAN DEFAULT true,
    
    UNIQUE (agent_id, tool_name)
);

-- Create indexes for agent_tools
CREATE INDEX idx_tools_agent ON agent_tools (agent_id);
CREATE INDEX idx_tools_name ON agent_tools (tool_name);

-- Agent model preferences
CREATE TABLE agent_model_preferences (
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    llm_provider VARCHAR(50) DEFAULT 'openai',
    primary_model VARCHAR(100) DEFAULT 'gpt-4o-mini',
    fallback_model VARCHAR(100) DEFAULT 'gpt-3.5-turbo',
    reasoning_model VARCHAR(100),
    max_tokens INTEGER DEFAULT 2000,
    temperature DECIMAL(2,1) DEFAULT 0.7,
    
    PRIMARY KEY (agent_id)
);

-- Agent performance metrics
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    metric_date DATE DEFAULT CURRENT_DATE,
    interactions_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    avg_response_time DECIMAL(10,2),
    tokens_used INTEGER DEFAULT 0,
    
    UNIQUE (agent_id, metric_date)
);

-- Create indexes for agent_metrics
CREATE INDEX idx_metrics_agent_date ON agent_metrics (agent_id, metric_date);

-- Agent teams/collaborations
CREATE TABLE agent_teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    team_name VARCHAR(255) NOT NULL,
    team_purpose TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agent_team_members (
    team_id UUID REFERENCES agent_teams(id) ON DELETE CASCADE,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    role VARCHAR(100),
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (team_id, agent_id)
);

-- Search optimization with full text search
ALTER TABLE agents ADD COLUMN search_vector tsvector;

CREATE OR REPLACE FUNCTION update_agent_search() RETURNS trigger AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.domain, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.subdomain, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.instructions, '')), 'C');
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_agent_search_trigger 
    BEFORE INSERT OR UPDATE ON agents
    FOR EACH ROW EXECUTE FUNCTION update_agent_search();

CREATE INDEX idx_agents_search ON agents USING gin(search_vector);

-- Chat sessions table
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    user_id VARCHAR(255),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    session_metadata JSONB
);

-- Create indexes for chat_sessions
CREATE INDEX idx_sessions_agent ON chat_sessions (agent_id);
CREATE INDEX idx_sessions_user ON chat_sessions (user_id);
CREATE INDEX idx_sessions_started ON chat_sessions (started_at);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL, -- 'user', 'agent', 'system'
    content TEXT NOT NULL,
    metadata JSONB, -- Store tool calls, responses, etc.
    tokens_used INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for chat_messages
CREATE INDEX idx_messages_session ON chat_messages (session_id);
CREATE INDEX idx_messages_created ON chat_messages (created_at);

-- Chat tools usage table
CREATE TABLE chat_tool_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id UUID REFERENCES chat_messages(id) ON DELETE CASCADE,
    tool_name VARCHAR(255) NOT NULL,
    tool_input JSONB,
    tool_output JSONB,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT true,
    error_message TEXT
);

-- Create indexes for chat_tool_usage
CREATE INDEX idx_tool_usage_message ON chat_tool_usage (message_id);
CREATE INDEX idx_tool_usage_tool ON chat_tool_usage (tool_name);

-- MCP coupling history
CREATE TABLE mcp_coupling_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    mcp_server VARCHAR(255) NOT NULL,
    coupling_id VARCHAR(500) NOT NULL,
    compatibility_level VARCHAR(50),
    activated_at TIMESTAMP,
    deactivated_at TIMESTAMP,
    test_results JSONB
);

-- Create indexes for mcp_coupling_history
CREATE INDEX idx_coupling_agent ON mcp_coupling_history (agent_id);
CREATE INDEX idx_coupling_server ON mcp_coupling_history (mcp_server);

-- Agent search history (for analytics)
CREATE TABLE agent_search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_query TEXT NOT NULL,
    search_filters JSONB,
    results_count INTEGER,
    selected_agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
    searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for agent_search_history
CREATE INDEX idx_search_time ON agent_search_history (searched_at);

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_agents_updated_at BEFORE UPDATE
    ON agents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
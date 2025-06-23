import React from 'react'
import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  ArrowLeft, 
  MessageSquare, 
  Users, 
  Star, 
  Shield, 
  Zap,
  Network,
  Trophy,
  Target,
  Clock,
  Code,
  Database,
  Globe,
  Hash,
  GitBranch,
  Award,
  Layers,
  CheckCircle,
  XCircle
} from 'lucide-react'
import axios from 'axios'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

export default function AgentDetails() {
  const { agentId } = useParams()

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/agents/${agentId}`)
      return response.data.agent
    }
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="liquid-loader"></div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="glass-card text-center p-8">
          <h2 className="text-2xl font-bold gradient-text">Agent not found</h2>
          <Link to="/agents" className="mt-4 inline-block liquid-button">
            Back to agents
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Back Button */}
      <Link 
        to="/agents" 
        className="inline-flex items-center gap-2 glass-card p-3 hover:scale-105 transition-transform mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Agents
      </Link>

      {/* Agent Header */}
      <div className="glass-card p-8 mb-6">
        <div className="flex items-start gap-6">
          <div className="text-6xl">{agent.avatar || '🤖'}</div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold gradient-text mb-2">
              {agent.display_name}
            </h1>
            <p className="text-lg text-secondary mb-4">
              {agent.canonical_name}
            </p>
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4" style={{ color: 'var(--accent-gradient-start)' }} />
                <span className="text-secondary">Trust Score: {(agent.trust_score * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4" style={{ color: 'var(--accent-gradient-end)' }} />
                <span className="text-secondary">Performance: {agent.performance_metrics?.success_rate || 95}%</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4" style={{ color: 'var(--primary-gradient-start)' }} />
                <span className="text-secondary">Response Time: {agent.performance_metrics?.avg_response_time || '1.2s'}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            <Link
              to={`/chat/${agent.id}`}
              className="liquid-button inline-flex items-center gap-2"
            >
              <MessageSquare className="h-5 w-5" />
              Start Chat
            </Link>
            <button className="glass-button inline-flex items-center gap-2">
              <Users className="h-5 w-5" />
              Add to Team
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Capabilities */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Capabilities
            </h2>
            
            {/* Primary Expertise */}
            <div className="mb-6">
              <h3 className="font-medium text-secondary mb-3">Primary Expertise</h3>
              <div className="flex flex-wrap gap-2">
                {agent.capabilities?.primary_expertise?.map((skill, idx) => (
                  <span
                    key={idx}
                    className="glass-badge"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Secondary Skills */}
            {agent.capabilities?.secondary_skills && (
              <div className="mb-6">
                <h3 className="font-medium text-secondary mb-3">Secondary Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.secondary_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="glass-badge"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Tools */}
            {agent.capabilities?.tools && (
              <div>
                <h3 className="font-medium text-secondary mb-3">Tools & Technologies</h3>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.tools.map((tool, idx) => (
                    <span
                      key={idx}
                      className="glass-badge"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Instructions & Behavior */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Shield className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Instructions & Behavior
            </h2>
            
            {agent.instructions ? (
              <div className="space-y-4">
                <div className="p-4 glass-card rounded-lg">
                  <p className="text-sm text-secondary whitespace-pre-wrap">
                    {agent.instructions}
                  </p>
                </div>
                
                {/* Behavior Traits */}
                {agent.enhanced_metadata?.behavior && (
                  <div>
                    <h3 className="font-medium text-secondary mb-2">Behavior Traits</h3>
                    <div className="flex flex-wrap gap-2">
                      {Object.entries(agent.enhanced_metadata.behavior).map(([key, value], idx) => (
                        <span key={idx} className="glass-badge text-xs">
                          {key.replace(/_/g, ' ')}: {value}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted">No specific instructions configured</p>
            )}
          </div>

          {/* Collaboration Network */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Network className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Collaboration Network
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Upstream Dependencies */}
              <div>
                <h3 className="font-medium text-secondary mb-3">Works Well With</h3>
                {agent.collaboration?.upstream_dependencies?.map((dep, idx) => (
                  <div key={idx} className="mb-2 p-3 glass-card rounded-lg">
                    <span className="font-medium text-primary">{dep}</span>
                  </div>
                ))}
              </div>

              {/* Downstream Dependents */}
              <div>
                <h3 className="font-medium text-secondary mb-3">Supports These Agents</h3>
                {agent.collaboration?.downstream_dependents?.map((dep, idx) => (
                  <div key={idx} className="mb-2 p-3 glass-card rounded-lg">
                    <span className="font-medium text-primary">{dep}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Collaboration Style */}
            <div className="mt-6 p-4 glass-card rounded-lg">
              <h3 className="font-medium text-secondary mb-2">Collaboration Style</h3>
              <p className="text-sm text-secondary">
                {agent.collaboration_style?.join(', ')}
              </p>
            </div>
          </div>
        </div>

        {/* Right Column - Stats & Meta */}
        <div className="space-y-6">
          {/* Performance Metrics */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Trophy className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Performance
            </h2>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-secondary">Success Rate</span>
                  <span className="font-medium text-primary">{agent.performance_metrics?.success_rate || 95}%</span>
                </div>
                <div className="w-full glass-card rounded-full h-2">
                  <div 
                    className="h-2 rounded-full"
                    style={{ 
                      width: `${agent.performance_metrics?.success_rate || 95}%`,
                      background: 'linear-gradient(90deg, var(--accent-gradient-start), var(--accent-gradient-end))'
                    }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-secondary">Reliability</span>
                  <span className="font-medium text-primary">{agent.performance_metrics?.reliability || 98}%</span>
                </div>
                <div className="w-full glass-card rounded-full h-2">
                  <div 
                    className="h-2 rounded-full"
                    style={{ 
                      width: `${agent.performance_metrics?.reliability || 98}%`,
                      background: 'linear-gradient(90deg, var(--primary-gradient-start), var(--primary-gradient-end))'
                    }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t" style={{ borderColor: 'var(--glass-border)' }}>
                <div className="flex justify-between text-sm">
                  <span className="text-secondary">Tasks Completed</span>
                  <span className="font-medium text-primary">{agent.performance_metrics?.tasks_completed || '2,847'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Target className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Agent Info
            </h2>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-muted">Agent ID</span>
                <span className="font-medium text-xs text-secondary">{agent.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Canonical Name</span>
                <span className="font-medium text-xs truncate ml-2 text-secondary">{agent.canonical_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Version</span>
                <span className="font-medium text-primary">{agent.version || '1.0.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Created</span>
                <span className="font-medium text-primary">{agent.created_at || 'June 2025'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Created By</span>
                <span className="font-medium text-primary">{agent.enhanced_metadata?.created_by || 'System'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Domain</span>
                <span className="font-medium capitalize text-primary">{agent.domain?.replace(/_/g, ' ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Subdomain</span>
                <span className="font-medium capitalize text-primary">{agent.subdomain?.replace(/_/g, ' ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Type</span>
                <span className="font-medium capitalize text-primary">{agent.enhanced_metadata?.taxonomy?.type || 'Specialist'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Model</span>
                <span className="font-medium text-primary">{agent.enhanced_metadata?.model_preferences?.primary || 'GPT-4'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Tools Available</span>
                <span className="font-medium text-primary">{agent.tools?.length || agent.enhanced_metadata?.tools?.length || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">MCP Server</span>
                <span className="font-medium" style={{ color: 'var(--accent-gradient-start)' }}>{agent.enhanced_metadata?.mcp_coupling?.server_name || 'None'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted">Language Support</span>
                <span className="font-medium text-primary">{agent.enhanced_metadata?.model_preferences?.languages?.join(', ') || 'English'}</span>
              </div>
            </div>
          </div>

          {/* Tools & Integrations */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Code className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Tools & Integrations
            </h2>
            
            <div className="space-y-4">
              {/* Tools List */}
              {agent.enhanced_metadata?.tools && agent.enhanced_metadata.tools.length > 0 ? (
                <div className="space-y-2">
                  {agent.enhanced_metadata.tools.map((tool, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 glass-card rounded">
                      <span className="text-sm font-medium text-primary">{tool.name || tool}</span>
                      <CheckCircle className="h-4 w-4" style={{ color: 'var(--accent-gradient-start)' }} />
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted">No specific tools configured</p>
              )}
              
              {/* MCP Status */}
              <div className="pt-4 border-t" style={{ borderColor: 'var(--glass-border)' }}>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted">MCP Connection</span>
                  {agent.enhanced_metadata?.mcp_coupling?.server_name ? (
                    <span className="flex items-center gap-2 text-sm" style={{ color: 'var(--accent-gradient-start)' }}>
                      <Database className="h-4 w-4" />
                      {agent.enhanced_metadata.mcp_coupling.server_name}
                    </span>
                  ) : (
                    <span className="flex items-center gap-2 text-sm text-muted">
                      <XCircle className="h-4 w-4" />
                      Not Connected
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Taxonomy & Classification */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Layers className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Taxonomy
            </h2>
            
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <span className="text-muted">Domain</span>
                  <p className="font-medium mt-1 text-primary">{agent.domain || 'general'}</p>
                </div>
                <div>
                  <span className="text-muted">Type</span>
                  <p className="font-medium mt-1 text-primary">{agent.enhanced_metadata?.taxonomy?.type || 'specialist'}</p>
                </div>
                <div>
                  <span className="text-muted">Specialization</span>
                  <p className="font-medium mt-1 text-primary">{agent.enhanced_metadata?.taxonomy?.specialization || agent.subdomain || 'general'}</p>
                </div>
                <div>
                  <span className="text-muted">Industry</span>
                  <p className="font-medium mt-1 text-primary">{agent.enhanced_metadata?.taxonomy?.industry || 'Technology'}</p>
                </div>
              </div>
              
              {/* Discovery Keywords */}
              {agent.enhanced_metadata?.discovery?.keywords && (
                <div className="pt-3 border-t" style={{ borderColor: 'var(--glass-border)' }}>
                  <p className="text-sm text-muted mb-2">Discovery Keywords</p>
                  <div className="flex flex-wrap gap-1">
                    {agent.enhanced_metadata.discovery.keywords.slice(0, 8).map((keyword, idx) => (
                      <span key={idx} className="glass-badge text-xs">
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quality Metrics */}
          <div className="glass-card p-6">
            <h2 className="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
              <Award className="h-5 w-5" style={{ color: 'var(--primary-gradient-start)' }} />
              Quality Metrics
            </h2>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Certification Level</span>
                <span className="text-sm font-medium text-primary">{agent.enhanced_metadata?.quality?.certification_level || 'Standard'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Testing Status</span>
                <span className="text-sm font-medium" style={{ color: 'var(--accent-gradient-start)' }}>{agent.enhanced_metadata?.quality?.testing_status || 'Passed'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Last Updated</span>
                <span className="text-sm font-medium text-primary">{agent.enhanced_metadata?.updated_at || agent.created_at || 'June 2025'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted">Maintenance</span>
                <span className="text-sm font-medium text-primary">{agent.enhanced_metadata?.lifecycle?.maintenance_schedule || 'Regular'}</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="glass-card p-6" style={{ background: 'linear-gradient(135deg, var(--primary-gradient-start), var(--primary-gradient-end))' }}>
            <h3 className="font-semibold mb-3 text-primary">Need help with this agent?</h3>
            <p className="text-sm text-secondary mb-4">
              Check out our documentation or join the community
            </p>
            <button className="w-full glass-button font-medium">
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
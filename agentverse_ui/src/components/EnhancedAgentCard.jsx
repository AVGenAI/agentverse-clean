import React from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, Cpu, MessageSquare, Shield, Activity, 
  Code, Database, Zap, Star, Clock, Users,
  GitBranch, Hash, Layers, Award
} from 'lucide-react';

const EnhancedAgentCard = ({ agent, viewMode = 'grid' }) => {
  const navigate = useNavigate();

  // Get status info
  const getAgentStatus = (agent) => {
    const statuses = {
      'active': { label: 'Active', color: 'bg-green-500', icon: Activity },
      'idle': { label: 'Idle', color: 'bg-yellow-500', icon: Clock },
      'busy': { label: 'Busy', color: 'bg-blue-500', icon: Zap },
      'error': { label: 'Error', color: 'bg-red-500', icon: Shield }
    };
    return statuses[agent.status] || statuses['idle'];
  };

  // Get avatar or fallback
  const getAvatar = () => {
    if (agent.avatar) return agent.avatar;
    if (agent.enhanced_metadata?.avatar_emoji) return agent.enhanced_metadata.avatar_emoji;
    
    const domainEmojis = {
      sre: '🚨', devops: '🔧', data: '📊', engineering: '💻',
      security: '🔒', healthcare: '🏥', finance: '💰', ml: '🤖'
    };
    return domainEmojis[agent.domain] || '🤖';
  };

  // Format agent ID for display
  const formatAgentId = (id) => {
    if (!id) return 'Unknown';
    const parts = id.split('_');
    return parts.slice(0, 3).join('-').toUpperCase();
  };

  // Get trust score color
  const getTrustScoreColor = (score) => {
    if (score >= 0.9) return 'text-green-400';
    if (score >= 0.7) return 'text-yellow-400';
    return 'text-orange-400';
  };

  const status = getAgentStatus(agent);
  const StatusIcon = status.icon;

  if (viewMode === 'list') {
    return (
      <div
        className="glass-card p-6 hover:scale-[1.01] transition-all cursor-pointer"
        onClick={() => navigate(`/agents/${agent.id}`)}
      >
        <div className="flex items-center justify-between">
          {/* Left section */}
          <div className="flex items-center space-x-4">
            {/* Avatar */}
            <div className="relative">
              <div className="text-5xl">{getAvatar()}</div>
              <div className={`absolute -bottom-1 -right-1 w-4 h-4 ${status.color} rounded-full border-2 border-gray-900`} />
            </div>

            {/* Main Info */}
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-1">
                <h3 className="text-xl font-semibold gradient-text">
                  {agent.name || agent.display_name}
                </h3>
                {agent.enhanced_metadata?.trust_score && (
                  <span className={`flex items-center gap-1 text-sm ${getTrustScoreColor(agent.enhanced_metadata.trust_score)}`}>
                    <Star className="w-4 h-4" />
                    {(agent.enhanced_metadata.trust_score * 100).toFixed(0)}%
                  </span>
                )}
              </div>
              
              {/* IDs and Taxonomy */}
              <div className="flex items-center gap-4 text-xs text-gray-400 mb-2">
                <span className="flex items-center gap-1">
                  <Hash className="w-3 h-3" />
                  {formatAgentId(agent.id)}
                </span>
                <span className="flex items-center gap-1">
                  <Layers className="w-3 h-3" />
                  {agent.domain}/{agent.type}
                </span>
                <span className="flex items-center gap-1">
                  <GitBranch className="w-3 h-3" />
                  v{agent.version || '1.0.0'}
                </span>
              </div>

              {/* Capabilities */}
              <div className="flex flex-wrap gap-2">
                {agent.capabilities?.primary_expertise?.slice(0, 4).map(skill => (
                  <span key={skill} className="glass-badge text-xs">
                    {skill}
                  </span>
                ))}
                {agent.tools?.length > 0 && (
                  <span className="glass-badge text-xs bg-purple-500/20">
                    <Code className="w-3 h-3 inline mr-1" />
                    {agent.tools.length} tools
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Right section */}
          <div className="flex items-center gap-6">
            {/* Model & MCP Info */}
            <div className="text-right">
              <div className="flex items-center gap-2 text-sm text-gray-300 mb-1">
                <Brain className="w-4 h-4" />
                {agent.model_preferences?.primary || 'GPT-4'}
              </div>
              {agent.mcp_server && (
                <div className="flex items-center gap-2 text-sm text-cyan-400">
                  <Database className="w-4 h-4" />
                  {agent.mcp_server}
                </div>
              )}
            </div>

            {/* Status */}
            <div className="text-center">
              <StatusIcon className={`w-6 h-6 ${status.color.replace('bg-', 'text-')} mb-1`} />
              <p className="text-xs text-gray-400">{status.label}</p>
            </div>

            {/* Action Button */}
            <button
              onClick={(e) => {
                e.stopPropagation();
                navigate(`/chat/${agent.id}`);
              }}
              className="liquid-button py-2 px-4 text-sm flex items-center"
            >
              <MessageSquare className="w-4 h-4 mr-1" />
              Chat
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Grid view
  return (
    <div
      className="glass-card p-6 hover:scale-[1.02] transition-all cursor-pointer group"
      onClick={() => navigate(`/agents/${agent.id}`)}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="relative">
          <div className="text-5xl">{getAvatar()}</div>
          <div className={`absolute -bottom-1 -right-1 w-4 h-4 ${status.color} rounded-full border-2 border-gray-900`} />
        </div>
        
        <div className="text-right">
          <StatusIcon className={`w-5 h-5 ${status.color.replace('bg-', 'text-')} mb-1`} />
          <p className="text-xs text-gray-400">{status.label}</p>
        </div>
      </div>

      {/* Name & Trust Score */}
      <div className="mb-3">
        <h3 className="text-xl font-semibold gradient-text mb-1">
          {agent.name || agent.display_name}
        </h3>
        {agent.enhanced_metadata?.trust_score && (
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1">
              {[...Array(5)].map((_, i) => (
                <Star 
                  key={i} 
                  className={`w-3 h-3 ${
                    i < Math.floor(agent.enhanced_metadata.trust_score * 5) 
                      ? 'text-yellow-400 fill-yellow-400' 
                      : 'text-gray-600'
                  }`} 
                />
              ))}
            </div>
            <span className={`text-sm ${getTrustScoreColor(agent.enhanced_metadata.trust_score)}`}>
              {(agent.enhanced_metadata.trust_score * 100).toFixed(0)}%
            </span>
          </div>
        )}
      </div>

      {/* Taxonomy Info */}
      <div className="glass-card bg-gray-800/30 p-3 mb-3 text-xs">
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center gap-1 text-gray-400">
            <Hash className="w-3 h-3" />
            <span className="truncate">{formatAgentId(agent.id)}</span>
          </div>
          <div className="flex items-center gap-1 text-gray-400">
            <Layers className="w-3 h-3" />
            <span>{agent.domain}/{agent.type}</span>
          </div>
          <div className="flex items-center gap-1 text-gray-400">
            <GitBranch className="w-3 h-3" />
            <span>v{agent.version || '1.0.0'}</span>
          </div>
          <div className="flex items-center gap-1 text-gray-400">
            <Users className="w-3 h-3" />
            <span>{agent.enhanced_metadata?.created_by || 'System'}</span>
          </div>
        </div>
      </div>

      {/* Expertise */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 mb-2">Primary Expertise:</p>
        <div className="flex flex-wrap gap-1">
          {agent.capabilities?.primary_expertise?.slice(0, 3).map(skill => (
            <span key={skill} className="glass-badge text-xs">
              {skill}
            </span>
          ))}
          {agent.capabilities?.primary_expertise?.length > 3 && (
            <span className="glass-badge text-xs opacity-50">
              +{agent.capabilities.primary_expertise.length - 3}
            </span>
          )}
        </div>
      </div>

      {/* Tools & Model */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <Brain className="w-3 h-3" />
            {agent.model_preferences?.primary || 'GPT-4'}
          </span>
          {agent.tools?.length > 0 && (
            <span className="flex items-center gap-1">
              <Code className="w-3 h-3" />
              {agent.tools.length}
            </span>
          )}
          {agent.mcp_server && (
            <span className="flex items-center gap-1 text-cyan-400">
              <Database className="w-3 h-3" />
              MCP
            </span>
          )}
        </div>
      </div>

      {/* Instructions Preview */}
      {agent.instructions && (
        <div className="mb-4 opacity-0 group-hover:opacity-100 transition-opacity">
          <p className="text-xs text-gray-500 line-clamp-2">
            "{agent.instructions}"
          </p>
        </div>
      )}

      {/* Action Button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          navigate(`/chat/${agent.id}`);
        }}
        className="liquid-button w-full py-2 text-sm flex items-center justify-center"
      >
        <MessageSquare className="w-4 h-4 mr-1" />
        Start Chat
      </button>
    </div>
  );
};

export default EnhancedAgentCard;
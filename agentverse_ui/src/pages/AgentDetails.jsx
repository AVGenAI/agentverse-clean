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
  Clock
} from 'lucide-react'
import axios from 'axios'

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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="p-6 max-w-7xl mx-auto">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Agent not found</h2>
          <Link to="/agents" className="mt-4 text-purple-600 hover:text-purple-700">
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
        className="inline-flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white mb-6"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to Agents
      </Link>

      {/* Agent Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-8 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <div className="flex items-start gap-6">
          <div className="text-6xl">{agent.avatar || '🤖'}</div>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              {agent.display_name}
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-400 mb-4">
              {agent.canonical_name}
            </p>
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-green-500" />
                <span>Trust Score: {(agent.trust_score * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-center gap-2">
                <Star className="h-4 w-4 text-yellow-500" />
                <span>Performance: {agent.performance_metrics?.success_rate || 95}%</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-blue-500" />
                <span>Response Time: {agent.performance_metrics?.avg_response_time || '1.2s'}</span>
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            <Link
              to={`/chat/${agent.id}`}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors inline-flex items-center gap-2"
            >
              <MessageSquare className="h-5 w-5" />
              Start Chat
            </Link>
            <button className="px-6 py-3 border border-gray-300 dark:border-gray-600 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors inline-flex items-center gap-2">
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
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5 text-purple-600" />
              Capabilities
            </h2>
            
            {/* Primary Expertise */}
            <div className="mb-6">
              <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Primary Expertise</h3>
              <div className="flex flex-wrap gap-2">
                {agent.capabilities?.primary_expertise?.map((skill, idx) => (
                  <span
                    key={idx}
                    className="px-3 py-1.5 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded-lg text-sm font-medium"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Secondary Skills */}
            {agent.capabilities?.secondary_skills && (
              <div className="mb-6">
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Secondary Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.secondary_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg text-sm"
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
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Tools & Technologies</h3>
                <div className="flex flex-wrap gap-2">
                  {agent.capabilities.tools.map((tool, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded-lg text-sm"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Collaboration Network */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Network className="h-5 w-5 text-purple-600" />
              Collaboration Network
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Upstream Dependencies */}
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Works Well With</h3>
                {agent.collaboration?.upstream_dependencies?.map((dep, idx) => (
                  <div key={idx} className="mb-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <span className="font-medium">{dep}</span>
                  </div>
                ))}
              </div>

              {/* Downstream Dependents */}
              <div>
                <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Supports These Agents</h3>
                {agent.collaboration?.downstream_dependents?.map((dep, idx) => (
                  <div key={idx} className="mb-2 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <span className="font-medium">{dep}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Collaboration Style */}
            <div className="mt-6 p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
              <h3 className="font-medium text-gray-700 dark:text-gray-300 mb-2">Collaboration Style</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {agent.collaboration_style?.join(', ')}
              </p>
            </div>
          </div>
        </div>

        {/* Right Column - Stats & Meta */}
        <div className="space-y-6">
          {/* Performance Metrics */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Trophy className="h-5 w-5 text-purple-600" />
              Performance
            </h2>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Success Rate</span>
                  <span className="font-medium">{agent.performance_metrics?.success_rate || 95}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full"
                    style={{ width: `${agent.performance_metrics?.success_rate || 95}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>Reliability</span>
                  <span className="font-medium">{agent.performance_metrics?.reliability || 98}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${agent.performance_metrics?.reliability || 98}%` }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
                <div className="flex justify-between text-sm">
                  <span>Tasks Completed</span>
                  <span className="font-medium">{agent.performance_metrics?.tasks_completed || '2,847'}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Metadata */}
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Target className="h-5 w-5 text-purple-600" />
              Agent Info
            </h2>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Version</span>
                <span className="font-medium">{agent.version || '1.0.0'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Created</span>
                <span className="font-medium">{agent.created_at || 'June 2025'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Domain</span>
                <span className="font-medium capitalize">{agent.domain?.replace(/_/g, ' ')}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Subdomain</span>
                <span className="font-medium capitalize">{agent.subdomain?.replace(/_/g, ' ')}</span>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-6 text-white">
            <h3 className="font-semibold mb-3">Need help with this agent?</h3>
            <p className="text-sm text-purple-100 mb-4">
              Check out our documentation or join the community
            </p>
            <button className="w-full bg-white/20 backdrop-blur-sm px-4 py-2 rounded-lg font-medium hover:bg-white/30 transition-colors">
              View Documentation
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
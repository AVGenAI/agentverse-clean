import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  Activity, Brain, Bot, Server, Zap, MessageSquare, 
  TrendingUp, Users, Globe, Sparkles, Clock, BarChart3,
  Shield, Cpu, Database, Cloud
} from 'lucide-react'
import axios from 'axios'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

const DashboardGlass = () => {
  const navigate = useNavigate()
  const [currentTime, setCurrentTime] = useState(new Date())

  // Update time
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Fetch system health
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/health`)
      return response.data
    },
    refetchInterval: 5000
  })

  // Fetch agents
  const { data: agentsData } = useQuery({
    queryKey: ['agents-overview'],
    queryFn: async () => {
      const response = await axios.post(`${API_URL}/agents`, {
        limit: 5,
        offset: 0
      })
      return response.data
    }
  })

  // Fetch MCP servers
  const { data: mcpServers } = useQuery({
    queryKey: ['mcp-servers-overview'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/mcp/servers`)
      return response.data
    }
  })

  // Fetch active couplings
  const { data: couplings } = useQuery({
    queryKey: ['mcp-couplings-overview'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/mcp/couplings`)
      return response.data
    }
  })

  const stats = [
    {
      title: 'Total Agents',
      value: agentsData?.total || 0,
      icon: Bot,
      color: 'from-blue-400 to-blue-600',
      change: '+12%',
      trend: 'up'
    },
    {
      title: 'Active Sessions',
      value: health?.active_sessions || 0,
      icon: MessageSquare,
      color: 'from-green-400 to-green-600',
      change: '+5%',
      trend: 'up'
    },
    {
      title: 'MCP Servers',
      value: mcpServers?.length || 0,
      icon: Server,
      color: 'from-purple-400 to-purple-600',
      change: '+8%',
      trend: 'up'
    },
    {
      title: 'Active Couplings',
      value: couplings?.filter(c => c.active).length || 0,
      icon: Zap,
      color: 'from-yellow-400 to-amber-600',
      change: '+15%',
      trend: 'up'
    }
  ]

  const recentActivities = [
    { type: 'agent_created', message: 'New SRE Agent deployed', time: '2 min ago', icon: Bot },
    { type: 'coupling_active', message: 'ServiceNow MCP connected', time: '5 min ago', icon: Zap },
    { type: 'chat_started', message: 'User started chat with Django Expert', time: '10 min ago', icon: MessageSquare },
    { type: 'server_added', message: 'Database MCP server registered', time: '15 min ago', icon: Server }
  ]

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">Agent Verse Dashboard</h1>
            <p className="flex items-center gap-2" style={{ color: 'var(--text-secondary)' }}>
              <Clock className="w-4 h-4" />
              {currentTime.toLocaleString()}
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="glass-card px-4 py-2 flex items-center gap-2">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm">All Systems Operational</span>
            </div>
            <button
              onClick={() => navigate('/agents/create')}
              className="liquid-button flex items-center"
            >
              <Sparkles className="w-5 h-5 mr-2" />
              Create Agent
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <div key={index} className="glass-card p-6 hover:scale-[1.02] transition-all">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg bg-gradient-to-r ${stat.color}`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
                <div className={`flex items-center gap-1 text-sm ${
                  stat.trend === 'up' ? 'text-green-400' : 'text-red-400'
                }`}>
                  <TrendingUp className="w-4 h-4" />
                  {stat.change}
                </div>
              </div>
              <div className="text-3xl font-bold gradient-text mb-1">{stat.value}</div>
              <div className="text-sm text-gray-400">{stat.title}</div>
            </div>
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* System Health */}
          <div className="lg:col-span-2">
            <div className="glass-card p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Activity className="w-5 h-5 mr-2 text-green-400" />
                System Health
              </h2>
              
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">API Response Time</span>
                    <span className="text-sm font-medium text-green-400">42ms</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-green-400 to-green-600 rounded-full" style={{ width: '95%' }}></div>
                  </div>
                </div>
                
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">CPU Usage</span>
                    <span className="text-sm font-medium text-blue-400">38%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-blue-400 to-blue-600 rounded-full" style={{ width: '38%' }}></div>
                  </div>
                </div>
                
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Memory Usage</span>
                    <span className="text-sm font-medium text-purple-400">52%</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-purple-400 to-purple-600 rounded-full" style={{ width: '52%' }}></div>
                  </div>
                </div>
                
                <div className="glass-card p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-gray-400">Active Connections</span>
                    <span className="text-sm font-medium text-yellow-400">127</span>
                  </div>
                  <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-yellow-400 to-amber-600 rounded-full" style={{ width: '63%' }}></div>
                  </div>
                </div>
              </div>

              {/* LLM Providers Status */}
              <h3 className="text-lg font-semibold mb-3 flex items-center">
                <Brain className="w-5 h-5 mr-2 text-purple-400" />
                LLM Providers
              </h3>
              <div className="space-y-2">
                {Object.entries(health?.llm_providers || {}).map(([provider, status]) => (
                  <div key={provider} className="flex items-center justify-between glass-card p-3">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        status.available ? 'bg-green-400' : 'bg-red-400'
                      }`}></div>
                      <span className="font-medium capitalize">{provider}</span>
                    </div>
                    <span className="text-sm text-gray-400">
                      {status.available ? 'Connected' : 'Disconnected'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recent Activity */}
          <div>
            <div className="glass-card p-6">
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Clock className="w-5 h-5 mr-2 text-blue-400" />
                Recent Activity
              </h2>
              
              <div className="space-y-3">
                {recentActivities.map((activity, index) => (
                  <div key={index} className="flex items-start gap-3 glass-card p-3">
                    <div className="p-2 rounded-lg bg-gray-700/50">
                      <activity.icon className="w-4 h-4 text-gray-400" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm">{activity.message}</p>
                      <p className="text-xs text-gray-400">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
              
              <button className="w-full mt-4 liquid-button py-2 text-sm">
                View All Activity
              </button>
            </div>
          </div>
        </div>

        {/* Recent Agents */}
        <div className="mt-6">
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center">
                <Bot className="w-5 h-5 mr-2 text-blue-400" />
                Recent Agents
              </h2>
              <button
                onClick={() => navigate('/agents')}
                className="text-sm text-purple-400 hover:text-purple-300"
              >
                View All →
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {agentsData?.agents?.slice(0, 5).map(agent => (
                <div
                  key={agent.id}
                  className="glass-card p-4 text-center hover:scale-[1.05] transition-all cursor-pointer"
                  onClick={() => navigate(`/chat/${agent.id}`)}
                >
                  <div className="text-3xl mb-2">{agent.avatar || '🤖'}</div>
                  <h3 className="font-medium text-sm line-clamp-1">
                    {agent.display_name || agent.canonical_name}
                  </h3>
                  <div className="flex justify-center gap-1 mt-2">
                    {agent.skills?.slice(0, 2).map((skill, i) => (
                      <span key={i} className="glass-badge text-xs py-1 px-2">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <button
            onClick={() => navigate('/agents')}
            className="glass-card p-6 hover:scale-[1.02] transition-all flex flex-col items-center"
          >
            <Bot className="w-8 h-8 mb-2 text-blue-400" />
            <span className="font-medium">Browse Agents</span>
          </button>
          
          <button
            onClick={() => navigate('/mcp-integration')}
            className="glass-card p-6 hover:scale-[1.02] transition-all flex flex-col items-center"
          >
            <Zap className="w-8 h-8 mb-2 text-yellow-400" />
            <span className="font-medium">MCP Integration</span>
          </button>
          
          <button
            onClick={() => navigate('/agents/create')}
            className="glass-card p-6 hover:scale-[1.02] transition-all flex flex-col items-center"
          >
            <Sparkles className="w-8 h-8 mb-2 text-purple-400" />
            <span className="font-medium">Create Agent</span>
          </button>
          
          <button
            onClick={() => navigate('/settings')}
            className="glass-card p-6 hover:scale-[1.02] transition-all flex flex-col items-center"
          >
            <Shield className="w-8 h-8 mb-2 text-green-400" />
            <span className="font-medium">Settings</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardGlass
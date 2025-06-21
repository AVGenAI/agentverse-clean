import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { 
  Brain, Bot, Zap, Database, Globe, MessageSquare,
  GitBranch, FileText, Cpu, Play, ArrowRight,
  Activity, TrendingUp, Users, Server
} from 'lucide-react'
import axios from 'axios'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

const DashboardVectorShift = () => {
  const navigate = useNavigate()

  // Apply VectorShift theme by default
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', 'vectorshift')
  }, [])

  // Fetch system stats
  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/health`)
      return response.data
    },
    refetchInterval: 5000
  })

  const { data: agentsData } = useQuery({
    queryKey: ['agents-count'],
    queryFn: async () => {
      const response = await axios.post(`${API_URL}/agents`, { limit: 1, offset: 0 })
      return response.data
    }
  })

  const quickActions = [
    {
      title: 'Choose AI Model',
      description: 'Select from leading AI providers',
      icon: Brain,
      color: 'from-purple-600 to-purple-700',
      path: '/llm-providers',
      badge: 'New',
      bgColor: 'bg-purple-600/20'
    },
    {
      title: 'Build Pipeline',
      description: 'Create visual agent workflows',
      icon: GitBranch,
      color: 'from-blue-600 to-blue-700',
      path: '/pipeline-builder',
      badge: 'Beta',
      bgColor: 'bg-blue-600/20'
    },
    {
      title: 'Browse Agents',
      description: `${agentsData?.total || '1000+'} specialized agents`,
      icon: Bot,
      color: 'from-green-600 to-green-700',
      path: '/agents',
      bgColor: 'bg-green-600/20'
    },
    {
      title: 'Connect Tools',
      description: 'MCP servers & integrations',
      icon: Zap,
      color: 'from-orange-600 to-orange-700',
      path: '/mcp-integration',
      bgColor: 'bg-orange-600/20'
    }
  ]

  const workflowSteps = [
    { icon: Brain, label: 'Select Model', sublabel: 'OpenAI, Claude, Gemini' },
    { icon: Database, label: 'Connect Tools', sublabel: 'Databases, APIs, Files' },
    { icon: Bot, label: 'Deploy Agent', sublabel: 'Custom instructions' },
    { icon: MessageSquare, label: 'Start Chatting', sublabel: 'Real-time responses' }
  ]

  const stats = [
    { label: 'Active Agents', value: health?.agents_loaded || '0', icon: Bot, trend: '+12%' },
    { label: 'API Calls', value: '2.4M', icon: Activity, trend: '+8%' },
    { label: 'Users', value: '15K', icon: Users, trend: '+25%' },
    { label: 'Uptime', value: '99.9%', icon: Server, trend: '0%' }
  ]

  return (
    <div className="min-h-screen bg-gradient p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 gradient-text">
            AgentVerse Platform
          </h1>
          <p className="text-xl text-gray-400">
            Build, deploy, and scale AI agents with any LLM
          </p>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat, idx) => (
            <div key={idx} className="vs-card text-center group hover:border-purple-500/50 transition-all">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-purple-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <stat.icon className="w-6 h-6 text-purple-400" />
              </div>
              <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
              <div className="text-sm text-gray-300 font-medium">{stat.label}</div>
              <div className={`text-xs mt-2 font-medium ${
                stat.trend.startsWith('+') ? 'text-green-400' : 'text-gray-500'
              }`}>
                {stat.trend}
              </div>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {quickActions.map((action, idx) => (
            <div
              key={idx}
              onClick={() => navigate(action.path)}
              className="group cursor-pointer"
            >
              <div className="vs-card hover:scale-105 transition-all duration-300 hover:border-purple-500/50">
                <div className={`w-16 h-16 rounded-2xl ${action.bgColor} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <action.icon className="w-8 h-8 text-white" />
                </div>
                
                <h3 className="text-lg font-semibold mb-2 text-white flex items-center justify-between">
                  {action.title}
                  {action.badge && (
                    <span className="text-xs px-2 py-0.5 rounded bg-purple-500/30 text-purple-300 border border-purple-500/30">
                      {action.badge}
                    </span>
                  )}
                </h3>
                
                <p className="text-sm text-gray-400 mb-4 leading-relaxed">
                  {action.description}
                </p>
                
                <div className="flex items-center text-purple-400 text-sm font-medium group-hover:text-purple-300 transition-colors">
                  Get started
                  <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Workflow Section */}
        <div className="vs-card mb-8 overflow-hidden">
          <h2 className="text-2xl font-semibold mb-8 text-white">How It Works</h2>
          
          <div className="flex items-center justify-center gap-8 flex-wrap">
            {workflowSteps.map((step, idx) => (
              <React.Fragment key={idx}>
                <div className="group">
                  <div className="vs-node hover:border-purple-500/50 hover:scale-105 transition-all cursor-pointer">
                    <div className="w-16 h-16 mx-auto mb-3 rounded-xl bg-purple-600/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <step.icon className="w-8 h-8 text-purple-400" />
                    </div>
                    <div className="font-medium text-white">{step.label}</div>
                    <div className="text-xs text-gray-400 mt-1">{step.sublabel}</div>
                  </div>
                </div>
                {idx < workflowSteps.length - 1 && (
                  <div className="hidden md:block">
                    <ArrowRight className="w-6 h-6 text-purple-400/50" />
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <div className="vs-card inline-block px-12 py-10">
            <h2 className="text-3xl font-bold mb-4 text-white">
              Ready to build intelligent AI agents?
            </h2>
            <p className="text-gray-300 mb-8 max-w-2xl mx-auto text-lg">
              Join thousands of developers using AgentVerse to create powerful AI applications
              with any language model and tool integration.
            </p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => navigate('/agents/create')}
                className="vs-button-primary"
              >
                Create Your First Agent
              </button>
              <button
                onClick={() => navigate('/pipeline-builder')}
                className="px-6 py-3 text-gray-300 hover:text-white transition-colors font-medium"
              >
                Explore Pipelines →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardVectorShift
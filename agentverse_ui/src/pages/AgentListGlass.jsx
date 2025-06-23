import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, MessageSquare, Bot, Brain, Sparkles, Filter, Grid, List, Plus, Cpu, Activity } from 'lucide-react'
import axios from 'axios'
import EnhancedAgentCard from '../components/EnhancedAgentCard'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

const AgentListGlass = () => {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [viewMode, setViewMode] = useState('grid')
  const [showFilters, setShowFilters] = useState(false)

  // Fetch agents
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await axios.post(`${API_URL}/agents`, {
        limit: 100,
        offset: 0
      })
      return response.data.agents
    }
  })

  // Get unique categories
  const categories = ['all', ...new Set(agents?.map(a => a.category || 'general').filter(Boolean))]

  // Filter agents
  const filteredAgents = agents?.filter(agent => {
    const matchesSearch = !searchTerm || 
      agent.display_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.canonical_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      agent.skills?.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase()))
    
    const matchesCategory = selectedCategory === 'all' || agent.category === selectedCategory
    
    return matchesSearch && matchesCategory
  }) || []

  const getAgentAvatar = (agent) => {
    if (agent.avatar) return agent.avatar
    if (agent.display_name?.includes('SRE')) return '🛠️'
    if (agent.display_name?.includes('Support')) return '🎧'
    if (agent.display_name?.includes('Django')) return '🐍'
    if (agent.display_name?.includes('DevOps')) return '⚙️'
    if (agent.display_name?.includes('Data')) return '📊'
    return '🤖'
  }

  const getAgentStatus = (agent) => {
    // Mock status - in real app, this would come from agent data
    const statuses = ['active', 'idle', 'busy']
    const status = statuses[Math.floor(Math.random() * statuses.length)]
    
    const statusConfig = {
      active: { color: 'bg-green-400', text: 'Active' },
      idle: { color: 'bg-yellow-400', text: 'Idle' },
      busy: { color: 'bg-red-400', text: 'Busy' }
    }
    
    return statusConfig[status]
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold mb-4 gradient-text">AI Agent Universe</h1>
          <p className="text-xl text-gray-300 glass-card inline-block px-6 py-3">
            <Sparkles className="inline w-5 h-5 mr-2" />
            Discover and interact with {agents?.length || 0} intelligent AI agents
          </p>
        </div>

        {/* Controls Bar */}
        <div className="glass-card p-4 mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search agents by name, skills, or capabilities..."
                className="glass-input pl-12"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Category Filter */}
            <select
              className="glass-input w-full lg:w-48"
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              {categories.map(cat => (
                <option key={cat} value={cat} className="bg-gray-800">
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>

            {/* View Mode Toggle */}
            <div className="glass-card p-1 inline-flex">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded transition-all ${
                  viewMode === 'grid' 
                    ? 'bg-purple-500 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <Grid className="w-5 h-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded transition-all ${
                  viewMode === 'list' 
                    ? 'bg-purple-500 text-white' 
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                <List className="w-5 h-5" />
              </button>
            </div>

            {/* Create Agent Button */}
            <button
              onClick={() => navigate('/agents/create')}
              className="liquid-button flex items-center"
            >
              <Plus className="w-5 h-5 mr-2" />
              Create Agent
            </button>
          </div>

          {/* Active Filters */}
          {(searchTerm || selectedCategory !== 'all') && (
            <div className="flex items-center gap-2 mt-4">
              <span className="text-sm text-gray-400">Active filters:</span>
              {searchTerm && (
                <span className="glass-badge">
                  Search: {searchTerm}
                  <button
                    onClick={() => setSearchTerm('')}
                    className="ml-2 text-xs hover:text-red-400"
                  >
                    ×
                  </button>
                </span>
              )}
              {selectedCategory !== 'all' && (
                <span className="glass-badge">
                  Category: {selectedCategory}
                  <button
                    onClick={() => setSelectedCategory('all')}
                    className="ml-2 text-xs hover:text-red-400"
                  >
                    ×
                  </button>
                </span>
              )}
            </div>
          )}
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center p-12">
            <div className="liquid-loader"></div>
          </div>
        )}

        {/* Agents Grid/List */}
        {!isLoading && filteredAgents.length > 0 && (
          <div className={
            viewMode === 'grid' 
              ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
              : 'space-y-4'
          }>
            {filteredAgents.map(agent => (
              <EnhancedAgentCard 
                key={agent.id} 
                agent={agent} 
                viewMode={viewMode} 
              />
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && filteredAgents.length === 0 && (
          <div className="text-center py-12 glass-card">
            <Bot className="w-16 h-16 mx-auto mb-4 text-gray-500" />
            <h3 className="text-xl font-semibold mb-2">No agents found</h3>
            <p className="text-gray-400 mb-6">
              {searchTerm 
                ? `No agents match "${searchTerm}"`
                : 'No agents available in this category'}
            </p>
            <button
              onClick={() => {
                setSearchTerm('')
                setSelectedCategory('all')
              }}
              className="liquid-button"
            >
              Clear Filters
            </button>
          </div>
        )}

        {/* Stats Footer */}
        <div className="mt-12 glass-card p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <Activity className="w-8 h-8 mx-auto mb-2 text-green-400" />
              <div className="text-2xl font-bold gradient-text">{agents?.length || 0}</div>
              <div className="text-sm text-gray-400">Total Agents</div>
            </div>
            <div>
              <Cpu className="w-8 h-8 mx-auto mb-2 text-blue-400" />
              <div className="text-2xl font-bold gradient-text">
                {agents?.filter(a => a.mcp_server_name).length || 0}
              </div>
              <div className="text-sm text-gray-400">MCP Connected</div>
            </div>
            <div>
              <Brain className="w-8 h-8 mx-auto mb-2 text-purple-400" />
              <div className="text-2xl font-bold gradient-text">{categories.length - 1}</div>
              <div className="text-sm text-gray-400">Categories</div>
            </div>
            <div>
              <Sparkles className="w-8 h-8 mx-auto mb-2 text-yellow-400" />
              <div className="text-2xl font-bold gradient-text">∞</div>
              <div className="text-sm text-gray-400">Possibilities</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AgentListGlass
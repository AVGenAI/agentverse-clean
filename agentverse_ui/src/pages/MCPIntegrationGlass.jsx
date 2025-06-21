import React, { useState, useEffect } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Loader2, Link, Unlink, Activity, Server, Bot, Zap, CheckCircle, AlertCircle, Sparkles, Cpu, Globe } from 'lucide-react'
import axios from 'axios'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

const MCPIntegrationGlass = () => {
  const [selectedAgent, setSelectedAgent] = useState(null)
  const [selectedServer, setSelectedServer] = useState(null)
  const [activeTab, setActiveTab] = useState('coupling')
  const [agentSearch, setAgentSearch] = useState('')

  // Animated background orbs
  useEffect(() => {
    const handleMouseMove = (e) => {
      const x = e.clientX / window.innerWidth
      const y = e.clientY / window.innerHeight
      
      document.querySelectorAll('.orb').forEach((orb, index) => {
        const speed = (index + 1) * 0.01
        orb.style.transform = `translate(${x * speed * 50}px, ${y * speed * 50}px)`
      })
    }
    
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Fetch agents
  const { data: agents, isLoading: agentsLoading, refetch: refetchAgents } = useQuery({
    queryKey: ['agents'],
    queryFn: async () => {
      const response = await axios.post(`${API_URL}/agents`, {
        limit: 100,
        offset: 0
      })
      return response.data.agents
    },
    staleTime: 0
  })

  // Fetch MCP servers
  const { data: mcpServers, isLoading: serversLoading } = useQuery({
    queryKey: ['mcp-servers'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/mcp/servers`)
      return response.data
    }
  })

  // Fetch active couplings
  const { data: couplings, refetch: refetchCouplings } = useQuery({
    queryKey: ['mcp-couplings'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/mcp/couplings`)
      return response.data
    }
  })

  // Create coupling mutation
  const createCoupling = useMutation({
    mutationFn: async (data) => {
      const response = await axios.post(`${API_URL}/api/mcp/couplings`, data)
      return response.data
    },
    onSuccess: () => {
      refetchCouplings()
      setSelectedAgent(null)
      setSelectedServer(null)
    }
  })

  const getCompatibilityColor = (level) => {
    const colors = {
      'PERFECT': 'from-green-400 to-emerald-500',
      'HIGH': 'from-blue-400 to-indigo-500',
      'MEDIUM': 'from-yellow-400 to-amber-500',
      'LOW': 'from-orange-400 to-red-500',
      'MINIMAL': 'from-red-400 to-pink-500',
      'INCOMPATIBLE': 'from-gray-400 to-gray-500'
    }
    return colors[level] || colors['INCOMPATIBLE']
  }

  const getServerIcon = (type) => {
    const icons = {
      'servicenow': '🎫',
      'database': '💾',
      'monitoring': '📊',
      'ci_cd': '⚡',
      'messaging': '💬',
      'analytics': '📈',
      'security': '🛡️',
      'cloud_provider': '☁️'
    }
    return icons[type] || '🔌'
  }

  return (
    <div className="min-h-screen bg-gradient text-white p-6">
      {/* Animated Background */}
      <div className="orb-container">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold mb-4 gradient-text">MCP Integration Hub</h1>
          <p className="text-xl text-gray-300 glass-card inline-block px-6 py-3">
            <Sparkles className="inline w-5 h-5 mr-2" />
            Connect agents with Model Context Protocol servers to unlock infinite possibilities
          </p>
        </div>

        {/* Tabs */}
        <div className="flex justify-center mb-8">
          <div className="glass-card p-1 inline-flex rounded-full">
            {['coupling', 'active', 'servers'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-3 rounded-full font-medium transition-all ${
                  activeTab === tab
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                    : 'text-gray-300 hover:text-white'
                }`}
              >
                {tab === 'coupling' && <Link className="inline w-4 h-4 mr-2" />}
                {tab === 'active' && <Activity className="inline w-4 h-4 mr-2" />}
                {tab === 'servers' && <Server className="inline w-4 h-4 mr-2" />}
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'coupling' && (
          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center">
              <Zap className="w-6 h-6 mr-3 text-yellow-400" />
              Create Dynamic Agent-MCP Coupling
            </h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Agent Selection */}
              <div>
                <label className="block text-sm font-medium mb-3 text-gray-300">
                  <Bot className="inline w-4 h-4 mr-2" />
                  Select AI Agent
                </label>
                <input
                  type="text"
                  placeholder="Search agents..."
                  className="glass-input mb-4"
                  value={agentSearch}
                  onChange={(e) => setAgentSearch(e.target.value)}
                />
                <div className="glass-card p-4 max-h-96 overflow-y-auto">
                  {agentsLoading ? (
                    <div className="flex justify-center p-8">
                      <div className="liquid-loader"></div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {agents?.filter(agent => {
                        const searchLower = agentSearch.toLowerCase()
                        return !searchLower || 
                          agent.display_name?.toLowerCase().includes(searchLower) ||
                          agent.canonical_name?.toLowerCase().includes(searchLower)
                      }).map(agent => (
                        <div
                          key={agent.id}
                          onClick={() => setSelectedAgent(agent)}
                          className={`glass-card p-4 cursor-pointer transition-all hover:scale-[1.02] ${
                            selectedAgent?.id === agent.id ? 'ring-2 ring-purple-500' : ''
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div>
                              <h4 className="font-semibold flex items-center">
                                <span className="text-2xl mr-2">{agent.avatar || '🤖'}</span>
                                {agent.display_name || agent.canonical_name}
                              </h4>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {agent.skills?.slice(0, 3).map(skill => (
                                  <span key={skill} className="glass-badge text-xs">
                                    {skill}
                                  </span>
                                ))}
                              </div>
                            </div>
                            {agent.display_name?.includes('SRE') && (
                              <span className="text-yellow-400">
                                <Sparkles className="w-5 h-5" />
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Server Selection */}
              <div>
                <label className="block text-sm font-medium mb-3 text-gray-300">
                  <Server className="inline w-4 h-4 mr-2" />
                  Select MCP Server
                </label>
                <div className="glass-card p-4 max-h-[480px] overflow-y-auto">
                  {serversLoading ? (
                    <div className="flex justify-center p-8">
                      <div className="liquid-loader"></div>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {mcpServers?.map(server => (
                        <div
                          key={server.id}
                          onClick={() => setSelectedServer(server)}
                          className={`glass-card p-4 cursor-pointer transition-all hover:scale-[1.02] ${
                            selectedServer?.id === server.id ? 'ring-2 ring-purple-500' : ''
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex-1">
                              <h4 className="font-semibold flex items-center">
                                <span className="text-2xl mr-2">{getServerIcon(server.type)}</span>
                                {server.name}
                              </h4>
                              <p className="text-sm text-gray-400 mt-1">{server.description}</p>
                              <div className="flex flex-wrap gap-2 mt-2">
                                {server.toolPackages?.slice(0, 3).map(pkg => (
                                  <span key={pkg} className="glass-badge text-xs">
                                    {pkg}
                                  </span>
                                ))}
                              </div>
                            </div>
                            {server.connected ? (
                              <CheckCircle className="w-5 h-5 text-green-400" />
                            ) : (
                              <AlertCircle className="w-5 h-5 text-gray-400" />
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Connection Preview */}
            {selectedAgent && selectedServer && (
              <div className="mt-8 glass-card p-6 shimmer">
                <h3 className="text-lg font-semibold mb-4 flex items-center">
                  <Cpu className="w-5 h-5 mr-2 text-purple-400" />
                  Connection Preview
                </h3>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-center">
                      <div className="text-3xl mb-1">{selectedAgent.avatar || '🤖'}</div>
                      <p className="text-sm">{selectedAgent.display_name}</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 h-0.5 bg-gradient-to-r from-purple-500 to-pink-500"></div>
                      <Zap className="w-6 h-6 text-yellow-400" />
                      <div className="w-16 h-0.5 bg-gradient-to-r from-pink-500 to-purple-500"></div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl mb-1">{getServerIcon(selectedServer.type)}</div>
                      <p className="text-sm">{selectedServer.name}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => createCoupling.mutate({
                      agentId: selectedAgent.id,
                      serverId: selectedServer.id
                    })}
                    disabled={createCoupling.isLoading}
                    className="liquid-button flex items-center"
                  >
                    {createCoupling.isLoading ? (
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    ) : (
                      <Link className="w-5 h-5 mr-2" />
                    )}
                    Create Coupling
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'active' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {couplings?.map(coupling => (
              <div key={coupling.id} className="glass-card p-6 hover:scale-[1.02] transition-all">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <Bot className="w-5 h-5 text-blue-400" />
                    <Zap className="w-4 h-4 text-yellow-400" />
                    <Server className="w-5 h-5 text-green-400" />
                  </div>
                  <span className={`glass-badge ${coupling.active ? 'bg-green-500/20 border-green-500/30' : 'bg-gray-500/20 border-gray-500/30'}`}>
                    {coupling.active ? 'Active' : 'Inactive'}
                  </span>
                </div>
                
                <h3 className="font-semibold text-lg mb-1">{coupling.agentName}</h3>
                <p className="text-sm text-gray-400 mb-3">{coupling.serverName}</p>
                
                <div className="mb-4">
                  <span className="text-xs text-gray-500">Compatibility</span>
                  <div className={`mt-1 h-2 rounded-full bg-gradient-to-r ${getCompatibilityColor(coupling.compatibility)}`}></div>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 liquid-button py-2 text-sm">
                    <Activity className="w-4 h-4 mr-1 inline" />
                    Test
                  </button>
                  <button className="flex-1 liquid-button py-2 text-sm bg-red-500/20 border-red-500/30">
                    <Unlink className="w-4 h-4 mr-1 inline" />
                    Disconnect
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'servers' && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mcpServers?.map(server => (
              <div key={server.id} className="glass-card p-6 hover:scale-[1.02] transition-all">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold flex items-center">
                    <span className="text-3xl mr-3">{getServerIcon(server.type)}</span>
                    {server.name}
                  </h3>
                  <Globe className="w-5 h-5 text-blue-400" />
                </div>
                
                <p className="text-gray-400 mb-4">{server.description}</p>
                
                <div className="space-y-3">
                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider">Type</span>
                    <p className="glass-badge inline-block mt-1">{server.type}</p>
                  </div>
                  
                  <div>
                    <span className="text-xs text-gray-500 uppercase tracking-wider">Tool Packages</span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      {server.toolPackages?.map(pkg => (
                        <span key={pkg} className="glass-badge text-xs">
                          {pkg}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="pt-3 border-t border-gray-700/50">
                    <div className="flex items-center justify-between">
                      <span className="flex items-center">
                        {server.connected ? (
                          <>
                            <CheckCircle className="w-4 h-4 text-green-400 mr-2" />
                            <span className="text-sm text-green-400">Connected</span>
                          </>
                        ) : (
                          <>
                            <AlertCircle className="w-4 h-4 text-gray-400 mr-2" />
                            <span className="text-sm text-gray-400">Disconnected</span>
                          </>
                        )}
                      </span>
                      <button className="liquid-button py-2 px-4 text-sm">
                        Configure
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MCPIntegrationGlass
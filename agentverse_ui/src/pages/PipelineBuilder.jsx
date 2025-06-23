import React, { useState, useEffect, useRef } from 'react'
import { 
  Database, Brain, FileText, Globe, MessageSquare, 
  Cpu, GitBranch, ArrowRight, Plus, Settings,
  Play, Save, Upload, Download, Zap, Code, Shield,
  Server, Check, X, AlertCircle, Loader
} from 'lucide-react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import axios from 'axios'
import { toast } from 'react-hot-toast'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

const PipelineBuilder = () => {
  const queryClient = useQueryClient()
  const [pipelineName, setPipelineName] = useState('My Pipeline')
  const [pipelineDescription, setPipelineDescription] = useState('AI agent workflow')
  const [nodes, setNodes] = useState([])
  const [connections, setConnections] = useState([])
  const [selectedNode, setSelectedNode] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [dragNode, setDragNode] = useState(null)
  const [isRunning, setIsRunning] = useState(false)
  const [showConfigModal, setShowConfigModal] = useState(false)
  const [currentPipelineId, setCurrentPipelineId] = useState(null)
  const [connectionMode, setConnectionMode] = useState(false)
  const [connectionStart, setConnectionStart] = useState(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [executionResult, setExecutionResult] = useState(null)
  const [executionError, setExecutionError] = useState(null)
  const canvasRef = useRef(null)
  
  // Theme is now managed by LayoutGlass component
  
  // Initialize with default pipeline
  useEffect(() => {
    setNodes([
      { id: 'node-1', type: 'input', label: 'Input', position: { x: 100, y: 200 }, config: {} },
      { id: 'node-2', type: 'agent', label: 'AI Agent', position: { x: 350, y: 200 }, config: { agent_id: '' } },
      { id: 'node-3', type: 'output', label: 'Output', position: { x: 600, y: 200 }, config: {} }
    ])
    setConnections([
      { from: 'node-1', to: 'node-2' },
      { from: 'node-2', to: 'node-3' }
    ])
  }, [])

  // Fetch node types from API
  const { data: nodeTypesData } = useQuery({
    queryKey: ['node-types'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/pipeline/node-types`)
      return response.data.node_types
    }
  })
  
  // Fetch available agents
  const { data: agentsData } = useQuery({
    queryKey: ['agents-list'],
    queryFn: async () => {
      const response = await axios.post(`${API_URL}/agents`, { limit: 100, offset: 0 })
      return response.data
    }
  })
  
  // Map icon names to components
  const iconMap = {
    Upload, Download, Brain, Server, Database, FileText, Globe, MessageSquare,
    Code, Shield, Cpu, GitBranch, Zap
  }
  
  const nodeTypes = nodeTypesData?.map(nt => ({
    ...nt,
    icon: iconMap[nt.icon] || Brain
  })) || []

  // Create pipeline mutation
  const createPipelineMutation = useMutation({
    mutationFn: async (pipelineData) => {
      const response = await axios.post(`${API_URL}/api/pipeline/pipelines`, pipelineData)
      return response.data
    },
    onSuccess: (data) => {
      setCurrentPipelineId(data.id)
      toast.success('Pipeline saved successfully!')
      queryClient.invalidateQueries(['pipelines'])
    },
    onError: (error) => {
      toast.error(`Failed to save pipeline: ${error.response?.data?.detail || error.message}`)
    }
  })
  
  // Update pipeline mutation
  const updatePipelineMutation = useMutation({
    mutationFn: async ({ id, data }) => {
      const response = await axios.put(`${API_URL}/api/pipeline/pipelines/${id}`, data)
      return response.data
    },
    onSuccess: () => {
      toast.success('Pipeline updated successfully!')
      queryClient.invalidateQueries(['pipelines'])
    },
    onError: (error) => {
      toast.error(`Failed to update pipeline: ${error.response?.data?.detail || error.message}`)
    }
  })
  
  // Execute pipeline mutation
  const executePipelineMutation = useMutation({
    mutationFn: async ({ id, inputData }) => {
      const response = await axios.post(`${API_URL}/api/pipeline/pipelines/${id}/execute`, {
        input_data: inputData,
        config: {}
      })
      return response.data
    },
    onSuccess: (data) => {
      toast.success('Pipeline executed successfully!')
      console.log('Execution result:', data)
    },
    onError: (error) => {
      toast.error(`Pipeline execution failed: ${error.response?.data?.detail || error.message}`)
    }
  })
  
  // Validate pipeline mutation
  const validatePipelineMutation = useMutation({
    mutationFn: async (id) => {
      const response = await axios.post(`${API_URL}/api/pipeline/pipelines/${id}/validate`)
      return response.data
    }
  })
  
  const addNode = (type) => {
    const nodeType = nodeTypes.find(n => n.type === type)
    if (!nodeType) return
    
    const newNode = {
      id: `node-${Date.now()}`,
      type: type,
      label: nodeType.label,
      position: { x: 250 + Math.random() * 200, y: 150 + Math.random() * 200 },
      config: nodeType.config_schema ? Object.keys(nodeType.config_schema).reduce((acc, key) => {
        acc[key] = nodeType.config_schema[key].default || ''
        return acc
      }, {}) : {}
    }
    setNodes([...nodes, newNode])
  }

  const connectNodes = (fromId, toId) => {
    // Don't allow self-connections
    if (fromId === toId) return
    
    // Check if connection already exists
    if (!connections.find(c => c.from === fromId && c.to === toId)) {
      setConnections([...connections, { from: fromId, to: toId }])
      toast.success('Nodes connected')
    }
  }
  
  const removeConnection = (fromId, toId) => {
    setConnections(connections.filter(c => !(c.from === fromId && c.to === toId)))
  }
  
  const removeNode = (nodeId) => {
    setNodes(nodes.filter(n => n.id !== nodeId))
    setConnections(connections.filter(c => c.from !== nodeId && c.to !== nodeId))
    if (selectedNode?.id === nodeId) {
      setSelectedNode(null)
    }
  }
  
  const handleNodeDragStart = (e, node) => {
    setIsDragging(true)
    setDragNode(node)
    e.dataTransfer.effectAllowed = 'move'
  }
  
  const handleNodeDragEnd = (e, node) => {
    setIsDragging(false)
    setDragNode(null)
    
    if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      
      const updatedNodes = nodes.map(n => 
        n.id === node.id ? { ...n, position: { x, y } } : n
      )
      setNodes(updatedNodes)
    }
  }
  
  const savePipeline = async () => {
    // Validate pipeline has required nodes
    const hasInput = nodes.some(n => n.type === 'input')
    const hasOutput = nodes.some(n => n.type === 'output')
    
    if (!hasInput || !hasOutput) {
      toast.error('Pipeline must have at least one Input and one Output node')
      return
    }
    
    const pipelineData = {
      name: pipelineName,
      description: pipelineDescription,
      nodes: nodes.map(n => ({
        id: n.id,
        type: n.type,
        label: n.label,
        position: n.position,
        config: n.config || {}
      })),
      connections: connections
    }
    
    if (currentPipelineId) {
      updatePipelineMutation.mutate({ id: currentPipelineId, data: pipelineData })
    } else {
      createPipelineMutation.mutate(pipelineData)
    }
  }
  
  const runPipeline = async () => {
    if (!currentPipelineId) {
      toast.error('Please save the pipeline first')
      return
    }
    
    // First validate
    const validation = await validatePipelineMutation.mutateAsync(currentPipelineId)
    if (!validation.valid) {
      toast.error(`Pipeline validation failed: ${validation.issues.join(', ')}`)
      return
    }
    
    // Get input from user
    const inputData = prompt('Enter input data for the pipeline (e.g., "Check system status"):')
    if (inputData === null) return
    
    setIsRunning(true)
    setExecutionResult(null)
    setExecutionError(null)
    
    executePipelineMutation.mutate(
      { id: currentPipelineId, inputData },
      {
        onSuccess: (data) => {
          setExecutionResult(data)
          // Show result in a better way
          if (data.result) {
            toast.success('Pipeline completed successfully!')
          }
        },
        onError: (error) => {
          setExecutionError(error.response?.data?.detail || error.message)
        },
        onSettled: () => {
          setIsRunning(false)
        }
      }
    )
  }

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2 gradient-text">Pipeline Builder</h1>
            <p className="text-gray-300 text-lg">
              Build your agent workflow visually
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={runPipeline}
              disabled={isRunning || nodes.length === 0}
              className="av-button-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isRunning ? (
                <><Loader className="w-4 h-4 mr-2 animate-spin" /> Running...</>
              ) : (
                <><Play className="w-4 h-4 mr-2" /> Run Pipeline</>
              )}
            </button>
            <button 
              onClick={savePipeline}
              disabled={nodes.length === 0}
              className="px-6 py-3 bg-gray-800 border border-gray-700 rounded-lg flex items-center hover:bg-gray-700 transition-colors text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4 mr-2" />
              {currentPipelineId ? 'Update' : 'Save'}
            </button>
            {connections.length > 0 && (
              <button
                onClick={() => {
                  if (confirm('Clear all connections?')) {
                    setConnections([])
                    toast.success('All connections cleared')
                  }
                }}
                className="px-4 py-2 text-sm text-red-400 hover:text-red-300 transition-colors"
              >
                Clear Connections
              </button>
            )}
            <button
              onClick={() => {
                // Create a simple test pipeline
                const testNodes = [
                  { id: 'test-input', type: 'input', label: 'User Input', position: { x: 100, y: 200 }, config: {} },
                  { id: 'test-text', type: 'text', label: 'Make Uppercase', position: { x: 350, y: 200 }, config: { operation: 'uppercase' } },
                  { id: 'test-output', type: 'output', label: 'Result', position: { x: 600, y: 200 }, config: {} }
                ]
                const testConnections = [
                  { from: 'test-input', to: 'test-text' },
                  { from: 'test-text', to: 'test-output' }
                ]
                setNodes(testNodes)
                setConnections(testConnections)
                setPipelineName('Test Text Pipeline')
                setPipelineDescription('Simple text transformation pipeline')
                toast.success('Test pipeline created! Click Save, then Run.')
              }}
              className="px-4 py-2 text-sm text-blue-400 hover:text-blue-300 transition-colors"
              title="Create a simple test pipeline"
            >
              Load Test Pipeline
            </button>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar */}
          <div className="col-span-3">
            <div className="av-card">
              <h3 className="text-xl font-bold mb-6 text-white">Components</h3>
              
              <div className="space-y-3">
                {nodeTypes.map((nodeType) => (
                  <button
                    key={nodeType.type}
                    onClick={() => addNode(nodeType.type)}
                    className="w-full group"
                  >
                    <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-4 flex items-center gap-3 hover:bg-gray-800 hover:border-purple-500/50 transition-all text-left">
                      <div className={`w-10 h-10 rounded-lg ${nodeType.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform`}>
                        <nodeType.icon className={`w-5 h-5 ${nodeType.color}`} />
                      </div>
                      <span className="text-sm font-medium text-white">{nodeType.label}</span>
                      <Plus className="w-4 h-4 ml-auto text-gray-400 group-hover:text-purple-400 transition-colors" />
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Node Properties */}
            {selectedNode && (
              <div className="av-card mt-6">
                <h3 className="text-xl font-bold mb-6 flex items-center justify-between text-white">
                  <span className="flex items-center">
                    <Settings className="w-5 h-5 mr-2 text-purple-400" />
                    Properties
                  </span>
                  <button
                    onClick={() => removeNode(selectedNode.id)}
                    className="text-red-400 hover:text-red-300 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-300 font-medium">Name</label>
                    <input
                      type="text"
                      value={selectedNode.label}
                      className="w-full mt-2 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition-colors"
                      onChange={(e) => {
                        const updated = nodes.map(n => 
                          n.id === selectedNode.id 
                            ? { ...n, label: e.target.value }
                            : n
                        )
                        setNodes(updated)
                        setSelectedNode({ ...selectedNode, label: e.target.value })
                      }}
                    />
                  </div>
                  
                  <div>
                    <label className="text-sm text-gray-300 font-medium">Type</label>
                    <p className="mt-2 text-sm text-white bg-gray-800 px-4 py-3 rounded-lg">{selectedNode.type}</p>
                  </div>

                  {/* Dynamic config based on node type */}
                  {selectedNode.type === 'agent' && (
                    <div>
                      <label className="text-sm text-gray-300 font-medium">Agent</label>
                      <select 
                        value={selectedNode.config?.agent_id || ''}
                        onChange={(e) => {
                          const updated = nodes.map(n => 
                            n.id === selectedNode.id 
                              ? { ...n, config: { ...n.config, agent_id: e.target.value } }
                              : n
                          )
                          setNodes(updated)
                          setSelectedNode({ ...selectedNode, config: { ...selectedNode.config, agent_id: e.target.value } })
                        }}
                        className="w-full mt-2 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition-colors"
                      >
                        <option value="">Select an agent...</option>
                        {agentsData?.agents?.map(agent => (
                          <option key={agent.id} value={agent.id}>
                            {agent.display_name || agent.canonical_name} ({agent.llm_config?.model || 'default'})
                          </option>
                        ))}
                      </select>
                    </div>
                  )}
                  
                  {selectedNode.type === 'text' && (
                    <div>
                      <label className="text-sm text-gray-300 font-medium">Operation</label>
                      <select 
                        value={selectedNode.config?.operation || 'uppercase'}
                        onChange={(e) => {
                          const updated = nodes.map(n => 
                            n.id === selectedNode.id 
                              ? { ...n, config: { ...n.config, operation: e.target.value } }
                              : n
                          )
                          setNodes(updated)
                          setSelectedNode({ ...selectedNode, config: { ...selectedNode.config, operation: e.target.value } })
                        }}
                        className="w-full mt-2 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition-colors"
                      >
                        <option value="uppercase">Uppercase</option>
                        <option value="lowercase">Lowercase</option>
                        <option value="reverse">Reverse</option>
                        <option value="word_count">Word Count</option>
                      </select>
                    </div>
                  )}
                  
                  {selectedNode.type === 'mcp_server' && (
                    <>
                      <div>
                        <label className="text-sm text-gray-300 font-medium">Server Name</label>
                        <input
                          type="text"
                          value={selectedNode.config?.server_name || ''}
                          placeholder="e.g., sqlite"
                          className="w-full mt-2 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition-colors"
                          onChange={(e) => {
                            const updated = nodes.map(n => 
                              n.id === selectedNode.id 
                                ? { ...n, config: { ...n.config, server_name: e.target.value } }
                                : n
                            )
                            setNodes(updated)
                            setSelectedNode({ ...selectedNode, config: { ...selectedNode.config, server_name: e.target.value } })
                          }}
                        />
                      </div>
                      <div>
                        <label className="text-sm text-gray-300 font-medium">Tool Name</label>
                        <input
                          type="text"
                          value={selectedNode.config?.tool_name || ''}
                          placeholder="e.g., query"
                          className="w-full mt-2 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white focus:border-purple-500 focus:outline-none transition-colors"
                          onChange={(e) => {
                            const updated = nodes.map(n => 
                              n.id === selectedNode.id 
                                ? { ...n, config: { ...n.config, tool_name: e.target.value } }
                                : n
                            )
                            setNodes(updated)
                            setSelectedNode({ ...selectedNode, config: { ...selectedNode.config, tool_name: e.target.value } })
                          }}
                        />
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Canvas */}
          <div className="col-span-9">
            <div 
              className="av-card h-[600px] relative overflow-hidden bg-gray-900/50" 
              ref={canvasRef}
              onMouseMove={(e) => {
                if (connectionMode && connectionStart) {
                  const rect = canvasRef.current.getBoundingClientRect()
                  setMousePosition({
                    x: e.clientX - rect.left,
                    y: e.clientY - rect.top
                  })
                }
              }}
            >
              {/* Pipeline Info */}
              <div className="absolute top-4 left-4 z-10">
                <input
                  type="text"
                  value={pipelineName}
                  onChange={(e) => setPipelineName(e.target.value)}
                  className="text-2xl font-bold bg-transparent border-b border-gray-700 text-white focus:border-purple-500 focus:outline-none transition-colors mb-2"
                  placeholder="Pipeline Name"
                />
                <input
                  type="text"
                  value={pipelineDescription}
                  onChange={(e) => setPipelineDescription(e.target.value)}
                  className="text-sm text-gray-400 bg-transparent border-b border-gray-800 focus:border-gray-600 focus:outline-none transition-colors w-64"
                  placeholder="Pipeline Description"
                />
              </div>
              {/* Grid Pattern Background */}
              <div className="absolute inset-0 opacity-10">
                <svg width="100%" height="100%">
                  <defs>
                    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
                    </pattern>
                  </defs>
                  <rect width="100%" height="100%" fill="url(#grid)" />
                </svg>
              </div>

              {/* Connections */}
              <svg className="absolute inset-0 w-full h-full" style={{ pointerEvents: connectionMode ? 'none' : 'auto' }}>
                {/* Draw temporary connection line when in connection mode */}
                {connectionMode && connectionStart && (
                  <line
                    x1={connectionStart.position.x + 80}
                    y1={connectionStart.position.y + 40}
                    x2={mousePosition.x}
                    y2={mousePosition.y}
                    stroke="#a855f7"
                    strokeWidth="2"
                    strokeDasharray="5,5"
                    opacity="0.6"
                  />
                )}
                
                {connections.map((conn, idx) => {
                  const fromNode = nodes.find(n => n.id === conn.from)
                  const toNode = nodes.find(n => n.id === conn.to)
                  if (!fromNode || !toNode) return null

                  return (
                    <g key={idx}>
                      <line
                        x1={fromNode.position.x + 80}
                        y1={fromNode.position.y + 40}
                        x2={toNode.position.x}
                        y2={toNode.position.y + 40}
                        stroke="url(#purpleGradient)"
                        strokeWidth="3"
                        strokeDasharray="5,5"
                        className="animate-pulse cursor-pointer hover:stroke-red-500"
                        onClick={(e) => {
                          e.stopPropagation()
                          if (confirm('Delete this connection?')) {
                            removeConnection(conn.from, conn.to)
                          }
                        }}
                        style={{ pointerEvents: 'stroke' }}
                      />
                      <circle
                        cx={toNode.position.x}
                        cy={toNode.position.y + 40}
                        r="6"
                        fill="#a855f7"
                        className="animate-pulse"
                      />
                    </g>
                  )
                })}
                <defs>
                  <linearGradient id="purpleGradient">
                    <stop offset="0%" stopColor="#7c3aed" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#a855f7" stopOpacity="1" />
                  </linearGradient>
                </defs>
              </svg>

              {/* Nodes */}
              {nodes.map((node) => {
                const nodeType = nodeTypes.find(n => n.type === node.type) || { 
                  icon: Brain, 
                  color: 'text-gray-400', 
                  bgColor: 'bg-gray-600/20' 
                }
                const Icon = nodeType.icon
                
                return (
                  <div
                    key={node.id}
                    draggable
                    onDragStart={(e) => handleNodeDragStart(e, node)}
                    onDragEnd={(e) => handleNodeDragEnd(e, node)}
                    className={`absolute transition-all group ${
                      selectedNode?.id === node.id ? 'scale-110 z-20' : ''
                    } ${isDragging && dragNode?.id === node.id ? 'opacity-50' : ''} ${
                      connectionMode ? 'cursor-crosshair' : 'cursor-move'
                    } ${
                      connectionMode && connectionStart?.id === node.id ? 'ring-4 ring-purple-500 rounded-xl' : ''
                    }`}
                    style={{
                      left: `${node.position.x}px`,
                      top: `${node.position.y}px`,
                      minWidth: '160px'
                    }}
                    onClick={(e) => {
                      e.stopPropagation()
                      if (connectionMode) {
                        if (!connectionStart) {
                          // Start connection
                          setConnectionStart(node)
                          toast.info(`Connect from ${node.label}...`)
                        } else if (connectionStart.id !== node.id) {
                          // Complete connection
                          connectNodes(connectionStart.id, node.id)
                          setConnectionStart(null)
                          setConnectionMode(false)
                        }
                      } else {
                        setSelectedNode(node)
                      }
                    }}
                  >
                    <div className={`bg-gray-800 border-2 ${
                      selectedNode?.id === node.id ? 'border-purple-500' : 'border-gray-700'
                    } rounded-xl p-4 hover:border-purple-500/50 transition-all shadow-xl hover:shadow-purple-500/20`}>
                      {/* Config status indicator */}
                      {node.type === 'agent' && (
                        <div className="absolute -top-2 -right-2">
                          {node.config?.agent_id ? (
                            <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                              <Check className="w-4 h-4 text-white" />
                            </div>
                          ) : (
                            <div className="w-6 h-6 rounded-full bg-yellow-500 flex items-center justify-center">
                              <AlertCircle className="w-4 h-4 text-white" />
                            </div>
                          )}
                        </div>
                      )}
                      
                      <div className={`w-12 h-12 rounded-lg ${nodeType.bgColor} flex items-center justify-center mb-3 mx-auto group-hover:scale-110 transition-transform`}>
                        <Icon className={`w-6 h-6 ${nodeType.color}`} />
                      </div>
                      <p className="text-sm font-semibold text-white text-center">{node.label}</p>
                    </div>
                  </div>
                )
              })}

              {/* Instructions */}
              <div className="absolute bottom-4 left-4 right-4 flex justify-between items-center">
                <p className="text-xs text-gray-500">
                  {connectionMode 
                    ? 'Click a node to start connection, then click another to connect them' 
                    : 'Click components to add • Click nodes to select • Drag to move'}
                </p>
                <button
                  onClick={() => {
                    setConnectionMode(!connectionMode)
                    setConnectionStart(null)
                  }}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    connectionMode 
                      ? 'bg-purple-500 text-white' 
                      : 'glass-button'
                  }`}
                >
                  <GitBranch className="w-3 h-3 inline mr-1" />
                  {connectionMode ? 'Cancel Connect' : 'Connect Mode'}
                </button>
              </div>
            </div>

            {/* Pipeline Status */}
            <div className="av-card mt-6">
              <h3 className="text-lg font-semibold mb-3 text-white">Pipeline Status</h3>
              
              {/* Validation Status */}
              {validatePipelineMutation.data && (
                <div className={`mb-4 p-4 rounded-lg border ${
                  validatePipelineMutation.data.valid 
                    ? 'bg-green-900/20 border-green-600/50' 
                    : 'bg-red-900/20 border-red-600/50'
                }`}>
                  <div className="flex items-center gap-2 mb-2">
                    {validatePipelineMutation.data.valid ? (
                      <><Check className="w-5 h-5 text-green-400" /> <span className="text-green-400 font-medium">Pipeline is valid</span></>
                    ) : (
                      <><X className="w-5 h-5 text-red-400" /> <span className="text-red-400 font-medium">Pipeline has issues</span></>
                    )}
                  </div>
                  {!validatePipelineMutation.data.valid && (
                    <ul className="text-sm text-red-300 space-y-1">
                      {validatePipelineMutation.data.issues.map((issue, idx) => (
                        <li key={idx}>• {issue}</li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
              
              {/* Execution Result */}
              {executionResult && (
                <div className="p-4 bg-green-900/20 rounded-lg border border-green-600/50">
                  <h4 className="text-sm font-medium text-green-300 mb-2 flex items-center gap-2">
                    <Check className="w-4 h-4" /> Execution Result:
                  </h4>
                  <div className="text-sm text-white overflow-auto max-h-40">
                    {typeof executionResult.result === 'string' ? (
                      <p className="whitespace-pre-wrap">{executionResult.result}</p>
                    ) : (
                      <pre className="text-xs">
                        {JSON.stringify(executionResult.result || executionResult, null, 2)}
                      </pre>
                    )}
                  </div>
                  {executionResult.execution_id && (
                    <p className="text-xs text-gray-400 mt-2">Execution ID: {executionResult.execution_id}</p>
                  )}
                </div>
              )}
              
              {/* Execution Error */}
              {executionError && (
                <div className="p-4 bg-red-900/20 rounded-lg border border-red-600/50">
                  <h4 className="text-sm font-medium text-red-300 mb-2 flex items-center gap-2">
                    <X className="w-4 h-4" /> Execution Error:
                  </h4>
                  <p className="text-sm text-red-200">{executionError}</p>
                </div>
              )}
              
              <div className="flex items-center gap-4 text-sm mt-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-gray-600"></div>
                  <span className="text-gray-300">Nodes: {nodes.length}</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-purple-600"></div>
                  <span className="text-gray-300">Connections: {connections.length}</span>
                </div>
                {currentPipelineId && (
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-600"></div>
                    <span className="text-gray-300">Saved</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PipelineBuilder
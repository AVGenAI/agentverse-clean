import React, { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Send, Bot, User, Loader2, Sparkles, Brain, Zap, MessageSquare, ArrowLeft } from 'lucide-react'
import axios from 'axios'
import ReactMarkdown from 'react-markdown'
import '../styles/glass.css'

const API_URL = 'http://localhost:8000'

const ChatGlass = () => {
  const { agentId } = useParams()
  const navigate = useNavigate()
  const [message, setMessage] = useState('')
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const messagesEndRef = useRef(null)
  const chatContainerRef = useRef(null)

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

  // Fetch agent details
  const { data: agent } = useQuery({
    queryKey: ['agent', agentId],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/agents/${agentId}`)
      return response.data.agent
    }
  })

  // Create session
  useEffect(() => {
    const createSession = async () => {
      try {
        const response = await axios.post(`${API_URL}/chat/session?agent_id=${agentId}`)
        setSessionId(response.data.session_id)
        
        // Add welcome message
        setMessages([{
          id: 'welcome',
          sender: 'agent',
          content: `Hello! I'm ${agent?.display_name || 'your AI assistant'}. ${agent?.greeting || 'How can I help you today?'}`,
          timestamp: new Date().toISOString()
        }])
      } catch (error) {
        console.error('Failed to create session:', error)
      }
    }

    if (agentId && agent) {
      createSession()
    }
  }, [agentId, agent])

  // Send message mutation
  const sendMessage = useMutation({
    mutationFn: async (content) => {
      const response = await axios.post(`${API_URL}/chat/message`, {
        agent_id: agentId,
        message: content,
        session_id: sessionId
      })
      return response.data
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        id: `agent-${Date.now()}`,
        sender: 'agent',
        content: data.response,
        timestamp: new Date().toISOString()
      }])
    }
  })

  const handleSend = async () => {
    if (!message.trim() || !sessionId) return

    const userMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setMessage('')
    
    sendMessage.mutate(message)
  }

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const getAgentAvatar = () => {
    if (agent?.avatar) return agent.avatar
    if (agent?.display_name?.includes('SRE')) return '🛠️'
    if (agent?.display_name?.includes('Support')) return '🎧'
    if (agent?.display_name?.includes('Django')) return '🐍'
    return '🤖'
  }

  return (
    <div className="min-h-screen bg-gradient text-white">
      {/* Animated Background */}
      <div className="orb-container">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      <div className="h-screen flex flex-col relative z-10">
        {/* Header */}
        <div className="glass-nav p-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/agents')}
                className="glass-card p-2 hover:scale-110 transition-transform"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="text-3xl">{getAgentAvatar()}</div>
                <div>
                  <h1 className="text-xl font-bold gradient-text">
                    {agent?.display_name || agent?.canonical_name}
                  </h1>
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Brain className="w-4 h-4" />
                    {agent?.llm_config?.model || 'GPT-4'}
                    {agent?.mcp_server_name && (
                      <>
                        <Zap className="w-4 h-4 text-yellow-400" />
                        <span>{agent.mcp_server_name}</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {agent?.skills?.slice(0, 3).map(skill => (
                <span key={skill} className="glass-badge">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <div className="flex-1 overflow-y-auto p-4" ref={chatContainerRef}>
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex items-start space-x-3 max-w-[80%] ${
                  msg.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}>
                  <div className="flex-shrink-0">
                    {msg.sender === 'user' ? (
                      <div className="glass-card p-2 rounded-full">
                        <User className="w-6 h-6" />
                      </div>
                    ) : (
                      <div className="text-3xl">{getAgentAvatar()}</div>
                    )}
                  </div>
                  
                  <div className={`glass-card p-4 ${
                    msg.sender === 'user' 
                      ? 'bg-gradient-to-r from-purple-500/20 to-pink-500/20 border-purple-500/30' 
                      : 'shimmer'
                  }`}>
                    <ReactMarkdown className="prose prose-invert prose-sm max-w-none">
                      {msg.content}
                    </ReactMarkdown>
                    <div className="text-xs text-gray-400 mt-2">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {sendMessage.isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-3">
                  <div className="text-3xl">{getAgentAvatar()}</div>
                  <div className="glass-card p-4">
                    <div className="liquid-loader scale-50"></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="glass-nav p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center space-x-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Type your message..."
                  className="glass-input pr-12"
                  disabled={!sessionId || sendMessage.isLoading}
                />
                <Sparkles className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-purple-400 opacity-50" />
              </div>
              
              <button
                onClick={handleSend}
                disabled={!message.trim() || !sessionId || sendMessage.isLoading}
                className="liquid-button flex items-center"
              >
                {sendMessage.isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    <Send className="w-5 h-5 mr-2" />
                    Send
                  </>
                )}
              </button>
            </div>
            
            {/* Suggestions */}
            {agent?.suggested_prompts && messages.length === 1 && (
              <div className="mt-3 flex flex-wrap gap-2">
                <span className="text-xs text-gray-400">Try:</span>
                {agent.suggested_prompts.slice(0, 3).map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => setMessage(prompt)}
                    className="glass-badge hover:bg-purple-500/20 transition-colors cursor-pointer"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatGlass
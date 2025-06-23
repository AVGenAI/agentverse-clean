import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { ThemeProvider } from './contexts/ThemeContext'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Agents from './pages/Agents'
import AgentDetails from './pages/AgentDetails'
import AgentCreate from './pages/AgentCreate'
import Chat from './pages/Chat'
import TeamBuilder from './pages/TeamBuilder'
import Marketplace from './pages/Marketplace'
import MCPIntegration from './pages/MCPIntegration'
import LLMProviders from './pages/LLMProviders'
import PipelineBuilder from './pages/PipelineBuilder'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <ThemeProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/agents" element={<Agents />} />
            <Route path="/agents/create" element={<AgentCreate />} />
            <Route path="/agents/:agentId" element={<AgentDetails />} />
            <Route path="/chat/:agentId?" element={<Chat />} />
            <Route path="/team-builder" element={<TeamBuilder />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/mcp-integration" element={<MCPIntegration />} />
            <Route path="/llm-providers" element={<LLMProviders />} />
            <Route path="/pipeline-builder" element={<PipelineBuilder />} />
          </Routes>
        </Layout>
        </ThemeProvider>
        <Toaster 
          position="top-right"
          toastOptions={{
            duration: 3000,
            style: {
              background: '#1a1825',
              color: '#fff',
              border: '1px solid rgba(168, 85, 247, 0.3)',
              borderRadius: '8px',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  )
}

export default App
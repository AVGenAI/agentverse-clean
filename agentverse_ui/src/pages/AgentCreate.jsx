import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Save, Cpu, Database, Bot } from 'lucide-react';

const AgentCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: '',
    domain: 'general',
    type: 'specialist',
    instructions: '',
    model: 'gpt-4o-mini',
    temperature: 0.7,
    max_tokens: 2000,
    tools: [],
    mcp_server: ''
  });

  const domains = ['general', 'sre', 'devops', 'data', 'engineering', 'security', 'healthcare', 'finance'];
  const models = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'claude-3', 'llama3'];
  const mcpServers = ['servicenow', 'postgresql', 'mongodb', 'prometheus', 'jenkins'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('http://localhost:8000/agents', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...formData,
          id: `${formData.domain}_${formData.name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`,
          status: 'active',
          version: '1.0.0',
          model_preferences: {
            primary: formData.model,
            temperature: parseFloat(formData.temperature),
            max_tokens: parseInt(formData.max_tokens)
          },
          capabilities: {
            primary_expertise: [],
            tools_mastery: {}
          }
        })
      });

      if (response.ok) {
        navigate('/agents');
      }
    } catch (error) {
      console.error('Error creating agent:', error);
    }
  };

  return (
    <div className="glass-container">
      <div className="glass-header">
        <button
          onClick={() => navigate('/agents')}
          className="glass-button-secondary"
        >
          <ChevronLeft className="w-4 h-4" />
          Back
        </button>
        <h1 className="glass-title">Create New Agent</h1>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Basic Information */}
          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Bot className="w-5 h-5 text-cyan-400" />
              Basic Information
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Agent Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="glass-input w-full"
                  placeholder="e.g., Python Expert"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Domain
                </label>
                <select
                  value={formData.domain}
                  onChange={(e) => setFormData({ ...formData, domain: e.target.value })}
                  className="glass-input w-full"
                >
                  {domains.map(domain => (
                    <option key={domain} value={domain}>
                      {domain.charAt(0).toUpperCase() + domain.slice(1)}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Type
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="glass-input w-full"
                >
                  <option value="specialist">Specialist</option>
                  <option value="coordinator">Coordinator</option>
                  <option value="analyzer">Analyzer</option>
                  <option value="executor">Executor</option>
                </select>
              </div>
            </div>
          </div>

          {/* Model Configuration */}
          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              Model Configuration
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  LLM Model
                </label>
                <select
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="glass-input w-full"
                >
                  {models.map(model => (
                    <option key={model} value={model}>{model}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Temperature ({formData.temperature})
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={formData.temperature}
                  onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">
                  Max Tokens
                </label>
                <input
                  type="number"
                  value={formData.max_tokens}
                  onChange={(e) => setFormData({ ...formData, max_tokens: e.target.value })}
                  className="glass-input w-full"
                  min="100"
                  max="4000"
                />
              </div>
            </div>
          </div>

          {/* Instructions */}
          <div className="glass-card md:col-span-2">
            <h3 className="text-lg font-semibold mb-4">System Instructions</h3>
            <textarea
              value={formData.instructions}
              onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
              className="glass-input w-full h-32"
              placeholder="Describe the agent's behavior, expertise, and how it should respond..."
              required
            />
          </div>

          {/* MCP Integration */}
          <div className="glass-card md:col-span-2">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" />
              MCP Server Connection (Optional)
            </h3>
            <select
              value={formData.mcp_server}
              onChange={(e) => setFormData({ ...formData, mcp_server: e.target.value })}
              className="glass-input w-full"
            >
              <option value="">None</option>
              {mcpServers.map(server => (
                <option key={server} value={server}>
                  {server.charAt(0).toUpperCase() + server.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/agents')}
            className="glass-button-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="glass-button-primary flex items-center gap-2"
          >
            <Save className="w-4 h-4" />
            Create Agent
          </button>
        </div>
      </form>
    </div>
  );
};

export default AgentCreate;
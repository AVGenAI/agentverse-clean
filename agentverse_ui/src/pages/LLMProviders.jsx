import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, Sparkles, Brain, Cpu, Globe, Zap, Server, Cloud } from 'lucide-react'
import '../styles/glass.css'

const LLMProviders = () => {
  const navigate = useNavigate()
  const [selectedProvider, setSelectedProvider] = useState(null)

  // Theme is now managed by LayoutGlass component

  const providers = [
    {
      id: 'openai',
      name: 'OpenAI',
      icon: '🤖',
      models: ['GPT-4o', 'GPT-4', 'GPT-3.5-turbo'],
      color: 'from-green-600 to-green-700',
      bgColor: 'bg-green-600/20',
      description: 'Industry-leading language models',
      features: ['Function calling', 'Vision', 'JSON mode']
    },
    {
      id: 'anthropic',
      name: 'Anthropic',
      icon: '🔮',
      models: ['Claude 3 Opus', 'Claude 3 Sonnet', 'Claude 3 Haiku'],
      color: 'from-orange-600 to-orange-700',
      bgColor: 'bg-orange-600/20',
      description: 'Constitutional AI with large context',
      features: ['200K context', 'Safe outputs', 'Artifacts']
    },
    {
      id: 'huggingface',
      name: 'HuggingFace',
      icon: '🤗',
      models: ['Llama 3', 'Mistral', 'Falcon', 'Custom Models'],
      color: 'from-yellow-600 to-yellow-700',
      bgColor: 'bg-yellow-600/20',
      description: 'Open-source model hub',
      features: ['1000+ models', 'Fine-tuning', 'Inference API']
    },
    {
      id: 'google',
      name: 'Google',
      icon: '🌈',
      models: ['Gemini Pro', 'Gemini Ultra', 'PaLM 2'],
      color: 'from-blue-600 to-blue-700',
      bgColor: 'bg-blue-600/20',
      description: 'Multimodal AI models',
      features: ['Multimodal', 'Code generation', 'Reasoning']
    },
    {
      id: 'meta',
      name: 'Meta LLAMA',
      icon: '🦙',
      models: ['Llama 3 70B', 'Llama 3 8B', 'Code Llama'],
      color: 'from-purple-600 to-purple-700',
      bgColor: 'bg-purple-600/20',
      description: 'Open-source powerhouse',
      features: ['Open weights', 'Commercial use', 'Fine-tunable']
    },
    {
      id: 'aws',
      name: 'AWS Bedrock',
      icon: '☁️',
      models: ['Claude', 'Llama', 'Titan', 'Stable Diffusion'],
      color: 'from-orange-500 to-orange-600',
      bgColor: 'bg-orange-600/20',
      description: 'Enterprise-grade AI platform',
      features: ['Multi-provider', 'Serverless', 'Private VPC']
    },
    {
      id: 'mistral',
      name: 'Mistral AI',
      icon: '💨',
      models: ['Mistral Large', 'Mixtral 8x7B', 'Mistral 7B'],
      color: 'from-gray-600 to-gray-700',
      bgColor: 'bg-gray-600/20',
      description: 'European AI excellence',
      features: ['Efficient', 'Multilingual', 'Apache 2.0']
    }
  ]

  const handleProviderSelect = (provider) => {
    setSelectedProvider(provider)
    // In a real app, this would save the configuration
    setTimeout(() => {
      navigate('/agents')
    }, 1500)
  }

  return (
    <div className="p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold mb-4 gradient-text">
            Choose an AI model
          </h1>
          <p className="text-xl text-gray-300">
            Access the latest models through the Agent Verse system
          </p>
        </div>

        {/* Provider Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-12">
          {providers.map((provider) => (
            <div
              key={provider.id}
              onClick={() => handleProviderSelect(provider)}
              className="group cursor-pointer"
            >
              <div className={`av-card transition-all hover:scale-105 hover:border-purple-500/50 relative ${
                selectedProvider?.id === provider.id ? 'border-purple-500 bg-purple-900/20' : ''
              }`}>
                {/* Icon */}
                <div className="text-center mb-6">
                  <div className={`w-20 h-20 rounded-2xl ${provider.bgColor} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform`}>
                    <div className="text-4xl">{provider.icon}</div>
                  </div>
                  <h3 className="text-xl font-bold text-white">{provider.name}</h3>
                </div>

                {/* Description */}
                <p className="text-sm text-gray-300 mb-4 leading-relaxed">
                  {provider.description}
                </p>

                {/* Features */}
                <div className="space-y-2 mb-6">
                  {provider.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center text-sm text-gray-300">
                      <Check className="w-4 h-4 mr-2 text-purple-400" />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>

                {/* Models */}
                <div className="pt-4 border-t border-gray-700">
                  <p className="text-xs text-gray-400 mb-3 font-medium">Available models:</p>
                  <div className="flex flex-wrap gap-2">
                    {provider.models.slice(0, 3).map((model, idx) => (
                      <span key={idx} className="text-xs px-3 py-1 rounded-lg bg-gray-800 text-gray-300 border border-gray-700">
                        {model}
                      </span>
                    ))}
                    {provider.models.length > 3 && (
                      <span className="text-xs px-3 py-1 text-gray-500">
                        +{provider.models.length - 3}
                      </span>
                    )}
                  </div>
                </div>

                {selectedProvider?.id === provider.id && (
                  <div className="absolute top-4 right-4">
                    <div className="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center">
                      <Check className="w-5 h-5 text-white" />
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Actions */}
        <div className="text-center">
          <div className="av-card inline-block px-12 py-8">
            <h3 className="text-2xl font-bold text-white mb-4">
              Ready to get started?
            </h3>
            <p className="text-gray-300 mb-6">
              {selectedProvider 
                ? `You've selected ${selectedProvider.name}. Let's configure your agent!`
                : 'Select a provider above to begin building your AI agent.'}
            </p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => navigate('/agents')}
                className="av-button-primary"
                disabled={!selectedProvider}
              >
                Get started
              </button>
              <button
                onClick={() => navigate('/settings')}
                className="px-6 py-3 text-gray-300 hover:text-white transition-colors font-medium"
              >
                Configure API keys →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LLMProviders
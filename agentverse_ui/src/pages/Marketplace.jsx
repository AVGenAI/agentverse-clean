import React from 'react'
import { Star, Download, TrendingUp, Shield, Zap, Brain } from 'lucide-react'

const templates = [
  {
    id: 1,
    name: 'Customer Support Team',
    description: 'Complete customer service solution with L1, L2, and L3 support agents',
    category: 'Support',
    agents: 5,
    downloads: 1234,
    rating: 4.8,
    icon: Shield,
    color: 'bg-blue-500'
  },
  {
    id: 2,
    name: 'DevOps Pipeline',
    description: 'CI/CD, monitoring, and infrastructure automation agents',
    category: 'Engineering',
    agents: 8,
    downloads: 892,
    rating: 4.9,
    icon: Zap,
    color: 'bg-green-500'
  },
  {
    id: 3,
    name: 'Data Analytics Suite',
    description: 'ETL, analysis, and visualization agents for data teams',
    category: 'Analytics',
    agents: 6,
    downloads: 756,
    rating: 4.7,
    icon: TrendingUp,
    color: 'bg-purple-500'
  },
  {
    id: 4,
    name: 'E-commerce Starter',
    description: 'Frontend, backend, payment, and inventory management agents',
    category: 'Business',
    agents: 7,
    downloads: 1567,
    rating: 4.9,
    icon: Brain,
    color: 'bg-yellow-500'
  }
]

export default function Marketplace() {
  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Agent Marketplace
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Deploy pre-built agent teams and templates
        </p>
      </div>

      {/* Coming Soon Banner */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-8 text-white mb-8">
        <h2 className="text-2xl font-bold mb-2">Marketplace Coming Soon!</h2>
        <p className="text-purple-100 mb-4">
          We're building a marketplace where you can share and discover agent templates
        </p>
        <div className="flex gap-4">
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <p className="text-sm font-medium">100+ Templates</p>
            <p className="text-xs text-purple-100">Ready to deploy</p>
          </div>
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <p className="text-sm font-medium">Community Built</p>
            <p className="text-xs text-purple-100">Share your creations</p>
          </div>
          <div className="bg-white/20 rounded-lg px-4 py-2">
            <p className="text-sm font-medium">One-Click Deploy</p>
            <p className="text-xs text-purple-100">Instant setup</p>
          </div>
        </div>
      </div>

      {/* Preview Templates */}
      <h2 className="text-xl font-semibold mb-4">Preview Templates</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {templates.map((template) => (
          <div
            key={template.id}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`${template.color} p-3 rounded-lg`}>
                  <template.icon className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{template.name}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {template.category}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1 text-yellow-500">
                <Star className="h-4 w-4 fill-current" />
                <span className="text-sm font-medium">{template.rating}</span>
              </div>
            </div>

            <p className="text-gray-600 dark:text-gray-400 mb-4">
              {template.description}
            </p>

            <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-4">
              <span>{template.agents} agents</span>
              <span className="flex items-center gap-1">
                <Download className="h-4 w-4" />
                {template.downloads} downloads
              </span>
            </div>

            <button
              disabled
              className="w-full bg-gray-100 dark:bg-gray-700 text-gray-400 dark:text-gray-500 px-4 py-2 rounded-lg font-medium cursor-not-allowed"
            >
              Coming Soon
            </button>
          </div>
        ))}
      </div>

      {/* Features */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="text-center">
          <div className="bg-purple-100 dark:bg-purple-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="font-semibold mb-2">Verified Templates</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            All templates are tested and verified by our team
          </p>
        </div>
        <div className="text-center">
          <div className="bg-purple-100 dark:bg-purple-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Zap className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="font-semibold mb-2">One-Click Deploy</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Deploy entire agent teams instantly
          </p>
        </div>
        <div className="text-center">
          <div className="bg-purple-100 dark:bg-purple-900/30 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Brain className="h-8 w-8 text-purple-600" />
          </div>
          <h3 className="font-semibold mb-2">Customizable</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Modify templates to fit your specific needs
          </p>
        </div>
      </div>
    </div>
  )
}
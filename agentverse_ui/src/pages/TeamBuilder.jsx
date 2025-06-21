import React, { useState } from 'react'
import { Users, Zap, Briefcase, ShoppingCart, Smartphone, Database } from 'lucide-react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const projectTypes = [
  {
    id: 'ecommerce',
    name: 'E-commerce Platform',
    icon: ShoppingCart,
    description: 'Build a full-featured online store',
    color: 'bg-blue-500'
  },
  {
    id: 'mobile',
    name: 'Mobile App',
    icon: Smartphone,
    description: 'Create a cross-platform mobile application',
    color: 'bg-green-500'
  },
  {
    id: 'data',
    name: 'Data Platform',
    icon: Database,
    description: 'Build a data analytics and processing system',
    color: 'bg-purple-500'
  }
]

export default function TeamBuilder() {
  const [selectedProject, setSelectedProject] = useState('')
  const [customRequirements, setCustomRequirements] = useState('')
  const [teamSize, setTeamSize] = useState(5)
  const [team, setTeam] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const buildTeam = async () => {
    if (!selectedProject) return

    setIsLoading(true)
    try {
      const requirements = customRequirements
        .split(',')
        .map(req => req.trim())
        .filter(req => req.length > 0)

      const response = await axios.post(`${API_URL}/team/assemble`, {
        project_type: selectedProject,
        requirements: requirements,
        team_size: teamSize
      })

      setTeam(response.data)
    } catch (error) {
      console.error('Error building team:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Team Builder
        </h1>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Automatically assemble the perfect team for your project
        </p>
      </div>

      {/* Project Selection */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <h2 className="text-xl font-semibold mb-4">1. Select Project Type</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {projectTypes.map((project) => (
            <button
              key={project.id}
              onClick={() => setSelectedProject(project.id)}
              className={`p-6 rounded-lg border-2 transition-all ${
                selectedProject === project.id
                  ? 'border-purple-600 bg-purple-50 dark:bg-purple-900/20'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className={`${project.color} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
                <project.icon className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-lg mb-1">{project.name}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {project.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Requirements */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <h2 className="text-xl font-semibold mb-4">2. Custom Requirements (Optional)</h2>
        <input
          type="text"
          placeholder="e.g., React Native, GraphQL, Blockchain (comma-separated)"
          className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          value={customRequirements}
          onChange={(e) => setCustomRequirements(e.target.value)}
        />
        
        <div className="mt-4">
          <label className="block text-sm font-medium mb-2">Team Size</label>
          <input
            type="range"
            min="3"
            max="10"
            value={teamSize}
            onChange={(e) => setTeamSize(parseInt(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
            <span>3</span>
            <span className="font-medium text-purple-600">{teamSize} agents</span>
            <span>10</span>
          </div>
        </div>
      </div>

      {/* Build Team Button */}
      <div className="text-center mb-8">
        <button
          onClick={buildTeam}
          disabled={!selectedProject || isLoading}
          className="px-8 py-3 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              Building Team...
            </>
          ) : (
            <>
              <Zap className="h-5 w-5" />
              Build Dream Team
            </>
          )}
        </button>
      </div>

      {/* Team Results */}
      {team && (
        <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <Users className="h-5 w-5" />
            Your Dream Team for {projectTypes.find(p => p.id === team.project_type)?.name}
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {team.team.map((member, idx) => (
              <div
                key={idx}
                className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
              >
                <div className="flex items-start gap-4">
                  <div className="text-3xl">{member.agent.avatar || '🤖'}</div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-lg">{member.role}</h3>
                    <p className="text-purple-600 font-medium">
                      {member.agent.display_name}
                    </p>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {member.agent.canonical_name}
                    </p>
                    
                    <div className="flex flex-wrap gap-1 mt-2">
                      {member.agent.skills?.slice(0, 4).map((skill, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                    
                    <div className="mt-2 text-xs text-gray-500">
                      Match Score: {member.agent.match_score}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Actions */}
          <div className="mt-6 flex justify-center gap-4">
            <button className="px-6 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors">
              Start Team Chat
            </button>
            <button className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              Save Team
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
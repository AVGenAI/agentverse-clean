import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, Bot, MessageSquare, Zap, Settings, Sparkles } from 'lucide-react'
import ThemeSwitcherEnhanced from './ThemeSwitcherEnhanced'
import '../styles/glass.css'

const NavigationGlass = () => {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard', icon: Home },
    { path: '/agents', label: 'Agents', icon: Bot },
    { path: '/pipeline-builder', label: 'Pipeline', icon: Zap },
    { path: '/llm-providers', label: 'Models', icon: Sparkles },
    { path: '/mcp-integration', label: 'Tools', icon: Settings }
  ]

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/'
    return location.pathname.startsWith(path)
  }

  return (
    <nav className="glass-nav fixed top-0 left-0 right-0 z-50">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left Section: Theme Switcher and Logo */}
          <div className="flex items-center space-x-6">
            <ThemeSwitcherEnhanced />
            
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="relative">
                <Sparkles className="w-8 h-8 text-purple-400 group-hover:text-purple-300 transition-colors" />
                <div className="absolute inset-0 blur-xl bg-purple-400 opacity-50 group-hover:opacity-70 transition-opacity"></div>
              </div>
              <span className="text-2xl font-bold gradient-text">Agent Verse</span>
            </Link>
          </div>

          {/* Center: Navigation Items */}
          <div className="flex items-center space-x-2">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-2 px-4 py-2 rounded-full transition-all ${
                  isActive(item.path)
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg'
                    : 'glass-card hover:bg-white/10 text-gray-300 hover:text-white'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </Link>
            ))}
          </div>

          {/* Right: Action Button */}
          <Link to="/agents/create" className="liquid-button flex items-center">
            <Sparkles className="w-5 h-5 mr-2" />
            Create Agent
          </Link>
        </div>
      </div>
    </nav>
  )
}

export default NavigationGlass
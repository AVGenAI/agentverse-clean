import React, { useState } from 'react'
import { Palette, Check, Globe, FileText, Lock, Unlock } from 'lucide-react'
import { useTheme } from '../contexts/ThemeContext'
import { useLocation } from 'react-router-dom'
import '../styles/glass.css'

const themes = [
  { id: 'agentverse', name: 'AgentVerse', preview: ['#7c3aed', '#a855f7'], badge: 'Pro' },
  { id: 'default', name: 'Minimalist', preview: ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.05)'] },
  { id: 'corporate', name: 'Corporate', preview: ['#3b82f6', '#2563eb'], badge: 'Clean' },
  { id: 'purple-dream', name: 'Purple Dream', preview: ['#667eea', '#764ba2'] },
  { id: 'arctic', name: 'Arctic Frost', preview: ['#2563eb', '#1d4ed8'] },
  { id: 'midnight', name: 'Midnight', preview: ['rgba(255,255,255,0.08)', 'rgba(255,255,255,0.02)'] },
  { id: 'sunset', name: 'Sunset Blush', preview: ['rgba(255,94,87,0.3)', 'rgba(255,154,0,0.2)'] },
  { id: 'ocean', name: 'Ocean Depths', preview: ['rgba(0,119,190,0.25)', 'rgba(0,180,216,0.15)'] },
  { id: 'neon-pulse', name: 'Neon Pulse', preview: ['#ff00ff', '#00ffff'], badge: 'Animated' },
  { id: 'aurora', name: 'Aurora', preview: ['rgba(0,255,170,0.3)', 'rgba(170,0,255,0.3)'], badge: 'Animated' }
]

const pageNames = {
  '/': 'Dashboard',
  '/dashboard': 'Dashboard',
  '/agents': 'Agents',
  '/chat': 'Chat',
  '/mcp': 'MCP Integration',
  '/pipeline': 'Pipeline Builder',
  '/marketplace': 'Marketplace',
  '/team': 'Team Builder',
  '/llm-providers': 'LLM Providers'
}

const ThemeSwitcherEnhanced = () => {
  const location = useLocation()
  const { 
    globalTheme, 
    currentTheme, 
    setTheme, 
    isPageOverride, 
    togglePageOverride,
    getPageDefault 
  } = useTheme()
  
  const [isOpen, setIsOpen] = useState(false)
  const [mode, setMode] = useState('global') // 'global' or 'page'
  
  const currentPage = pageNames[location.pathname] || 'This Page'
  const pageDefault = getPageDefault()

  const handleThemeSelect = (themeId) => {
    setTheme(themeId, mode === 'page')
    setIsOpen(false)
  }

  const handleModeToggle = () => {
    setMode(mode === 'global' ? 'page' : 'global')
  }

  const handleOverrideToggle = () => {
    togglePageOverride()
    if (!isPageOverride && mode === 'global') {
      setMode('page')
    }
  }

  return (
    <div className="relative">
      {/* Theme Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="glass-card p-3 hover:scale-110 transition-all flex items-center gap-2"
      >
        <Palette className="w-5 h-5" />
        <span className="text-sm font-medium hidden md:inline">
          {isPageOverride ? (
            <span className="flex items-center gap-1">
              <FileText className="w-4 h-4" />
              Page Theme
            </span>
          ) : (
            <span className="flex items-center gap-1">
              <Globe className="w-4 h-4" />
              Theme
            </span>
          )}
        </span>
      </button>

      {/* Theme Dropdown */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute left-0 mt-2 w-80 glass-card p-4 z-50">
            {/* Mode Toggle */}
            <div className="flex items-center justify-between mb-4 pb-4 border-b border-gray-700">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-gray-300">Theme Settings</h3>
                {isPageOverride && (
                  <span className="glass-badge text-xs">
                    Page Override Active
                  </span>
                )}
              </div>
              <button
                onClick={handleOverrideToggle}
                className={`p-1.5 rounded-lg transition-all ${
                  isPageOverride 
                    ? 'bg-purple-500/20 text-purple-400' 
                    : 'glass-card hover:bg-white/10'
                }`}
                title={isPageOverride ? 'Using page theme' : 'Using global theme'}
              >
                {isPageOverride ? <Lock className="w-4 h-4" /> : <Unlock className="w-4 h-4" />}
              </button>
            </div>

            {/* Scope Selector */}
            <div className="flex gap-2 mb-4">
              <button
                onClick={() => setMode('global')}
                className={`flex-1 p-2 rounded-lg text-sm font-medium transition-all ${
                  mode === 'global' 
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' 
                    : 'glass-card hover:bg-white/10'
                }`}
              >
                <Globe className="w-4 h-4 mx-auto mb-1" />
                Global Theme
              </button>
              <button
                onClick={() => setMode('page')}
                className={`flex-1 p-2 rounded-lg text-sm font-medium transition-all ${
                  mode === 'page' 
                    ? 'bg-purple-500/20 text-purple-400 border border-purple-500/30' 
                    : 'glass-card hover:bg-white/10'
                }`}
              >
                <FileText className="w-4 h-4 mx-auto mb-1" />
                {currentPage} Only
              </button>
            </div>

            {/* Current Selection Info */}
            <div className="glass-card p-3 mb-4 text-xs">
              {mode === 'global' ? (
                <p>Selecting a theme will apply it across all pages</p>
              ) : (
                <p>Selecting a theme will only apply it to {currentPage}</p>
              )}
            </div>

            {/* Theme List */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {themes.map((theme) => {
                const isSelected = mode === 'global' 
                  ? globalTheme === theme.id 
                  : currentTheme === theme.id
                
                return (
                  <button
                    key={theme.id}
                    onClick={() => handleThemeSelect(theme.id)}
                    className={`theme-switcher-item glass-card p-3 hover:scale-[1.02] transition-all ${
                      isSelected ? 'ring-2 ring-purple-500/50' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3 flex-1">
                      <div
                        className="w-8 h-8 rounded-full relative overflow-hidden flex-shrink-0"
                        style={{
                          background: `linear-gradient(135deg, ${theme.preview[0]}, ${theme.preview[1]})`
                        }}
                      >
                        {theme.id === 'neon-pulse' && (
                          <div className="absolute inset-0 animate-pulse bg-white opacity-30"></div>
                        )}
                      </div>
                      <div className="theme-name-container">
                        <span className="theme-name text-sm font-medium">{theme.name}</span>
                        {theme.badge && (
                          <span className="theme-badge text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/70">
                            {theme.badge}
                          </span>
                        )}
                        {theme.id === pageDefault && mode === 'page' && (
                          <span className="text-xs text-gray-500 ml-2">
                            (default)
                          </span>
                        )}
                      </div>
                    </div>
                    {isSelected && (
                      <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    )}
                  </button>
                )
              })}
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-700">
              <p className="text-xs text-gray-400">
                {isPageOverride 
                  ? `${currentPage} is using a custom theme. Toggle the lock to use global theme.`
                  : 'All pages are using the global theme setting.'
                }
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ThemeSwitcherEnhanced
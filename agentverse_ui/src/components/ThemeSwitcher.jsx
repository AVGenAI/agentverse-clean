import React, { useState, useEffect } from 'react'
import { Palette, Check } from 'lucide-react'
import '../styles/glass.css'

const themes = [
  { id: 'vectorshift', name: 'VectorShift', preview: ['#7c3aed', '#a855f7'], badge: 'Pro' },
  { id: 'default', name: 'Minimalist', preview: ['rgba(255,255,255,0.1)', 'rgba(255,255,255,0.05)'] },
  { id: 'corporate', name: 'Corporate', preview: ['rgba(59,130,246,0.08)', 'rgba(59,130,246,0.04)'], badge: 'Clean' },
  { id: 'purple-dream', name: 'Purple Dream', preview: ['#667eea', '#764ba2'] },
  { id: 'arctic', name: 'Arctic Frost', preview: ['rgba(255,255,255,0.1)', 'rgba(220,230,255,0.05)'] },
  { id: 'midnight', name: 'Midnight', preview: ['rgba(255,255,255,0.08)', 'rgba(255,255,255,0.02)'] },
  { id: 'sunset', name: 'Sunset Blush', preview: ['rgba(255,94,87,0.3)', 'rgba(255,154,0,0.2)'] },
  { id: 'ocean', name: 'Ocean Depths', preview: ['rgba(0,119,190,0.25)', 'rgba(0,180,216,0.15)'] },
  { id: 'neon-pulse', name: 'Neon Pulse', preview: ['#ff00ff', '#00ffff'], badge: 'Animated' },
  { id: 'aurora', name: 'Aurora', preview: ['rgba(0,255,170,0.3)', 'rgba(170,0,255,0.3)'], badge: 'Animated' }
]

const ThemeSwitcher = () => {
  const [currentTheme, setCurrentTheme] = useState('default')
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    // Load saved theme
    const savedTheme = localStorage.getItem('agentverse-theme') || 'default'
    setCurrentTheme(savedTheme)
    applyTheme(savedTheme)
  }, [])

  const applyTheme = (themeId) => {
    const root = document.documentElement
    if (themeId === 'default') {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', themeId)
    }
    
    // Update background classes
    const elements = document.querySelectorAll('.bg-gradient-to-br')
    elements.forEach(el => {
      el.className = el.className.replace(/from-\S+\s+via-\S+\s+to-\S+/, '')
      if (themeId === 'default' || themeId === 'midnight') {
        el.classList.add('from-gray-900', 'via-purple-900', 'to-gray-900')
      } else if (themeId === 'arctic' || themeId === 'corporate') {
        el.classList.add('from-gray-100', 'via-blue-50', 'to-gray-100')
      } else if (themeId === 'sunset') {
        el.classList.add('from-gray-900', 'via-orange-900', 'to-gray-900')
      } else if (themeId === 'ocean') {
        el.classList.add('from-blue-900', 'via-teal-900', 'to-blue-900')
      } else if (themeId === 'purple-dream') {
        el.classList.add('from-purple-900', 'via-pink-900', 'to-purple-900')
      } else if (themeId === 'neon-pulse') {
        el.classList.add('from-black', 'via-gray-900', 'to-black')
      } else if (themeId === 'aurora') {
        el.classList.add('from-blue-900', 'via-purple-900', 'to-blue-900')
      } else if (themeId === 'vectorshift') {
        el.classList.add('from-black', 'via-gray-900', 'to-black')
      }
    })
  }

  const selectTheme = (themeId) => {
    setCurrentTheme(themeId)
    applyTheme(themeId)
    localStorage.setItem('agentverse-theme', themeId)
    setIsOpen(false)
  }

  return (
    <div className="relative">
      {/* Theme Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="glass-card p-3 hover:scale-110 transition-all flex items-center gap-2"
      >
        <Palette className="w-5 h-5" />
        <span className="text-sm font-medium hidden md:inline">Theme</span>
      </button>

      {/* Theme Dropdown */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute left-0 mt-2 w-64 glass-card p-4 z-50">
            <h3 className="text-sm font-semibold mb-3 text-gray-300">Choose Theme</h3>
            <div className="space-y-2">
              {themes.map((theme) => (
                <button
                  key={theme.id}
                  onClick={() => selectTheme(theme.id)}
                  className={`w-full glass-card p-3 hover:scale-[1.02] transition-all flex items-center justify-between ${
                    currentTheme === theme.id ? 'ring-2 ring-white/30' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className="w-8 h-8 rounded-full relative overflow-hidden"
                      style={{
                        background: `linear-gradient(135deg, ${theme.preview[0]}, ${theme.preview[1]})`
                      }}
                    >
                      {theme.id === 'neon-pulse' && (
                        <div className="absolute inset-0 animate-pulse bg-white opacity-30"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <span className="text-sm font-medium">{theme.name}</span>
                      {theme.badge && (
                        <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/70">
                          {theme.badge}
                        </span>
                      )}
                    </div>
                  </div>
                  {currentTheme === theme.id && (
                    <Check className="w-4 h-4 text-green-400" />
                  )}
                </button>
              ))}
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-700">
              <p className="text-xs text-gray-400">
                Themes change colors instantly. Your preference is saved automatically.
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ThemeSwitcher
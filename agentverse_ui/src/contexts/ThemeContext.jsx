import React, { createContext, useContext, useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

const ThemeContext = createContext()

// Default themes for specific pages
const PAGE_DEFAULTS = {
  '/': 'agentverse',
  '/dashboard': 'agentverse',
  '/pipeline': 'agentverse',
  '/llm-providers': 'agentverse',
  '/agents': 'default',
  '/chat': 'default',
  '/mcp': 'corporate',
  '/marketplace': 'purple-dream',
  '/team': 'ocean'
}

export const ThemeProvider = ({ children }) => {
  const location = useLocation()
  const [globalTheme, setGlobalTheme] = useState('default')
  const [pageOverrides, setPageOverrides] = useState({})
  const [usePageOverride, setUsePageOverride] = useState({})

  // Load saved preferences on mount
  useEffect(() => {
    const savedGlobal = localStorage.getItem('agentverse-theme') || 'default'
    const savedOverrides = JSON.parse(localStorage.getItem('agentverse-theme-overrides') || '{}')
    const savedUseOverrides = JSON.parse(localStorage.getItem('agentverse-theme-use-overrides') || '{}')
    
    setGlobalTheme(savedGlobal)
    setPageOverrides(savedOverrides)
    setUsePageOverride(savedUseOverrides)
  }, [])

  // Apply theme based on current page
  useEffect(() => {
    const currentPath = location.pathname
    let themeToApply = globalTheme

    // Check if this page has override enabled
    if (usePageOverride[currentPath]) {
      // Use page-specific theme if override is enabled
      themeToApply = pageOverrides[currentPath] || PAGE_DEFAULTS[currentPath] || globalTheme
    }

    // Apply theme to document
    const root = document.documentElement
    if (themeToApply === 'default') {
      root.removeAttribute('data-theme')
    } else {
      root.setAttribute('data-theme', themeToApply)
    }

    // Update background classes
    updateBackgroundClasses(themeToApply)
  }, [location.pathname, globalTheme, pageOverrides, usePageOverride])

  const updateBackgroundClasses = (themeId) => {
    const elements = document.querySelectorAll('.bg-gradient-to-br')
    elements.forEach(el => {
      el.className = el.className.replace(/from-\S+\s+via-\S+\s+to-\S+/, '')
      
      const themeClasses = {
        'default': 'from-gray-900 via-purple-900 to-gray-900',
        'midnight': 'from-gray-900 via-purple-900 to-gray-900',
        'arctic': 'from-gray-100 via-blue-50 to-gray-100',
        'corporate': 'from-gray-100 via-blue-50 to-gray-100',
        'sunset': 'from-gray-900 via-orange-900 to-gray-900',
        'ocean': 'from-blue-900 via-teal-900 to-blue-900',
        'purple-dream': 'from-purple-900 via-pink-900 to-purple-900',
        'neon-pulse': 'from-black via-gray-900 to-black',
        'aurora': 'from-blue-900 via-purple-900 to-blue-900',
        'agentverse': 'from-black via-gray-900 to-black'
      }
      
      el.classList.add(...(themeClasses[themeId] || themeClasses['default']).split(' '))
    })
  }

  const setTheme = (theme, isPageSpecific = false) => {
    if (isPageSpecific) {
      const currentPath = location.pathname
      const newOverrides = { ...pageOverrides, [currentPath]: theme }
      setPageOverrides(newOverrides)
      localStorage.setItem('agentverse-theme-overrides', JSON.stringify(newOverrides))
    } else {
      setGlobalTheme(theme)
      localStorage.setItem('agentverse-theme', theme)
    }
  }

  const togglePageOverride = (path = location.pathname) => {
    const newUseOverrides = { ...usePageOverride, [path]: !usePageOverride[path] }
    setUsePageOverride(newUseOverrides)
    localStorage.setItem('agentverse-theme-use-overrides', JSON.stringify(newUseOverrides))
  }

  const getCurrentTheme = () => {
    const currentPath = location.pathname
    if (usePageOverride[currentPath]) {
      return pageOverrides[currentPath] || PAGE_DEFAULTS[currentPath] || globalTheme
    }
    return globalTheme
  }

  const getPageDefault = (path = location.pathname) => {
    return PAGE_DEFAULTS[path] || 'default'
  }

  const value = {
    globalTheme,
    pageOverrides,
    usePageOverride,
    currentTheme: getCurrentTheme(),
    setTheme,
    togglePageOverride,
    getPageDefault,
    isPageOverride: usePageOverride[location.pathname] || false
  }

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider')
  }
  return context
}
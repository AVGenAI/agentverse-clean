import React, { useEffect } from 'react'
import NavigationGlass from './NavigationGlass'
import '../styles/glass.css'

const LayoutGlass = ({ children }) => {
  useEffect(() => {
    // Theme is now handled by ThemeContext
    
    // Animated background orbs
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

  return (
    <div className="min-h-screen bg-gradient text-white relative overflow-hidden">
      {/* Animated Background Orbs */}
      <div className="orb-container">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>
      
      <NavigationGlass />
      {/* Main content with padding for fixed navigation */}
      <main className="pt-20 relative z-10">
        {children}
      </main>
    </div>
  )
}

export default LayoutGlass
import React from 'react'
import NavigationGlass from './NavigationGlass'
import '../styles/glass.css'

const LayoutGlass = ({ children }) => {
  return (
    <div className="min-h-screen bg-gradient">
      <NavigationGlass />
      {/* Main content with padding for fixed navigation */}
      <main className="pt-20">
        {children}
      </main>
    </div>
  )
}

export default LayoutGlass
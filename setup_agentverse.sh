#!/bin/bash

echo "🌌 Setting up AgentVerse..."
echo "=========================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your OpenAI API key"
    echo "    Edit: .env"
    echo "    Add: OPENAI_API_KEY=your-key-here"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start using AgentVerse:"
echo "   1. Activate the virtual environment: source venv/bin/activate"
echo "   2. Make sure your OpenAI API key is in .env file"
echo "   3. Run: python interactive_agentverse_demo.py"
echo ""
echo "📖 Quick commands:"
echo "   - Interactive demo: python interactive_agentverse_demo.py"
echo "   - Quick test: python quick_test_agentverse.py"
echo "   - Explore agents: python agentverse_explorer.py --list-domains"
echo "   - Chat with agent: python agentverse_chat.py --agent agentverse.engineering.backend.django"
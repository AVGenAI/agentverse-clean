#!/bin/bash
# Install A\V OS - AgentVerse Operating System

echo "🚀 Installing A\V OS (AgentVerse Operating System)"
echo "================================================"

# Install in development mode
pip install -e .

echo ""
echo "✅ A\V OS installed successfully!"
echo ""
echo "Try these commands:"
echo "  av              - Show A\V OS welcome"
echo "  av list         - List all agents"
echo "  av show <id>    - Show agent details"
echo "  av ps           - Show running agents"
echo "  av chat <id>    - Chat with an agent"
echo "  av status       - System status"
echo ""
echo "Type 'av --help' for all commands"
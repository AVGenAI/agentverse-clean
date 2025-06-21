#!/bin/bash

echo "🚀 AgentVerse OpenAI Setup"
echo "========================="
echo ""

# Check if .env file exists in agentverse_api
if [ ! -f "agentverse_api/.env" ]; then
    echo "Creating .env file from template..."
    cp agentverse_api/.env.example agentverse_api/.env
    echo "✅ Created agentverse_api/.env"
else
    echo "✅ .env file already exists"
fi

# Check if OPENAI_API_KEY is set
if grep -q "your_openai_api_key_here" agentverse_api/.env; then
    echo ""
    echo "⚠️  OPENAI_API_KEY is not configured!"
    echo ""
    echo "To enable OpenAI integration:"
    echo "1. Get your API key from https://platform.openai.com/api-keys"
    echo "2. Edit agentverse_api/.env"
    echo "3. Replace 'your_openai_api_key_here' with your actual API key"
    echo ""
    read -p "Would you like to enter your OpenAI API key now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your OpenAI API key: " api_key
        # Use sed to replace the placeholder
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            sed -i '' "s/your_openai_api_key_here/$api_key/" agentverse_api/.env
        else
            # Linux
            sed -i "s/your_openai_api_key_here/$api_key/" agentverse_api/.env
        fi
        echo "✅ OpenAI API key configured!"
    fi
else
    echo "✅ OpenAI API key is already configured"
fi

echo ""
echo "Setup complete! You can now run:"
echo "./start_agentverse.sh"
echo ""
echo "Note: AgentVerse will work without OpenAI, but agents will provide mock responses."
echo "With OpenAI configured, agents will provide real AI-powered responses!"
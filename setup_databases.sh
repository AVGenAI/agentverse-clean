#!/bin/bash

echo "🚀 Setting up AgentVerse Databases"
echo "=================================="

# Navigate to database directory
cd database

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose down
docker-compose up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to start..."
sleep 10

# Check if databases are running
echo "✅ Checking database status..."
docker-compose ps

echo ""
echo "📊 Database Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Generate and load 10,000 agents:"
echo "   python database/setup_and_load.py --count 10000"
echo ""
echo "2. Generate and load 100,000 agents:"
echo "   python database/setup_and_load.py --count 100000"
echo ""
echo "3. Generate and load 1,000,000 agents:"
echo "   python database/setup_and_load.py --count 1000000"
echo ""
echo "4. Test retrieval performance:"
echo "   python database/setup_and_load.py --test"
echo ""
echo "5. View database logs:"
echo "   cd database && docker-compose logs -f"
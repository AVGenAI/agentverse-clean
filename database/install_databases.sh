#!/bin/bash
# Install databases on macOS

echo "🔧 Installing Databases for AgentVerse"
echo "====================================="

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found. Please install from https://brew.sh"
    exit 1
fi

# PostgreSQL
echo "📦 Installing PostgreSQL..."
if brew list postgresql@14 &>/dev/null; then
    echo "✅ PostgreSQL already installed"
else
    brew install postgresql@14
    echo "✅ PostgreSQL installed"
fi

# Start PostgreSQL
echo "🚀 Starting PostgreSQL..."
brew services start postgresql@14

# Create database
echo "📁 Creating agentverse database..."
createdb agentverse 2>/dev/null || echo "Database might already exist"

# MongoDB
echo "📦 Installing MongoDB..."
if brew list mongodb-community &>/dev/null; then
    echo "✅ MongoDB already installed"
else
    brew tap mongodb/brew
    brew install mongodb-community
    echo "✅ MongoDB installed"
fi

# Start MongoDB
echo "🚀 Starting MongoDB..."
brew services start mongodb-community

# Python dependencies
echo "📦 Installing Python database drivers..."
pip install asyncpg motor python-dotenv

echo ""
echo "✅ Installation complete!"
echo ""
echo "📊 Database Status:"
echo "==================="
echo "PostgreSQL: $(pg_isready)"
echo "MongoDB: $(brew services list | grep mongodb)"
echo ""
echo "🔗 Connection strings:"
echo "PostgreSQL: postgresql://localhost:5432/agentverse"
echo "MongoDB: mongodb://localhost:27017/agentverse"
echo ""
echo "Next steps:"
echo "1. Add to .env file:"
echo "   DATABASE_URL=postgresql://localhost:5432/agentverse"
echo "   MONGODB_URL=mongodb://localhost:27017"
echo "2. Run: python database/migrate_json_to_db.py"
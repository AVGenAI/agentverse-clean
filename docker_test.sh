#!/bin/bash

# AgentVerse Docker Test Script
# This script helps test the dockerized platform repeatedly

echo "🚀 AgentVerse Docker Test Script"
echo "================================"

# Function to run a test cycle
run_test_cycle() {
    echo -e "\n📦 Stopping all containers..."
    docker-compose down -v
    
    echo -e "\n🧹 Cleaning up..."
    docker system prune -f
    
    echo -e "\n🏗️  Building and starting services..."
    docker-compose up --build -d
    
    echo -e "\n⏳ Waiting for services to be healthy..."
    sleep 10
    
    echo -e "\n✅ Services status:"
    docker-compose ps
    
    echo -e "\n📊 Health check:"
    # Check API health
    curl -s http://localhost:8000/health || echo "API not responding"
    
    # Check UI
    curl -s http://localhost:3000 > /dev/null && echo "UI is running" || echo "UI not responding"
    
    echo -e "\n📝 Logs preview:"
    docker-compose logs --tail=10
}

# Main script
if [ "$1" == "loop" ]; then
    # Run in infinite loop with delay
    echo "Running in infinite loop mode. Press Ctrl+C to stop."
    while true; do
        run_test_cycle
        echo -e "\n⏰ Waiting 30 seconds before next cycle..."
        sleep 30
    done
elif [ "$1" == "once" ]; then
    # Run once
    run_test_cycle
else
    echo "Usage: $0 [once|loop]"
    echo "  once - Run a single test cycle"
    echo "  loop - Run in infinite loop (Ctrl+C to stop)"
    exit 1
fi
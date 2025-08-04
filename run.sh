#!/bin/bash

# Image Recognition App Startup Script

set -e

echo "🚀 Starting Image Recognition App..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create uploads directory if it doesn't exist
mkdir -p uploads

# Run tests (optional)
if [ "$1" = "--test" ]; then
    echo "🧪 Running tests..."
    pytest tests/ -v
fi

# Start the application
echo "🌟 Starting Flask application..."
echo "📱 Open your browser and navigate to: http://localhost:5000"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python app.py
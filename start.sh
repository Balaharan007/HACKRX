#!/bin/bash

# HackRx 6.0 Document Intelligence Agent - Startup Script

echo "🚀 Starting HackRx 6.0 Document Intelligence Agent..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found! Please create it with your API keys."
    exit 1
fi

# Start PostgreSQL (if using local)
echo "🗄️  Starting PostgreSQL..."
# Uncomment if using local PostgreSQL
# sudo service postgresql start

# Start FastAPI server in background
echo "🌐 Starting FastAPI server..."
python main.py &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 5

# Start Streamlit app
echo "🎨 Starting Streamlit interface..."
streamlit run streamlit_app.py --server.port 8501

# Clean up when script exits
trap "kill $FASTAPI_PID" EXIT

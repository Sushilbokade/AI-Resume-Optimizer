#!/bin/bash

set -e

echo "🚀 Starting AI Resume Customizer in development mode..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found. Copying from .env.example..."
    cp .env.example .env
fi

# Start backend in background
echo "🖥️ Starting FastAPI backend..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting Streamlit frontend..."
cd frontend
streamlit run streamlit_app.py --server.port 8501 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo "✅ Development servers started!"
echo "🔗 Backend API: http://localhost:8000"
echo "🔗 Frontend: http://localhost:8501"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup processes
cleanup() {
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user interrupt
wait

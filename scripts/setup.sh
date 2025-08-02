#!/bin/bash

set -e

echo "🚀 Setting up AI Resume Customization App..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Found: $python_version"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install backend dependencies
echo "📚 Installing backend dependencies..."
pip install -r requirements.txt

# Install frontend dependencies  
echo "🎨 Installing frontend dependencies..."
pip install -r frontend/requirements.txt

# Download spaCy model
echo "🤖 Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p exports

# Copy environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment file..."
    cp .env.example .env
    echo "✏️ Please edit .env file with your configuration"
fi

# Initialize database (if local)
if [ "$1" = "--local" ]; then
    echo "🗄️ Setting up local database..."
    python -c "
import asyncio
from app.database.connection import init_db
asyncio.run(init_db())
print('Database initialized!')
"
fi

echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"  
echo "2. Run 'uvicorn app.main:app --reload' to start backend"
echo "3. Run 'streamlit run frontend/streamlit_app.py' to start frontend"

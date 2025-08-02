#!/bin/bash

set -e

echo "🚀 Starting deployment process..."

# Check if required environment variables are set
if [ -z "$RENDER_API_KEY" ]; then
    echo "❌ RENDER_API_KEY environment variable is not set"
    exit 1
fi

# Build and test locally first
echo "🔨 Building application locally..."
pip install -r requirements.txt
pip install -r frontend/requirements.txt

echo "🧪 Running tests..."
python -m pytest tests/ -v || echo "⚠️ Some tests failed, but continuing deployment..."

# Deploy message
echo "📦 Deploying to Render..."
echo "✅ Deployment configuration is in render.yaml"
echo "🔗 Push to main branch to trigger deployment"
echo "📊 Check deployment status at: https://dashboard.render.com"

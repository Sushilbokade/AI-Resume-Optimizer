# Quick Deployment Guide

## Deploy to Render.com

1. **Fork/Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd ai-resume-customizer
   ```

2. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

3. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New" → "Blueprint"  
   - Connect your GitHub repo
   - Render will use `render.yaml` for automatic deployment

4. **Set Environment Variables**
   In Render dashboard, set:
   - `SECRET_KEY`: Generate random 32-character string
   - `OPENAI_API_KEY`: Your OpenAI key (optional)
   - Other variables are auto-generated

5. **Access Application**
   - Backend API: `https://your-backend.onrender.com`
   - Frontend: `https://your-frontend.onrender.com`
   - API Docs: `https://your-backend.onrender.com/docs`

## Local Development

1. **Setup**
   ```bash
   chmod +x scripts/setup.sh
   ./scripts/setup.sh
   ```

2. **Run Development Servers**
   ```bash
   chmod +x scripts/run_dev.sh
   ./scripts/run_dev.sh
   ```

3. **Access Locally**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

## Quick Start Commands

```bash
# Setup everything
./scripts/setup.sh

# Start development servers  
./scripts/run_dev.sh

# Run tests
pytest tests/ -v

# Deploy (after pushing to main branch)
git push origin main
```

That's it! Your AI Resume Customizer will be live on Render.com.

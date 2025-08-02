from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import os
from typing import List, Optional
import uvicorn

from app.config import settings
from app.api import auth, resume, job_match, export
from app.database.connection import init_db
from app.services.ai_service import AIService

# Initialize AI service
ai_service = AIService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("Database initialized")

    # Create upload directories
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    os.makedirs("exports", exist_ok=True)

    yield
    # Shutdown
    print("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AI Resume Customization API",
    description="End-to-End AI-Powered Resume Customization Web Application",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume Management"])
app.include_router(job_match.router, prefix="/api/job-match", tags=["Job Matching"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/")
async def root():
    return {
        "message": "AI Resume Customization API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "ai_service": ai_service.is_available()}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=settings.DEBUG
    )

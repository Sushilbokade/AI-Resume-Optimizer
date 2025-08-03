from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
import os
import uuid
from datetime import datetime

from app.config import settings
from app.services.auth_service import AuthService
from app.services.resume_parser import ResumeParser
from app.models.resume import Resume, ResumeContent
from app.database.crud import ResumeCRUD

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
resume_parser = ResumeParser()
resume_crud = ResumeCRUD()

@router.post("/upload", response_model=dict)
async def upload_resume(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload and parse resume file"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        # Validate file
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )

        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format"
            )

        # Save file
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, f"{file_id}{file_ext}")

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse resume
        parsed_content = await resume_parser.parse_resume(file_path, file_ext)

        return {
            "file_id": file_id,
            "filename": file.filename,
            "parsed_content": parsed_content,
            "message": "Resume uploaded and parsed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.post("/save", response_model=dict)
async def save_resume(
    resume_data: dict,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Save parsed resume data"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        # Create resume object
        resume = Resume(
            user_id=user.id,
            title=resume_data.get("title", "My Resume"),
            content=ResumeContent(**resume_data.get("content", {})),
            original_filename=resume_data.get("filename"),
            is_master=resume_data.get("is_master", False)
        )

        # Save to database
        saved_resume = await resume_crud.create_resume(resume)

        return {
            "resume_id": saved_resume.id,
            "message": "Resume saved successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Save failed: {str(e)}"
        )

@router.get("/list", response_model=List[Resume])
async def list_resumes(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get user's resumes"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        resumes = await resume_crud.get_user_resumes(user.id)
        return resumes

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resumes: {str(e)}"
        )

@router.get("/{resume_id}", response_model=Resume)
async def get_resume(
    resume_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get specific resume"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        resume = await resume_crud.get_resume(resume_id, user.id)

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        return resume

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resume: {str(e)}"
        )

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Delete resume"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        await resume_crud.delete_resume(resume_id, user.id)
        return {"message": "Resume deleted successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete resume: {str(e)}"
        )

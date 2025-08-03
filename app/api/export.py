from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import FileResponse
from typing import Optional
import os

from app.config import settings
from app.services.auth_service import AuthService
from app.services.export_service import ExportService
from app.models.resume import ExportRequest
from app.database.crud import ResumeCRUD

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
export_service = ExportService()
resume_crud = ResumeCRUD()

@router.post("/generate", response_model=dict)
async def generate_resume(
    resume_id: str = Form(...),
    format: str = Form(...),
    template_id: Optional[str] = Form(None),
    filename: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Generate and export resume in specified format"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        # Get resume
        resume = await resume_crud.get_resume(resume_id, user.id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        # Create export request
        export_request = ExportRequest(
            resume_id=resume_id,
            format=format,
            template_id=template_id,
            filename=filename
        )

        # Generate file
        file_path = await export_service.generate_resume_file(
            resume, export_request, user.id
        )

        return {
            "file_path": file_path,
            "download_url": f"/api/export/download/{os.path.basename(file_path)}",
            "message": "Resume generated successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}"
        )

@router.get("/download/{filename}")
async def download_resume(
    filename: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Download generated resume file"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        file_path = os.path.join("exports", filename)

        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}"
        )

@router.get("/history", response_model=list)
async def get_export_history(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get user's export history"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        # Get export history from database
        history = await export_service.get_user_export_history(user.id)

        return history

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch export history: {str(e)}"
        )

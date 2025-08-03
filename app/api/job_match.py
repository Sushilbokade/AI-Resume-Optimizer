from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional

from app.config import settings
from app.services.ai_service import ai_service
from app.services.auth_service import AuthService
from app.services.job_analyzer import JobAnalyzer
from app.models.resume import JobDescription, MatchAnalysis
from app.database.crud import ResumeCRUD, JobDescriptionCRUD

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
job_analyzer = JobAnalyzer()
resume_crud = ResumeCRUD()
job_crud = JobDescriptionCRUD()

@router.post("/analyze-job", response_model=dict)
async def analyze_job_description(
    job_title: str = Form(...),
    company: str = Form(...),
    job_content: str = Form(...),
    job_url: Optional[str] = Form(None),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Analyze job description and extract key information"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        # Get user's API key
        user_api_key = await auth_service.get_user_api_key(user.id)

        # Create job description record
        job_desc = JobDescription(
            user_id=user.id,
            title=job_title,
            company=company,
            content=job_content,
            url=job_url
        )

        # Analyze job description using AI
        analysis = await job_analyzer.analyze_job_description(
            job_content, 
            user_api_key=user_api_key
        )

        # Update job description with analysis results
        job_desc.extracted_keywords = analysis.get("required_skills", [])
        job_desc.required_skills = analysis.get("required_skills", [])
        job_desc.preferred_qualifications = analysis.get("preferred_qualifications", [])
        job_desc.experience_level = analysis.get("experience_level")

        # Save job description
        saved_job = await job_crud.create_job_description(job_desc)

        return {
            "job_id": saved_job.id,
            "analysis": analysis,
            "message": "Job description analyzed successfully"
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job analysis failed: {str(e)}"
        )

@router.post("/match-resume", response_model=MatchAnalysis)
async def match_resume_to_job(
    resume_id: str = Form(...),
    job_description_id: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Match resume against job description and generate AI suggestions"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)

        # Get user's API key
        user_api_key = await auth_service.get_user_api_key(user.id)
        if not user_api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OpenAI API key not configured. Please set your API key first."
            )

        # Get resume and job description
        resume = await resume_crud.get_resume(resume_id, user.id)
        job_desc = await job_crud.get_job_description(job_description_id, user.id)

        if not resume or not job_desc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume or job description not found"
            )

        # Convert resume content to dict for AI processing
        resume_sections = {
            "summary": resume.content.summary,
            "experience": [exp.dict() for exp in resume.content.experience],
            "skills": resume.content.skills,
            "education": [edu.dict() for edu in resume.content.education],
            "projects": [proj.dict() for proj in resume.content.projects]
        }

        # Generate AI suggestions
        suggestions = await ai_service.enhance_resume_content(
            resume_sections=resume_sections,
            job_description=job_desc.content,
            user_api_key=user_api_key
        )

        # Calculate match score
        match_score = await job_analyzer.calculate_match_score(
            resume_sections, 
            job_desc.content,
            user_api_key=user_api_key
        )

        # Check ATS compliance
        resume_text = await job_analyzer.convert_resume_to_text(resume.content)
        ats_analysis = await ai_service.check_ats_compliance(
            resume_text, 
            user_api_key=user_api_key
        )

        # Create match analysis
        match_analysis = MatchAnalysis(
            resume_id=resume_id,
            job_description_id=job_description_id,
            overall_score=match_score,
            keyword_matches=job_desc.extracted_keywords,
            missing_keywords=[],
            suggestions=suggestions,
            ats_compliance_score=ats_analysis.get("overall_score", 0)
        )

        return match_analysis

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Resume matching failed: {str(e)}"
        )

@router.get("/my-jobs", response_model=List[JobDescription])
async def get_user_job_descriptions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get all job descriptions for the current user"""
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        jobs = await job_crud.get_user_job_descriptions(user.id)
        return jobs

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch job descriptions: {str(e)}"
        )

import json
import bcrypt
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from cryptography.fernet import Fernet
import base64

from app.database.connection import (
    UserModel, ResumeModel, JobDescriptionModel, 
    MatchAnalysisModel, ExportHistoryModel, AsyncSessionLocal
)
from app.models.user import User, UserCreate
from app.models.resume import Resume, JobDescription, ResumeContent
from app.config import settings

# Create encryption key for API keys
def get_encryption_key():
    # In production, store this securely
    key = base64.urlsafe_b64encode(settings.SECRET_KEY.encode()[:32].ljust(32, b'0'))
    return key

class UserCRUD:
    def __init__(self):
        self.cipher_suite = Fernet(get_encryption_key())

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        async with AsyncSessionLocal() as session:
            # Hash password
            password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # Create user model
            db_user = UserModel(
                email=user_data.email,
                name=user_data.name,
                password_hash=password_hash
            )

            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)

            return User(
                id=db_user.id,
                email=db_user.email,
                name=db_user.name,
                is_active=db_user.is_active,
                created_at=db_user.created_at,
                has_openai_key=False
            )

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            db_user = result.scalar_one_or_none()

            if not db_user:
                return None

            return User(
                id=db_user.id,
                email=db_user.email,
                name=db_user.name,
                is_active=db_user.is_active,
                created_at=db_user.created_at,
                has_openai_key=bool(db_user.openai_api_key_encrypted),
                password_hash=db_user.password_hash  # Include for authentication
            )

    async def update_user_api_key(self, user_id: str, api_key: str):
        """Update user's OpenAI API key"""
        async with AsyncSessionLocal() as session:
            # Encrypt API key
            encrypted_key = self.cipher_suite.encrypt(api_key.encode()).decode()

            await session.execute(
                update(UserModel)
                .where(UserModel.id == user_id)
                .values(openai_api_key_encrypted=encrypted_key)
            )
            await session.commit()

    async def get_user_api_key(self, user_id: str) -> Optional[str]:
        """Get user's decrypted OpenAI API key"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserModel.openai_api_key_encrypted)
                .where(UserModel.id == user_id)
            )
            encrypted_key = result.scalar_one_or_none()

            if not encrypted_key:
                return None

            # Decrypt API key
            try:
                decrypted_key = self.cipher_suite.decrypt(encrypted_key.encode()).decode()
                return decrypted_key
            except:
                return None

    async def user_has_api_key(self, user_id: str) -> bool:
        """Check if user has set their API key"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(UserModel.openai_api_key_encrypted)
                .where(UserModel.id == user_id)
            )
            encrypted_key = result.scalar_one_or_none()
            return bool(encrypted_key)

class ResumeCRUD:
    async def create_resume(self, resume: Resume) -> Resume:
        """Create a new resume"""
        async with AsyncSessionLocal() as session:
            db_resume = ResumeModel(
                user_id=resume.user_id,
                title=resume.title,
                content=json.dumps(resume.content.dict()),
                original_filename=resume.original_filename,
                file_path=resume.file_path,
                is_master=resume.is_master,
                version=resume.version
            )

            session.add(db_resume)
            await session.commit()
            await session.refresh(db_resume)

            return Resume(
                id=db_resume.id,
                user_id=db_resume.user_id,
                title=db_resume.title,
                content=ResumeContent(**json.loads(db_resume.content)),
                original_filename=db_resume.original_filename,
                file_path=db_resume.file_path,
                is_master=db_resume.is_master,
                version=db_resume.version,
                created_at=db_resume.created_at,
                updated_at=db_resume.updated_at
            )

    async def get_resume(self, resume_id: str, user_id: str) -> Optional[Resume]:
        """Get resume by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ResumeModel)
                .where(ResumeModel.id == resume_id, ResumeModel.user_id == user_id)
            )
            db_resume = result.scalar_one_or_none()

            if not db_resume:
                return None

            return Resume(
                id=db_resume.id,
                user_id=db_resume.user_id,
                title=db_resume.title,
                content=ResumeContent(**json.loads(db_resume.content)),
                original_filename=db_resume.original_filename,
                file_path=db_resume.file_path,
                is_master=db_resume.is_master,
                version=db_resume.version,
                created_at=db_resume.created_at,
                updated_at=db_resume.updated_at
            )

    async def get_user_resumes(self, user_id: str) -> List[Resume]:
        """Get all resumes for a user"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ResumeModel)
                .where(ResumeModel.user_id == user_id)
                .order_by(ResumeModel.created_at.desc())
            )
            db_resumes = result.scalars().all()

            resumes = []
            for db_resume in db_resumes:
                resumes.append(Resume(
                    id=db_resume.id,
                    user_id=db_resume.user_id,
                    title=db_resume.title,
                    content=ResumeContent(**json.loads(db_resume.content)),
                    original_filename=db_resume.original_filename,
                    file_path=db_resume.file_path,
                    is_master=db_resume.is_master,
                    version=db_resume.version,
                    created_at=db_resume.created_at,
                    updated_at=db_resume.updated_at
                ))

            return resumes

    async def delete_resume(self, resume_id: str, user_id: str):
        """Delete a resume"""
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(ResumeModel)
                .where(ResumeModel.id == resume_id, ResumeModel.user_id == user_id)
            )
            await session.commit()

class JobDescriptionCRUD:
    async def create_job_description(self, job_desc: JobDescription) -> JobDescription:
        """Create a new job description"""
        async with AsyncSessionLocal() as session:
            db_job = JobDescriptionModel(
                user_id=job_desc.user_id,
                title=job_desc.title,
                company=job_desc.company,
                content=job_desc.content,
                url=job_desc.url,
                extracted_keywords=json.dumps(job_desc.extracted_keywords),
                required_skills=json.dumps(job_desc.required_skills),
                preferred_qualifications=json.dumps(job_desc.preferred_qualifications),
                experience_level=job_desc.experience_level
            )

            session.add(db_job)
            await session.commit()
            await session.refresh(db_job)

            return JobDescription(
                id=db_job.id,
                user_id=db_job.user_id,
                title=db_job.title,
                company=db_job.company,
                content=db_job.content,
                url=db_job.url,
                extracted_keywords=json.loads(db_job.extracted_keywords or '[]'),
                required_skills=json.loads(db_job.required_skills or '[]'),
                preferred_qualifications=json.loads(db_job.preferred_qualifications or '[]'),
                experience_level=db_job.experience_level,
                created_at=db_job.created_at
            )

    async def get_job_description(self, job_id: str, user_id: str) -> Optional[JobDescription]:
        """Get job description by ID"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(JobDescriptionModel)
                .where(JobDescriptionModel.id == job_id, JobDescriptionModel.user_id == user_id)
            )
            db_job = result.scalar_one_or_none()

            if not db_job:
                return None

            return JobDescription(
                id=db_job.id,
                user_id=db_job.user_id,
                title=db_job.title,
                company=db_job.company,
                content=db_job.content,
                url=db_job.url,
                extracted_keywords=json.loads(db_job.extracted_keywords or '[]'),
                required_skills=json.loads(db_job.required_skills or '[]'),
                preferred_qualifications=json.loads(db_job.preferred_qualifications or '[]'),
                experience_level=db_job.experience_level,
                created_at=db_job.created_at
            )

    async def get_user_job_descriptions(self, user_id: str) -> List[JobDescription]:
        """Get all job descriptions for a user"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(JobDescriptionModel)
                .where(JobDescriptionModel.user_id == user_id)
                .order_by(JobDescriptionModel.created_at.desc())
            )
            db_jobs = result.scalars().all()

            jobs = []
            for db_job in db_jobs:
                jobs.append(JobDescription(
                    id=db_job.id,
                    user_id=db_job.user_id,
                    title=db_job.title,
                    company=db_job.company,
                    content=db_job.content,
                    url=db_job.url,
                    extracted_keywords=json.loads(db_job.extracted_keywords or '[]'),
                    required_skills=json.loads(db_job.required_skills or '[]'),
                    preferred_qualifications=json.loads(db_job.preferred_qualifications or '[]'),
                    experience_level=db_job.experience_level,
                    created_at=db_job.created_at
                ))

            return jobs

    async def delete_job_description(self, job_id: str, user_id: str):
        """Delete a job description"""
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(JobDescriptionModel)
                .where(JobDescriptionModel.id == job_id, JobDescriptionModel.user_id == user_id)
            )
            await session.commit()

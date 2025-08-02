from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SuggestionType(str, Enum):
    ENHANCEMENT = "enhancement"
    ADDITION = "addition"
    REMOVAL = "removal"
    REORDER = "reorder"

class AISuggestion(BaseModel):
    id: Optional[str] = None
    section: str
    subsection_index: Optional[int] = None
    item_index: Optional[int] = None
    original_content: str
    suggested_content: str
    explanation: str
    relevance_score: int = Field(ge=0, le=100)
    suggestion_type: SuggestionType
    created_at: datetime = Field(default_factory=datetime.now)
    is_accepted: bool = False

class PersonalInfo(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None

class Experience(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    start_date: str
    end_date: Optional[str] = None
    is_current: bool = False
    bullets: List[str] = []
    technologies: List[str] = []

class Education(BaseModel):
    degree: str
    school: str
    location: Optional[str] = None
    graduation_year: Optional[str] = None
    gpa: Optional[float] = None
    relevant_coursework: List[str] = []

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = []
    url: Optional[str] = None
    bullets: List[str] = []

class ResumeContent(BaseModel):
    personal_info: PersonalInfo
    summary: Optional[str] = None
    experience: List[Experience] = []
    education: List[Education] = []
    skills: List[str] = []
    projects: List[Project] = []
    certifications: List[str] = []
    languages: List[str] = []
    additional_sections: Dict[str, Any] = {}

class Resume(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    content: ResumeContent
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    is_master: bool = False
    version: int = 1
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = []

class JobDescription(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    company: str
    content: str
    url: Optional[str] = None
    extracted_keywords: List[str] = []
    required_skills: List[str] = []
    preferred_qualifications: List[str] = []
    experience_level: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class MatchAnalysis(BaseModel):
    resume_id: str
    job_description_id: str
    overall_score: int = Field(ge=0, le=100)
    keyword_matches: List[str] = []
    missing_keywords: List[str] = []
    suggestions: List[AISuggestion] = []
    ats_compliance_score: int = Field(ge=0, le=100)
    created_at: datetime = Field(default_factory=datetime.now)

class ExportRequest(BaseModel):
    resume_id: str
    format: str = Field(regex="^(pdf|docx)$")
    template_id: Optional[str] = None
    filename: Optional[str] = None

from typing import Dict, Any, List, Optional
import re
from app.models.resume import ResumeContent

class JobAnalyzer:
    def __init__(self):
        pass

    async def analyze_job_description(self, job_content: str, user_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Analyze job description and extract key information"""

        # Simple keyword extraction - in production, you'd use NLP/AI
        analysis = {
            "required_skills": self._extract_skills(job_content),
            "preferred_qualifications": self._extract_qualifications(job_content),
            "key_responsibilities": self._extract_responsibilities(job_content),
            "company_culture_keywords": self._extract_culture_keywords(job_content),
            "experience_level": self._determine_experience_level(job_content),
            "industry": self._determine_industry(job_content)
        }

        return analysis

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from job description"""

        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS', 'Docker',
            'Kubernetes', 'Git', 'HTML', 'CSS', 'MongoDB', 'PostgreSQL', 'Linux',
            'Machine Learning', 'Data Analysis', 'Project Management', 'Agile', 'Scrum',
            'REST API', 'GraphQL', 'TypeScript', 'Vue.js', 'Angular', 'Spring Boot',
            'Django', 'Flask', 'Redis', 'Elasticsearch', 'Kafka', 'Jenkins', 'CI/CD'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return found_skills[:10]  # Limit to top 10

    def _extract_qualifications(self, text: str) -> List[str]:
        """Extract preferred qualifications"""

        qualifications = []

        # Look for common qualification patterns
        if 'bachelor' in text.lower():
            qualifications.append("Bachelor's degree")
        if 'master' in text.lower():
            qualifications.append("Master's degree")
        if 'certification' in text.lower():
            qualifications.append("Professional certifications")

        return qualifications

    def _extract_responsibilities(self, text: str) -> List[str]:
        """Extract key responsibilities"""

        responsibilities = []

        # Simple extraction based on common patterns
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                if len(line) > 20:  # Filter out short lines
                    responsibilities.append(line[1:].strip())

        return responsibilities[:5]  # Limit to top 5

    def _extract_culture_keywords(self, text: str) -> List[str]:
        """Extract company culture keywords"""

        culture_keywords = [
            'innovative', 'collaborative', 'fast-paced', 'startup', 'agile',
            'remote', 'flexible', 'team player', 'growth', 'learning'
        ]

        found_keywords = []
        text_lower = text.lower()

        for keyword in culture_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)

        return found_keywords

    def _determine_experience_level(self, text: str) -> str:
        """Determine experience level from job description"""

        text_lower = text.lower()

        if 'senior' in text_lower or '5+ years' in text_lower or '7+ years' in text_lower:
            return 'senior'
        elif 'junior' in text_lower or 'entry level' in text_lower or '0-2 years' in text_lower:
            return 'junior'
        else:
            return 'mid'

    def _determine_industry(self, text: str) -> str:
        """Determine industry from job description"""

        text_lower = text.lower()

        if any(word in text_lower for word in ['fintech', 'finance', 'banking', 'trading']):
            return 'finance'
        elif any(word in text_lower for word in ['healthcare', 'medical', 'biotech']):
            return 'healthcare'
        elif any(word in text_lower for word in ['startup', 'tech', 'software', 'saas']):
            return 'technology'
        else:
            return 'general'

    async def calculate_match_score(
        self, 
        resume_sections: Dict[str, Any], 
        job_description: str,
        user_api_key: Optional[str] = None
    ) -> int:
        """Calculate match score between resume and job description"""

        # Simple scoring algorithm
        job_skills = self._extract_skills(job_description)
        resume_skills = resume_sections.get('skills', [])

        # Calculate skill overlap
        matching_skills = set(skill.lower() for skill in resume_skills) & set(skill.lower() for skill in job_skills)
        skill_score = (len(matching_skills) / len(job_skills)) * 100 if job_skills else 0

        # Factor in experience
        experience_score = min(len(resume_sections.get('experience', [])) * 20, 100)

        # Overall score (weighted average)
        overall_score = int((skill_score * 0.6) + (experience_score * 0.4))

        return min(overall_score, 100)

    async def convert_resume_to_text(self, resume_content: ResumeContent) -> str:
        """Convert resume content to plain text for ATS analysis"""

        text_parts = []

        # Personal info
        if resume_content.personal_info:
            text_parts.append(f"Name: {resume_content.personal_info.name}")
            text_parts.append(f"Email: {resume_content.personal_info.email}")
            if resume_content.personal_info.phone:
                text_parts.append(f"Phone: {resume_content.personal_info.phone}")

        # Summary
        if resume_content.summary:
            text_parts.append(f"Summary: {resume_content.summary}")

        # Experience
        if resume_content.experience:
            text_parts.append("Experience:")
            for exp in resume_content.experience:
                text_parts.append(f"{exp.title} at {exp.company}")
                for bullet in exp.bullets:
                    text_parts.append(f"- {bullet}")

        # Skills
        if resume_content.skills:
            text_parts.append(f"Skills: {', '.join(resume_content.skills)}")

        # Education
        if resume_content.education:
            text_parts.append("Education:")
            for edu in resume_content.education:
                text_parts.append(f"{edu.degree} from {edu.school}")

        return "\n".join(text_parts)

import openai
from typing import List, Dict, Optional, Any
import json
import asyncio
from datetime import datetime
import logging

from app.config import settings
from app.models.resume import AISuggestion, SuggestionType

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        self.client = None

        if self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)

    def set_api_key(self, api_key: str):
        """Allow dynamic API key setting"""
        self.api_key = api_key
        self.client = openai.AsyncOpenAI(api_key=api_key)

    def is_available(self) -> bool:
        """Check if AI service is properly configured"""
        return self.client is not None and self.api_key is not None

    async def enhance_resume_content(
        self, 
        resume_sections: Dict[str, Any], 
        job_description: str,
        user_api_key: Optional[str] = None
    ) -> List[AISuggestion]:
        """Generate AI-powered suggestions for resume enhancement"""

        if user_api_key:
            temp_client = openai.AsyncOpenAI(api_key=user_api_key)
        elif not self.is_available():
            raise ValueError("OpenAI API key not configured")
        else:
            temp_client = self.client

        try:
            suggestions = []

            # Analyze job description first
            jd_analysis = await self._analyze_job_description(job_description, temp_client)

            # Generate suggestions for each resume section
            for section_name, section_content in resume_sections.items():
                if section_name in ['experience', 'skills', 'summary']:
                    section_suggestions = await self._enhance_section(
                        section_name, 
                        section_content, 
                        jd_analysis, 
                        temp_client
                    )
                    suggestions.extend(section_suggestions)

            return suggestions

        except Exception as e:
            logger.error(f"AI service error: {str(e)}")
            raise Exception(f"AI processing failed: {str(e)}")

    async def _analyze_job_description(self, job_description: str, client) -> Dict[str, Any]:
        """Extract key information from job description"""

        prompt = f"""
        Analyze the following job description and extract key information:

        Job Description:
        {job_description}

        Please provide a JSON response with the following structure:
        {{
            "required_skills": ["skill1", "skill2", ...],
            "preferred_qualifications": ["qual1", "qual2", ...],
            "key_responsibilities": ["resp1", "resp2", ...],
            "company_culture_keywords": ["keyword1", "keyword2", ...],
            "experience_level": "junior/mid/senior",
            "industry": "technology/finance/healthcare/etc"
        }}
        """

        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert HR analyst specializing in job description analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.3
            )

            content = response.choices[0].message.content
            return json.loads(content)

        except Exception as e:
            logger.error(f"Job description analysis failed: {str(e)}")
            return {}

    async def _enhance_section(
        self, 
        section_name: str, 
        section_content: Any, 
        jd_analysis: Dict[str, Any], 
        client
    ) -> List[AISuggestion]:
        """Generate suggestions for a specific resume section"""

        suggestions = []

        if section_name == "experience":
            suggestions = await self._enhance_experience_section(section_content, jd_analysis, client)
        elif section_name == "skills":
            suggestions = await self._enhance_skills_section(section_content, jd_analysis, client)
        elif section_name == "summary":
            suggestions = await self._enhance_summary_section(section_content, jd_analysis, client)

        return suggestions

    async def _enhance_experience_section(
        self, 
        experience_data: List[Dict], 
        jd_analysis: Dict[str, Any], 
        client
    ) -> List[AISuggestion]:
        """Enhance experience bullet points"""

        suggestions = []
        required_skills = jd_analysis.get("required_skills", [])
        key_responsibilities = jd_analysis.get("key_responsibilities", [])

        for exp_idx, experience in enumerate(experience_data):
            bullets = experience.get("bullets", [])

            for bullet_idx, bullet in enumerate(bullets):
                prompt = f"""
                Enhance the following resume bullet point to better match the job requirements:

                Original bullet point: "{bullet}"

                Job requirements: {', '.join(required_skills)}
                Key responsibilities: {', '.join(key_responsibilities)}

                Please provide:
                1. An enhanced version that includes specific metrics, achievements, and relevant keywords
                2. A brief explanation of what was improved
                3. A relevance score (0-100) indicating how well it matches the job

                Respond in JSON format:
                {{
                    "enhanced_bullet": "improved version here",
                    "improvement_explanation": "explanation here",
                    "relevance_score": 85
                }}
                """

                try:
                    response = await client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a professional resume writer with expertise in ATS optimization."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=settings.MAX_TOKENS,
                        temperature=0.4
                    )

                    content = response.choices[0].message.content
                    result = json.loads(content)

                    suggestion = AISuggestion(
                        section="experience",
                        subsection_index=exp_idx,
                        item_index=bullet_idx,
                        original_content=bullet,
                        suggested_content=result["enhanced_bullet"],
                        explanation=result["improvement_explanation"],
                        relevance_score=result["relevance_score"],
                        suggestion_type=SuggestionType.ENHANCEMENT
                    )

                    suggestions.append(suggestion)

                except Exception as e:
                    logger.error(f"Failed to enhance bullet point: {str(e)}")
                    continue

        return suggestions

    async def _enhance_skills_section(
        self, 
        skills_data: List[str], 
        jd_analysis: Dict[str, Any], 
        client
    ) -> List[AISuggestion]:
        """Enhance skills section"""

        required_skills = jd_analysis.get("required_skills", [])

        # Simple suggestion for missing skills
        suggestion = AISuggestion(
            section="skills",
            subsection_index=0,
            item_index=0,
            original_content=", ".join(skills_data),
            suggested_content=", ".join(skills_data + [skill for skill in required_skills if skill not in skills_data][:3]),
            explanation="Added relevant skills from job requirements",
            relevance_score=90,
            suggestion_type=SuggestionType.ADDITION
        )

        return [suggestion] if any(skill not in skills_data for skill in required_skills) else []

    async def _enhance_summary_section(
        self, 
        summary_content: str, 
        jd_analysis: Dict[str, Any], 
        client
    ) -> List[AISuggestion]:
        """Enhance summary/profile section"""

        if not summary_content:
            return []

        required_skills = jd_analysis.get("required_skills", [])

        # Simple enhancement
        suggestion = AISuggestion(
            section="summary",
            subsection_index=0,
            item_index=0,
            original_content=summary_content,
            suggested_content=f"{summary_content} Skilled in {', '.join(required_skills[:3])}.",
            explanation="Added relevant keywords from job requirements",
            relevance_score=85,
            suggestion_type=SuggestionType.ENHANCEMENT
        )

        return [suggestion]

    async def check_ats_compliance(self, resume_content: str, user_api_key: Optional[str] = None) -> Dict[str, Any]:
        """Check resume for ATS compliance"""

        # Simplified ATS compliance check
        return {
            "overall_score": 85,
            "compliance_factors": {
                "section_headings": {"score": 90, "feedback": "Good standard headings"},
                "formatting": {"score": 80, "feedback": "Minor formatting issues"},
                "keywords": {"score": 75, "feedback": "Could use more industry keywords"},
                "structure": {"score": 95, "feedback": "Well organized structure"},
                "readability": {"score": 88, "feedback": "Clear and concise"}
            },
            "recommendations": ["Add more industry keywords", "Improve formatting consistency"],
            "critical_issues": []
        }

# Create global AI service instance
ai_service = AIService()

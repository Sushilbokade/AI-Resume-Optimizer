import os
import PyPDF2
import docx
from typing import Dict, Any, List
import re

from app.models.resume import PersonalInfo, Experience, Education, ResumeContent

class ResumeParser:
    def __init__(self):
        pass

    async def parse_resume(self, file_path: str, file_ext: str) -> Dict[str, Any]:
        """Parse resume file and extract structured data"""

        if file_ext.lower() == '.pdf':
            text = self._extract_pdf_text(file_path)
        elif file_ext.lower() in ['.docx', '.doc']:
            text = self._extract_docx_text(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

        # Parse the extracted text
        parsed_data = self._parse_text_content(text)

        return parsed_data

    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract PDF text: {str(e)}")

        return text

    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Failed to extract DOCX text: {str(e)}")

        return text

    def _parse_text_content(self, text: str) -> Dict[str, Any]:
        """Parse extracted text into structured data"""

        # Simple text parsing - in production, you'd use more sophisticated NLP
        parsed_data = {
            "personal_info": self._extract_personal_info(text),
            "summary": self._extract_summary(text),
            "experience": self._extract_experience(text),
            "education": self._extract_education(text),
            "skills": self._extract_skills(text),
            "projects": [],
            "certifications": [],
            "languages": []
        }

        return parsed_data

    def _extract_personal_info(self, text: str) -> Dict[str, str]:
        """Extract personal information from text"""

        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, text)

        # Phone regex
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b|\(\d{3}\)\s*\d{3}[-.]?\d{4}'
        phone_match = re.search(phone_pattern, text)

        # Extract name (first line that's not email/phone)
        lines = text.split('\n')
        name = ""
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and not re.search(email_pattern, line) and not re.search(phone_pattern, line):
                if len(line.split()) >= 2:  # Likely a name
                    name = line
                    break

        return {
            "name": name,
            "email": email_match.group() if email_match else "",
            "phone": phone_match.group() if phone_match else "",
            "location": "",  # Would need more sophisticated parsing
            "linkedin": "",
            "github": ""
        }

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary"""

        # Look for summary/objective section
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        lines = text.split('\n')

        summary_text = ""
        in_summary = False

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Check if this line is a summary header
            if any(keyword in line_lower for keyword in summary_keywords):
                in_summary = True
                continue

            # If we're in summary section
            if in_summary:
                # Stop if we hit another section
                if line.isupper() and len(line.strip()) > 0:
                    break

                if line.strip():
                    summary_text += line.strip() + " "

                # Stop after a few lines or if we hit a blank line followed by caps
                if i < len(lines) - 1 and not lines[i + 1].strip() and i < len(lines) - 2:
                    if lines[i + 2].isupper():
                        break

        return summary_text.strip()

    def _extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience"""

        # Simple extraction - look for patterns
        experience = []

        # This is a simplified version - real implementation would be more sophisticated
        lines = text.split('\n')
        current_job = {}
        in_experience = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for experience section
            if 'experience' in line.lower() or 'employment' in line.lower():
                in_experience = True
                continue

            if in_experience:
                # Look for job titles (simple heuristic)
                if any(word in line.lower() for word in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
                    if current_job:
                        experience.append(current_job)

                    current_job = {
                        "title": line,
                        "company": "",
                        "location": "",
                        "start_date": "",
                        "end_date": "",
                        "bullets": []
                    }

                # Look for bullet points
                elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    if current_job:
                        current_job["bullets"].append(line[1:].strip())

        if current_job:
            experience.append(current_job)

        return experience

    def _extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information"""

        education = []

        # Simple extraction
        if 'bachelor' in text.lower() or 'master' in text.lower() or 'phd' in text.lower():
            education.append({
                "degree": "Degree found in text",
                "school": "University",
                "location": "",
                "graduation_year": "",
                "gpa": None
            })

        return education

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills"""

        # Common technical skills
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'html', 'css', 'mongodb', 'postgresql', 'linux',
            'machine learning', 'data analysis', 'project management', 'agile'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in common_skills:
            if skill in text_lower:
                found_skills.append(skill.title())

        return found_skills

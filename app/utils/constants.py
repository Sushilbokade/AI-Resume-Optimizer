# File upload constants
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_EXTENSIONS = ['.pdf', '.docx', '.doc']

# Resume parsing constants
RESUME_SECTIONS = [
    'personal_info',
    'summary',
    'experience', 
    'education',
    'skills',
    'projects',
    'certifications',
    'languages'
]

# AI processing constants
MAX_AI_SUGGESTIONS = 10
MIN_RELEVANCE_SCORE = 60
MAX_OPENAI_TOKENS = 4000

# Export formats
EXPORT_FORMATS = ['pdf', 'docx']

# ATS compliance factors
ATS_COMPLIANCE_FACTORS = [
    'section_headings',
    'formatting',
    'keywords',
    'structure',
    'readability',
    'file_format',
    'length',
    'contact_info',
    'date_format',
    'bullet_points'
]

# Common skills database
COMMON_TECHNICAL_SKILLS = [
    'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Node.js',
    'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'AWS', 'Docker',
    'Kubernetes', 'Git', 'Linux', 'HTML', 'CSS', 'REST API',
    'GraphQL', 'Machine Learning', 'Data Analysis', 'CI/CD',
    'Jenkins', 'Terraform', 'Ansible', 'Microservices'
]

COMMON_SOFT_SKILLS = [
    'Leadership', 'Communication', 'Problem Solving', 'Team Collaboration',
    'Project Management', 'Critical Thinking', 'Adaptability',
    'Time Management', 'Mentoring', 'Public Speaking'
]

# Job analysis constants
EXPERIENCE_LEVELS = ['entry', 'junior', 'mid', 'senior', 'lead', 'principal']

INDUSTRIES = [
    'technology', 'finance', 'healthcare', 'education', 'retail',
    'manufacturing', 'consulting', 'government', 'nonprofit', 'startup'
]

# Error messages
ERROR_MESSAGES = {
    'invalid_file_type': 'Invalid file type. Please upload PDF, DOCX, or DOC files only.',
    'file_too_large': 'File size exceeds the maximum limit of 10MB.',
    'parsing_failed': 'Failed to parse the resume. Please ensure the file is not corrupted.',
    'ai_processing_failed': 'AI processing failed. Please check your API key and try again.',
    'invalid_api_key': 'Invalid OpenAI API key. Please check your key and try again.',
    'unauthorized': 'You are not authorized to perform this action.',
    'not_found': 'The requested resource was not found.',
    'invalid_input': 'Invalid input provided. Please check your data and try again.'
}

# Success messages
SUCCESS_MESSAGES = {
    'resume_uploaded': 'Resume uploaded and parsed successfully!',
    'resume_saved': 'Resume saved successfully!',
    'job_analyzed': 'Job description analyzed successfully!',
    'suggestions_generated': 'AI suggestions generated successfully!',
    'resume_exported': 'Resume exported successfully!',
    'api_key_saved': 'OpenAI API key saved successfully!',
    'profile_updated': 'Profile updated successfully!'
}

# Default resume template
DEFAULT_RESUME_TEMPLATE = {
    'name': 'Professional Classic',
    'description': 'Clean, traditional layout perfect for corporate roles',
    'sections': [
        'personal_info',
        'summary', 
        'experience',
        'education',
        'skills',
        'certifications'
    ]
}

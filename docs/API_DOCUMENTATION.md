# AI Resume Customization API Documentation

## Overview
This document provides comprehensive API documentation for the AI Resume Customization application.

## Base URL
- Local Development: `http://localhost:8000`
- Production: `https://your-app.onrender.com`

## Authentication
All API endpoints (except authentication) require a Bearer token in the Authorization header:
```
Authorization: Bearer <access_token>
```

## API Endpoints

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "uuid",
  "email": "john@example.com"
}
```

#### POST /api/auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer"
}
```

#### GET /api/auth/me
Get current user information.

**Response:**
```json
{
  "id": "uuid",
  "email": "john@example.com",
  "name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00",
  "has_openai_key": true
}
```

### Resume Management

#### POST /api/resume/upload
Upload and parse a resume file.

**Request:** Multipart form data with file upload

**Response:**
```json
{
  "file_id": "uuid",
  "filename": "resume.pdf",
  "parsed_content": {
    "personal_info": {...},
    "summary": "...",
    "experience": [...],
    "skills": [...],
    "education": [...]
  },
  "message": "Resume uploaded and parsed successfully"
}
```

#### POST /api/resume/save
Save parsed resume data to database.

**Request Body:**
```json
{
  "title": "My Resume",
  "content": {
    "personal_info": {...},
    "summary": "...",
    "experience": [...],
    "skills": [...],
    "education": [...]
  },
  "is_master": true
}
```

#### GET /api/resume/list
Get all resumes for the current user.

**Response:**
```json
[
  {
    "id": "uuid",
    "title": "My Resume",
    "created_at": "2024-01-01T00:00:00",
    "is_master": true,
    "version": 1
  }
]
```

### Job Matching

#### POST /api/job-match/analyze-job
Analyze a job description and extract key information.

**Request Body (Form Data):**
- `job_title`: Senior Software Engineer
- `company`: Google
- `job_content`: Full job description text
- `job_url`: https://... (optional)

**Response:**
```json
{
  "job_id": "uuid",
  "analysis": {
    "required_skills": ["Python", "React", "AWS"],
    "experience_level": "senior",
    "key_responsibilities": [...]
  },
  "message": "Job description analyzed successfully"
}
```

#### POST /api/job-match/match-resume
Match resume against job description and generate AI suggestions.

**Request Body (Form Data):**
- `resume_id`: uuid
- `job_description_id`: uuid

**Response:**
```json
{
  "resume_id": "uuid",
  "job_description_id": "uuid", 
  "overall_score": 85,
  "suggestions": [
    {
      "section": "experience",
      "original_content": "...",
      "suggested_content": "...",
      "explanation": "...",
      "relevance_score": 90
    }
  ],
  "ats_compliance_score": 78
}
```

### Export

#### POST /api/export/generate
Generate resume in specified format.

**Request Body (Form Data):**
- `resume_id`: uuid
- `format`: pdf or docx
- `template_id`: template_uuid (optional)
- `filename`: custom_filename (optional)

**Response:**
```json
{
  "file_path": "/path/to/generated/resume.pdf",
  "download_url": "/api/export/download/resume.pdf",
  "message": "Resume generated successfully"
}
```

#### GET /api/export/download/{filename}
Download generated resume file.

**Response:** File download

## Error Responses

All endpoints return error responses in this format:
```json
{
  "detail": "Error message"
}
```

Common HTTP status codes:
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting
API endpoints are rate limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- File upload endpoints: 10 requests per hour
- AI processing endpoints: 20 requests per hour

## OpenAI Integration
Users must provide their own OpenAI API keys for AI functionality:
1. Set API key via `POST /api/auth/set-api-key`
2. Check API key status via `GET /api/auth/api-key-status`

## File Upload Limits
- Maximum file size: 10MB
- Supported formats: PDF, DOCX, DOC
- Files are stored securely with user isolation

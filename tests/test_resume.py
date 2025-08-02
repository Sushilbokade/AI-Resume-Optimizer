import pytest
from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def get_auth_token():
    """Helper function to get authentication token"""
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "name": "Resume User",
            "email": "resume@example.com",
            "password": "TestPassword123"
        }
    )

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "resume@example.com",
            "password": "TestPassword123"
        }
    )
    return login_response.json()["access_token"]

def test_resume_upload():
    """Test resume file upload"""
    token = get_auth_token()

    # Create a dummy PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"

    response = client.post(
        "/api/resume/upload",
        files={"file": ("test_resume.pdf", io.BytesIO(pdf_content), "application/pdf")},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "file_id" in data
    assert "parsed_content" in data

def test_resume_save():
    """Test saving parsed resume data"""
    token = get_auth_token()

    resume_data = {
        "title": "My Test Resume",
        "content": {
            "personal_info": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "123-456-7890",
                "location": "San Francisco, CA"
            },
            "summary": "Experienced software engineer",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "start_date": "2020-01-01",
                    "end_date": "Present",
                    "bullets": ["Developed web applications", "Led team of 3 developers"]
                }
            ],
            "education": [
                {
                    "degree": "B.S. Computer Science",
                    "school": "University of California",
                    "graduation_year": "2019"
                }
            ],
            "skills": ["Python", "JavaScript", "React", "SQL"],
            "projects": [],
            "certifications": [],
            "languages": []
        },
        "is_master": True
    }

    response = client.post(
        "/api/resume/save",
        json=resume_data,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "resume_id" in data
    assert data["message"] == "Resume saved successfully"

def test_list_resumes():
    """Test listing user resumes"""
    token = get_auth_token()

    response = client.get(
        "/api/resume/list",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_unauthorized_access():
    """Test unauthorized access to resume endpoints"""
    response = client.get("/api/resume/list")
    assert response.status_code == 403  # Should require authentication

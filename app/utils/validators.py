from typing import List, Optional
import re
from email_validator import validate_email, EmailNotValidError

def validate_email_address(email: str) -> bool:
    """Validate email address"""
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_password(password: str) -> tuple[bool, List[str]]:
    """Validate password strength"""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit")

    return len(errors) == 0, errors

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if not filename:
        return False

    ext = filename.lower().split('.')[-1]
    return f".{ext}" in [ext.lower() for ext in allowed_extensions]

def validate_file_size(file_size: int, max_size: int) -> bool:
    """Validate file size"""
    return file_size <= max_size

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace dangerous characters
    safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

    # Limit length
    if len(safe_filename) > 255:
        safe_filename = safe_filename[:255]

    return safe_filename

def validate_openai_api_key(api_key: str) -> bool:
    """Validate OpenAI API key format"""
    if not api_key:
        return False

    # Basic format validation
    return api_key.startswith('sk-') and len(api_key) > 20

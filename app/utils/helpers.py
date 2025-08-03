import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

def generate_unique_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)

def hash_string(text: str) -> str:
    """Hash a string using SHA-256"""
    return hashlib.sha256(text.encode()).hexdigest()

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"

def calculate_age_from_date(date_str: str) -> Optional[int]:
    """Calculate age from date string"""
    try:
        birth_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return age
    except:
        return None

def extract_domain_from_email(email: str) -> Optional[str]:
    """Extract domain from email address"""
    try:
        return email.split('@')[1].lower()
    except:
        return None

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix

def parse_date_string(date_str: str) -> Optional[datetime]:
    """Parse various date string formats"""
    formats = [
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M:%S",
        "%m/%d/%Y %H:%M:%S"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None

def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data leaving only a few characters visible"""
    if len(data) <= visible_chars * 2:
        return "*" * len(data)

    return data[:visible_chars] + "*" * (len(data) - visible_chars * 2) + data[-visible_chars:]

def create_slug(text: str) -> str:
    """Create a URL-friendly slug from text"""
    import re

    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)

    return slug.strip('-')

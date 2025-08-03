from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta

from app.config import settings
from app.models.user import User, UserCreate, UserLogin, Token
from app.services.auth_service import AuthService
from app.database.crud import UserCRUD

router = APIRouter()
security = HTTPBearer()
auth_service = AuthService()
user_crud = UserCRUD()

class APIKeyRequest(BaseModel):
    openai_api_key: str

@router.post("/register", response_model=dict)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = await user_crud.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )

        # Create new user
        user = await user_crud.create_user(user_data)
        return {
            "message": "User registered successfully",
            "user_id": user.id,
            "email": user.email
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """User login with email and password"""
    try:
        user = await auth_service.authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        access_token = auth_service.create_access_token(data={"sub": user.email})
        return Token(access_token=access_token, token_type="bearer")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user information"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/set-api-key")
async def set_openai_api_key(
    api_key_data: APIKeyRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Set OpenAI API key for user"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)

        # Store encrypted API key in user profile
        await user_crud.update_user_api_key(user.id, api_key_data.openai_api_key)

        return {"message": "API key set successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set API key: {str(e)}"
        )

@router.get("/api-key-status")
async def check_api_key_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Check if user has set their OpenAI API key"""
    try:
        token = credentials.credentials
        user = await auth_service.get_current_user(token)

        has_api_key = await user_crud.user_has_api_key(user.id)

        return {"has_api_key": has_api_key}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check API key status: {str(e)}"
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """User logout"""
    return {"message": "Logged out successfully"}

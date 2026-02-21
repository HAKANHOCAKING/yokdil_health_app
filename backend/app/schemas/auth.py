"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional
from app.models.user import UserRole


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.STUDENT
    tenant_id: UUID


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenRefresh(BaseModel):
    """Refresh token request"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    full_name: str
    role: UserRole
    tenant_id: UUID
    is_active: bool
    is_email_verified: bool
    
    class Config:
        from_attributes = True

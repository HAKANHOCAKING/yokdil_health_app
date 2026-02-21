"""
Enhanced Security utilities: JWT, Argon2 password hashing, token rotation, device tracking
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import secrets
import hashlib

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.models.session_device import SessionDevice, RefreshToken
from app.schemas.auth import TokenData

# SECURITY ENHANCEMENT: Argon2id password hashing (more secure than bcrypt)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,        # 3 iterations
    argon2__parallelism=4,      # 4 threads
)

# Bearer token scheme
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against Argon2 hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2id"""
    return pwd_context.hash(password)


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create short-lived JWT access token (10-15 minutes)"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # SECURITY: Short-lived access tokens (15 minutes)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access",
        "jti": secrets.token_urlsafe(16),  # Unique token ID
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: str, device_id: str) -> tuple[str, str]:
    """
    Create long-lived refresh token with rotation support
    Returns: (token, token_hash)
    """
    token = secrets.token_urlsafe(64)
    
    # Store hash of refresh token (not plain text)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    return token, token_hash


def decode_token(token: str) -> TokenData:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return TokenData(user_id=user_id)
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user with tenant context"""
    token = credentials.credentials
    token_data = decode_token(token)
    
    # Get user
    result = await db.execute(
        select(User).filter(
            and_(
                User.id == token_data.user_id,
                User.is_active == True,
            )
        )
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # SECURITY: Set tenant context for this request
    # This will be used in tenant-scoped queries
    request.state.user = user
    request.state.tenant_id = user.tenant_id
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


class RoleChecker:
    """
    RBAC: Role-Based Access Control
    Enforces user roles at endpoint level
    """
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_user)) -> User:
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.allowed_roles)}",
            )
        return user


class TenantChecker:
    """
    Multi-tenancy: Ensure user can only access their tenant's data
    """
    
    async def __call__(
        self,
        request: Request,
        user: User = Depends(get_current_user),
    ) -> User:
        # Tenant ID is already set in get_current_user
        # This is an additional check for critical operations
        if not user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User must belong to a tenant",
            )
        return user


# Role-based dependencies
require_student = RoleChecker(["student", "teacher", "admin"])
require_teacher = RoleChecker(["teacher", "admin"])
require_admin = RoleChecker(["admin"])


async def verify_refresh_token(
    token: str,
    device_id: str,
    db: AsyncSession,
) -> Optional[RefreshToken]:
    """
    Verify refresh token with reuse detection
    SECURITY: Rotating refresh tokens + reuse detection
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    result = await db.execute(
        select(RefreshToken).filter(
            and_(
                RefreshToken.token_hash == token_hash,
                RefreshToken.device_id == device_id,
                RefreshToken.is_valid == True,
                RefreshToken.expires_at > datetime.utcnow(),
            )
        )
    )
    
    refresh_token = result.scalar_one_or_none()
    
    if not refresh_token:
        # SECURITY: Token reuse detection - invalidate all user's tokens
        result = await db.execute(
            select(RefreshToken).filter(
                RefreshToken.token_hash == token_hash,
            )
        )
        suspicious_token = result.scalar_one_or_none()
        
        if suspicious_token:
            # Token was used before - possible theft
            # Invalidate all tokens for this user
            await db.execute(
                select(RefreshToken)
                .filter(RefreshToken.user_id == suspicious_token.user_id)
                .update({"is_valid": False})
            )
            await db.commit()
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token reuse detected. All sessions invalidated.",
            )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    return refresh_token


def get_device_info(request: Request) -> dict:
    """Extract device information from request"""
    user_agent = request.headers.get("user-agent", "Unknown")
    
    # Parse user agent
    from user_agents import parse
    ua = parse(user_agent)
    
    return {
        "device_type": "mobile" if ua.is_mobile else "tablet" if ua.is_tablet else "desktop",
        "os": f"{ua.os.family} {ua.os.version_string}",
        "browser": f"{ua.browser.family} {ua.browser.version_string}",
        "ip_address": request.client.host if request.client else "Unknown",
    }

"""
Application Configuration using Pydantic Settings
SECURITY ENHANCED: Secure defaults, secret management
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings with security-first defaults"""
    
    # Project Info
    PROJECT_NAME: str = "YÖKDİL Health App"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    
    # JWT (SECURITY: Short-lived access tokens)
    SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 15 min
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # MinIO / S3
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(..., env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(..., env="MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = Field(default="yokdil-pdfs", env="MINIO_BUCKET_NAME")
    MINIO_SECURE: bool = Field(default=False, env="MINIO_SECURE")
    
    # Redis (Sessions + Cache + Celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # OpenAI
    OPENAI_API_KEY: str = Field(default="", env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", env="OPENAI_MODEL")
    
    # CORS (SECURITY: Whitelist only)
    ALLOWED_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="ALLOWED_ORIGINS"
    )
    
    # Rate Limiting (SECURITY: Stricter limits)
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    LOGIN_RATE_LIMIT: str = Field(default="5/minute", env="LOGIN_RATE_LIMIT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # OCR
    TESSERACT_PATH: str = Field(default="/usr/bin/tesseract", env="TESSERACT_PATH")
    
    # Security
    HSTS_MAX_AGE: int = Field(default=31536000, env="HSTS_MAX_AGE")  # 1 year
    ENABLE_HSTS: bool = Field(default=True, env="ENABLE_HSTS")
    
    # File Upload (SECURITY: Size limits)
    MAX_UPLOAD_SIZE_MB: int = Field(default=50, env="MAX_UPLOAD_SIZE_MB")
    
    # Data Retention (KVKK)
    AUDIT_LOG_RETENTION_DAYS: int = Field(default=730, env="AUDIT_LOG_RETENTION_DAYS")  # 2 years
    ATTEMPT_RETENTION_DAYS: int = Field(default=365, env="ATTEMPT_RETENTION_DAYS")  # 1 year
    
    # MFA (Optional)
    ENABLE_MFA: bool = Field(default=False, env="ENABLE_MFA")
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Ensure secret key is strong enough"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters")
        if v == "your-super-secret-key-change-in-production-min-32-chars":
            raise ValueError("SECRET_KEY must be changed from default value")
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

"""
YÖKDİL Health App - FastAPI Main Application
SECURITY ENHANCED: Middleware, HSTS, audit logging
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time

from app.core.config import settings
from app.core.database import engine, create_db_and_tables
from app.api.v1.router import api_router
from app.middleware.audit_middleware import AuditMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    # Startup
    logger.info("🚀 Starting YÖKDİL Health App Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    
    # Initialize database
    await create_db_and_tables()
    logger.info("✅ Database initialized")
    
    # Security warnings
    if settings.ENVIRONMENT == "production":
        if not settings.ENABLE_HSTS:
            logger.warning("⚠️  HSTS is disabled in production!")
        if len(settings.SECRET_KEY) < 32:
            logger.error("❌ SECRET_KEY is too short for production!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down gracefully...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade YÖKDİL Health exam preparation API with security-first design",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# SECURITY: Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# SECURITY: CORS Middleware (whitelist only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# SECURITY: Audit middleware (request ID + correlation)
app.add_middleware(AuditMiddleware)

# SECURITY: Trusted host middleware (prevent host header attacks)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.yourdomain.com", "yourdomain.com"]
    )


# SECURITY: Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # SECURITY: HSTS (HTTP Strict Transport Security)
    if settings.ENABLE_HSTS and settings.ENVIRONMENT == "production":
        response.headers["Strict-Transport-Security"] = f"max-age={settings.HSTS_MAX_AGE}; includeSubDomains; preload"
    
    # SECURITY: Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    
    # SECURITY: XSS Protection
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # SECURITY: Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # SECURITY: Content Security Policy (basic)
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    # SECURITY: Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response


# Request timing middleware (performance monitoring)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add request processing time to headers"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Log slow requests
    if process_time > 1.0:  # > 1 second
        logger.warning(
            f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s",
            extra={"request_id": getattr(request.state, "request_id", None)}
        )
    
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    No authentication required
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "YÖKDİL Health App API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None,
        "security": "enterprise-grade",
        "features": [
            "Multi-tenancy",
            "RBAC",
            "Audit logging",
            "Token rotation",
            "KVKK compliance"
        ]
    }


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler
    SECURITY: Don't leak stack traces in production
    """
    request_id = getattr(request.state, "request_id", "unknown")
    
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"request_id": request_id}
    )
    
    if settings.ENVIRONMENT == "development":
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "detail": str(exc),
                "traceback": traceback.format_exc(),
                "request_id": request_id,
            },
        )
    
    # SECURITY: Generic error in production
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        },
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info(f"🏥 {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API Prefix: {settings.API_V1_PREFIX}")
    logger.info(f"CORS Origins: {', '.join(settings.ALLOWED_ORIGINS)}")
    logger.info(f"Access Token TTL: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    logger.info(f"HSTS Enabled: {settings.ENABLE_HSTS}")
    logger.info("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )

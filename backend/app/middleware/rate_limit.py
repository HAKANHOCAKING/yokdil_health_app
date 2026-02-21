"""
Enhanced rate limiting middleware
Different limits for different endpoint types
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import redis
from app.core.config import settings


# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["60/minute"],
    storage_uri=settings.REDIS_URL,
)


# Custom rate limits for specific endpoints
RATE_LIMITS = {
    # Authentication (stricter)
    "/api/v1/auth/login": "5/minute",
    "/api/v1/auth/register": "3/minute",
    "/api/v1/auth/refresh": "10/minute",
    "/api/v1/auth/password-reset": "3/hour",
    
    # PDF upload (resource intensive)
    "/api/v1/admin/pdfs/upload": "10/hour",
    
    # AI endpoints (expensive)
    "/api/v1/questions/{id}/traps": "30/minute",
    "/api/v1/admin/traps/analyze": "20/minute",
    
    # General API
    "/api/v1/*": "120/minute",
}


class EnhancedRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Apply different rate limits based on endpoint and user
    """
    
    def __init__(self, app, redis_client=None):
        super().__init__(app)
        self.redis_client = redis_client or redis.from_url(settings.REDIS_URL)
    
    async def dispatch(self, request: Request, call_next):
        # Get user from token (if authenticated)
        user_id = None
        if hasattr(request.state, "user"):
            user_id = str(request.state.user.id)
        
        # Create rate limit key
        ip = request.client.host if request.client else "unknown"
        key_prefix = f"rl:{user_id or ip}:{request.url.path}"
        
        # Check rate limit
        path = request.url.path
        limit = self._get_limit_for_path(path)
        
        if not self._check_rate_limit(key_prefix, limit):
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type="application/json"
            )
        
        response = await call_next(request)
        return response
    
    def _get_limit_for_path(self, path: str) -> tuple[int, int]:
        """Get rate limit for path (requests, seconds)"""
        for pattern, limit_str in RATE_LIMITS.items():
            if self._path_matches(path, pattern):
                # Parse "5/minute" -> (5, 60)
                count, period = limit_str.split("/")
                seconds = {
                    "second": 1,
                    "minute": 60,
                    "hour": 3600,
                    "day": 86400,
                }[period]
                return int(count), seconds
        
        # Default: 60/minute
        return 60, 60
    
    def _path_matches(self, path: str, pattern: str) -> bool:
        """Simple wildcard matching"""
        if "*" in pattern:
            prefix = pattern.split("*")[0]
            return path.startswith(prefix)
        return path == pattern
    
    def _check_rate_limit(self, key: str, limit: tuple[int, int]) -> bool:
        """Check if request is within rate limit"""
        max_requests, window = limit
        
        current = self.redis_client.incr(key)
        
        if current == 1:
            self.redis_client.expire(key, window)
        
        return current <= max_requests

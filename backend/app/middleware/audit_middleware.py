"""
Audit logging middleware
Automatically logs requests to sensitive endpoints
"""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject request_id and prepare audit context
    """
    
    async def dispatch(self, request: Request, call_next):
        # Generate unique request ID for correlation
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response


async def log_audit(
    db: AsyncSession,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    action: str,
    resource_type: str = None,
    resource_id: str = None,
    description: str = None,
    changes: dict = None,
    metadata: dict = None,
    ip_address: str = None,
    user_agent: str = None,
    request_id: str = None,
    status: str = "success",
    error_message: str = None,
):
    """
    Helper function to log audit events
    Call this from endpoints for critical operations
    """
    from app.models.audit_log import AuditLog
    
    audit = AuditLog(
        user_id=user_id,
        tenant_id=tenant_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        description=description,
        changes=changes,
        metadata=metadata,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
        status=status,
        error_message=error_message,
    )
    
    db.add(audit)
    await db.commit()
    
    logger.info(
        f"AUDIT: {action} by user {user_id} on {resource_type}:{resource_id} - {status}",
        extra={"request_id": request_id}
    )

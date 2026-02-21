"""
Audit logging for compliance and security
SECURITY: Track all critical operations
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class AuditAction(str, enum.Enum):
    """Audit action categories"""
    # Authentication
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    AUTH_LOGOUT_ALL = "auth_logout_all"
    AUTH_REGISTER = "auth_register"
    AUTH_PASSWORD_CHANGE = "auth_password_change"
    AUTH_MFA_ENABLE = "auth_mfa_enable"
    AUTH_MFA_DISABLE = "auth_mfa_disable"
    
    # User Management
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DELETE = "user_delete"
    USER_ROLE_CHANGE = "user_role_change"
    USER_ACTIVATE = "user_activate"
    USER_DEACTIVATE = "user_deactivate"
    
    # PDF & Content
    PDF_UPLOAD = "pdf_upload"
    PDF_PARSE = "pdf_parse"
    PDF_DELETE = "pdf_delete"
    QUESTION_CREATE = "question_create"
    QUESTION_EDIT = "question_edit"
    QUESTION_DELETE = "question_delete"
    TRAP_LABEL_APPROVE = "trap_label_approve"
    
    # Assignments
    ASSIGNMENT_CREATE = "assignment_create"
    ASSIGNMENT_UPDATE = "assignment_update"
    ASSIGNMENT_DELETE = "assignment_delete"
    
    # Data Export/Delete (KVKK)
    DATA_EXPORT = "data_export"
    DATA_DELETE = "data_delete"
    
    # System
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    TENANT_CREATE = "tenant_create"
    TENANT_UPDATE = "tenant_update"


class AuditLog(Base):
    """
    Comprehensive audit logging
    WHO did WHAT on WHICH resource at WHEN from WHERE
    """
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    user_email = Column(String(255), nullable=True)  # Denormalized for retention
    user_role = Column(String(50), nullable=True)
    
    # Tenant (multi-tenancy)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # What
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True, index=True)  # User, Question, PDF, etc.
    resource_id = Column(String(255), nullable=True, index=True)
    
    # Details
    description = Column(Text, nullable=True)
    changes = Column(JSONB, nullable=True)  # {"field": {"old": "...", "new": "..."}}
    log_metadata = Column("metadata", JSONB, nullable=True)  # Additional context
    
    # When
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Where
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_id = Column(String(255), nullable=True)
    
    # Request context
    request_id = Column(String(100), nullable=True, index=True)  # Correlation ID
    
    # Status
    status = Column(String(20), default="success", nullable=False)  # success, failure, warning
    error_message = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    tenant = relationship("Tenant", back_populates="audit_logs")

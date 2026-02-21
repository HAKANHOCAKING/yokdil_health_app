"""
Multi-tenancy: Tenant (Institution) model with Row-Level Security support
SECURITY: Data isolation per tenant
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SQLEnum, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Tenant(Base):
    """
    Tenant (Institution) for multi-tenancy
    All data is scoped to a tenant
    """
    __tablename__ = "tenants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, index=True)
    subdomain = Column(String(100), nullable=True, unique=True, index=True)  # optional custom domain
    
    # Subscription
    subscription_tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    
    # Limits
    max_users = Column(Integer, default=100, nullable=False)
    max_storage_gb = Column(Integer, default=10, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Settings
    settings = Column(JSONB, nullable=True)  # Tenant-specific configuration
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    classes = relationship("Class", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")
    questions = relationship("Question", back_populates="tenant")

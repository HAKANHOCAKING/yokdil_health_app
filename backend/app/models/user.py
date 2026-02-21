"""
User, Institution, Class, and ClassMembership models
SECURITY ENHANCED: Multi-tenancy, session tracking, audit trails
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"


class User(Base):
    """User model with RBAC and multi-tenancy"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # SECURITY: Multi-tenancy - every user belongs to a tenant
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic info
    email = Column(String(255), nullable=False, index=True)  # Unique within tenant
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.STUDENT, index=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # KVKK: Deletion tracking
    deletion_requested_at = Column(DateTime, nullable=True)
    
    # MFA (optional)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(255), nullable=True)  # TOTP secret
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="user", cascade="all, delete-orphan")
    uploaded_pdfs = relationship("PDF", back_populates="uploader", foreign_keys="PDF.uploaded_by")
    
    # Session tracking (SECURITY: Device-based sessions)
    session_devices = relationship("SessionDevice", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    # Audit logging
    audit_logs = relationship("AuditLog", back_populates="user")
    
    # Teacher relationships
    taught_classes = relationship("Class", back_populates="teacher", foreign_keys="Class.teacher_id")
    created_assignments = relationship("Assignment", back_populates="teacher", foreign_keys="Assignment.teacher_id")
    
    # Student relationships
    class_memberships = relationship("ClassMembership", back_populates="student", foreign_keys="ClassMembership.student_id")


class Class(Base):
    """Class/Group model for teachers"""
    __tablename__ = "classes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # SECURITY: Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    teacher = relationship("User", back_populates="taught_classes", foreign_keys=[teacher_id])
    tenant = relationship("Tenant", back_populates="classes")
    memberships = relationship("ClassMembership", back_populates="class_obj", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="class_obj")


class ClassMembership(Base):
    """Student membership in classes"""
    __tablename__ = "class_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # SECURITY: Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    class_obj = relationship("Class", back_populates="memberships")
    student = relationship("User", back_populates="class_memberships", foreign_keys=[student_id])

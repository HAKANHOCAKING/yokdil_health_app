"""
PDF model for uploaded documents
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ParseStatus(str, enum.Enum):
    """PDF parse status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PDF(Base):
    """Uploaded PDF document"""
    __tablename__ = "pdfs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)  # MinIO path
    has_solutions = Column(Boolean, default=False, nullable=False, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    parse_status = Column(SQLEnum(ParseStatus), default=ParseStatus.PENDING, nullable=False, index=True)
    parse_metadata = Column(JSONB, nullable=True)  # {total_questions, errors, etc.}
    
    # Relationships
    uploader = relationship("User", back_populates="uploaded_pdfs", foreign_keys=[uploaded_by])
    questions = relationship("Question", back_populates="source_pdf")

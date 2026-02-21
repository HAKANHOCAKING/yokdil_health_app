"""
Assignment models with enhanced criteria_json
Supports trap-type based filtering and mastery exclusion
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class Assignment(Base):
    """
    Teacher-created assignment with enhanced filtering
    """
    __tablename__ = "assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    teacher_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Enhanced criteria
    criteria_json = Column(JSONB, nullable=False)
    """
    Enhanced criteria structure:
    {
        "branch": "all" | "health",
        "tags": ["anatomy", "epidemiology"],  // topic tags
        "trap_type_codes": ["TRAP_LOGIC_RELATION", "TRAP_CAUSE_EFFECT"],
        "difficulty_range": ["easy", "medium"],
        "exclude_mastered": true,  // exclude traps with accuracy >= 85% in last 30 days
        "count": 20,  // number of questions
        "mastery_threshold": 0.85,  // default 85%
        "mastery_window_days": 30  // default 30 days
    }
    """
    
    question_count = Column(Integer, nullable=False)
    
    # Timing
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    teacher = relationship("User", back_populates="created_assignments", foreign_keys=[teacher_id])
    class_obj = relationship("Class", back_populates="assignments")
    assignment_questions = relationship("AssignmentQuestion", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentQuestion(Base):
    """
    Many-to-many relationship between Assignments and Questions
    """
    __tablename__ = "assignment_questions"
    
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id", ondelete="CASCADE"), primary_key=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
    
    # Relationships
    assignment = relationship("Assignment", back_populates="assignment_questions")

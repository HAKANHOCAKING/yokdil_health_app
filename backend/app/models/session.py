"""
Session and Attempt models for tracking user progress
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class SessionMode(str, enum.Enum):
    """Session mode enumeration"""
    EXAM = "exam"
    COACHING = "coaching"
    QUICK_REVIEW = "quick_review"
    DAILY_GOAL = "daily_goal"
    SMART_MIX = "smart_mix"


class ConfidenceLevel(str, enum.Enum):
    """User confidence level for answers"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Session(Base):
    """User study session"""
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(SQLEnum(SessionMode), nullable=False, index=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    total_questions = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)
    metadata = Column(JSONB, nullable=True)  # {time_limit, tags_filter, etc.}
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    attempts = relationship("Attempt", back_populates="session", cascade="all, delete-orphan")


class Attempt(Base):
    """Individual question attempt"""
    __tablename__ = "attempts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    chosen_option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="SET NULL"), nullable=True, index=True)
    correct_option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="SET NULL"), nullable=True, index=True)
    is_correct = Column(Boolean, nullable=False, index=True)
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    hint_used = Column(Boolean, default=False, nullable=False)
    confidence = Column(SQLEnum(ConfidenceLevel), nullable=True)
    reviewed_after = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    trap_type_encountered = Column(String(100), nullable=True, index=True)  # Denormalized for reporting
    
    # Relationships
    session = relationship("Session", back_populates="attempts")
    user = relationship("User", back_populates="attempts")
    question = relationship("Question", back_populates="attempts")
    chosen_option = relationship("Option", foreign_keys=[chosen_option_id])
    correct_option = relationship("Option", foreign_keys=[correct_option_id])

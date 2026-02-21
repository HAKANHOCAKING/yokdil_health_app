"""
Vocabulary models for word sets and SRS progress
"""
import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Text, Boolean, DateTime, Date,
    ForeignKey, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MasteryLevel(str, enum.Enum):
    NEW = "new"            # 0 - never studied
    LEARNING = "learning"  # 1 - seen but not memorized
    REVIEW = "review"      # 2 - in SRS rotation
    MASTERED = "mastered"  # 3 - long intervals, well-known


class VocabSet(Base):
    """A named set of vocabulary words"""
    __tablename__ = "vocab_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    source_pdf_id = Column(String(255), nullable=True)
    created_by = Column(String(255), nullable=False)
    word_count = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="draft", nullable=False, index=True)  # draft, published
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    words = relationship("VocabWord", back_populates="vocab_set", cascade="all, delete-orphan")


class VocabWord(Base):
    """A single vocabulary word in a set"""
    __tablename__ = "vocab_words"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    set_id = Column(String(255), ForeignKey("vocab_sets.id", ondelete="CASCADE"), nullable=False, index=True)
    english = Column(String(500), nullable=False)
    turkish = Column(String(500), nullable=False)
    example_sentence = Column(Text, nullable=True)
    confidence = Column(Float, default=1.0, nullable=False)  # OCR confidence 0-1
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    vocab_set = relationship("VocabSet", back_populates="words")
    progress = relationship("VocabProgress", back_populates="word", cascade="all, delete-orphan")


class VocabProgress(Base):
    """SRS progress for a user on a specific word (SM-2 algorithm)"""
    __tablename__ = "vocab_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    word_id = Column(UUID(as_uuid=True), ForeignKey("vocab_words.id", ondelete="CASCADE"), nullable=False, index=True)

    # SM-2 fields
    ease_factor = Column(Float, default=2.5, nullable=False)       # EF >= 1.3
    interval = Column(Integer, default=0, nullable=False)           # days until next review
    repetition = Column(Integer, default=0, nullable=False)         # successful repetitions in a row
    next_review_date = Column(Date, nullable=True)                  # when to review next
    last_reviewed_at = Column(DateTime, nullable=True)

    # Mastery tracking
    mastery_level = Column(SQLEnum(MasteryLevel), default=MasteryLevel.NEW, nullable=False, index=True)
    total_reviews = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")
    word = relationship("VocabWord", back_populates="progress")


class StudySession(Base):
    """A vocabulary study session"""
    __tablename__ = "study_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mode = Column(String(50), nullable=False)  # flashcard, quiz_en_tr, quiz_tr_en, fill_blank
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    words_studied = Column(Integer, default=0, nullable=False)
    correct_count = Column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User")
    reviews = relationship("StudyReview", back_populates="session", cascade="all, delete-orphan")


class StudyReview(Base):
    """A single word review within a study session"""
    __tablename__ = "study_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    word_id = Column(UUID(as_uuid=True), ForeignKey("vocab_words.id", ondelete="CASCADE"), nullable=False, index=True)
    quality = Column(Integer, nullable=False)  # 0=Again, 3=Hard, 4=Good, 5=Easy
    is_correct = Column(Boolean, nullable=False)
    time_spent_ms = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    session = relationship("StudySession", back_populates="reviews")
    word = relationship("VocabWord")


class DailyStreak(Base):
    """Track consecutive daily study"""
    __tablename__ = "daily_streaks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_study_date = Column(Date, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User")

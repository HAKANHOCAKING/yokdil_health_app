"""
Question, Option, TrapAnalysis, Tag, and related models
SECURITY ENHANCED: Multi-tenancy support
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DifficultyLevel(str, enum.Enum):
    """Question difficulty enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class TagCategory(str, enum.Enum):
    """Tag category enumeration"""
    TOPIC = "topic"
    SKILL = "skill"
    DIFFICULTY = "difficulty"


class Question(Base):
    """Question model with multi-tenancy"""
    __tablename__ = "questions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # SECURITY: Multi-tenancy
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Question metadata
    exam_date = Column(String(50), nullable=False, index=True)  # "Mart 2018"
    question_no = Column(Integer, nullable=False)
    stem_text = Column(Text, nullable=False)  # The sentence with blank
    blank_position = Column(Integer, nullable=False)  # Word index of blank
    source_pdf_id = Column(UUID(as_uuid=True), ForeignKey("pdfs.id", ondelete="CASCADE"), nullable=True, index=True)
    page_no = Column(Integer, nullable=True)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM, nullable=False, index=True)
    is_ai_generated = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    bounding_box = Column(JSONB, nullable=True)  # {x, y, width, height}
    
    # Relationships
    tenant = relationship("Tenant", back_populates="questions")
    source_pdf = relationship("PDF", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary="question_tags", back_populates="questions")
    vocabulary = relationship("VocabularyGlossary", back_populates="question", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="question")


class Option(Base):
    """Answer option model"""
    __tablename__ = "options"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    option_letter = Column(String(1), nullable=False)  # A-E
    option_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="options")
    trap_analysis = relationship("TrapAnalysis", back_populates="option", uselist=False, cascade="all, delete-orphan")


class TrapAnalysis(Base):
    """Trap analysis for incorrect options"""
    __tablename__ = "trap_analyses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    trap_type = Column(String(100), nullable=False, index=True)
    explanation_tr = Column(Text, nullable=False)
    explanation_en = Column(Text, nullable=True)
    reasoning_points = Column(JSONB, nullable=True)  # [{type: "semantic", detail: "..."}]
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    option = relationship("Option", back_populates="trap_analysis")


class Tag(Base):
    """Tag for categorizing questions"""
    __tablename__ = "tags"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    category = Column(SQLEnum(TagCategory), default=TagCategory.TOPIC, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    questions = relationship("Question", secondary="question_tags", back_populates="tags")


class QuestionTag(Base):
    """Many-to-many relationship between Questions and Tags"""
    __tablename__ = "question_tags"
    
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)


class VocabularyGlossary(Base):
    """Vocabulary terms associated with questions"""
    __tablename__ = "vocabulary_glossary"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    term = Column(String(255), nullable=False)
    definition_tr = Column(Text, nullable=True)
    definition_en = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("Question", back_populates="vocabulary")

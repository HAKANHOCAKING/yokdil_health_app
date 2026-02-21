"""
Trap Types - Standardized ÖSYM trap classification
20 core trap types for sentence completion questions
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.core.database import Base


class TrapType(Base):
    """
    Standard trap type definitions (seed data)
    20 core trap types covering all ÖSYM patterns
    """
    __tablename__ = "trap_types"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Code (unique identifier)
    code = Column(String(50), nullable=False, unique=True, index=True)
    
    # Titles
    title_tr = Column(String(255), nullable=False)  # Turkish title
    title_en = Column(String(255), nullable=True)   # English title (optional)
    
    # Description
    description_tr = Column(Text, nullable=False)
    description_en = Column(Text, nullable=True)
    
    # Category grouping
    category = Column(String(50), nullable=False, index=True)
    # Categories: logic, grammar, semantic, structural, domain
    
    # Display order
    display_order = Column(Integer, default=0, nullable=False)
    
    # Active status
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    examples = Column(JSONB, nullable=True)  # Example sentences
    related_tags = Column(JSONB, nullable=True)  # Related reason_tags
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trap_analyses = relationship("TrapAnalysisEnhanced", back_populates="trap_type")


class TrapAnalysisEnhanced(Base):
    """
    Enhanced trap analysis with evidence and reason tags
    Links Option → TrapType with detailed analysis
    """
    __tablename__ = "trap_analyses_enhanced"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Links
    option_id = Column(UUID(as_uuid=True), ForeignKey("options.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    trap_type_id = Column(UUID(as_uuid=True), ForeignKey("trap_types.id", ondelete="RESTRICT"), nullable=False, index=True)
    
    # Analysis
    explanation_tr = Column(Text, nullable=False)  # 2-4 sentences
    explanation_en = Column(Text, nullable=True)
    
    # Evidence from stem (no hallucination)
    evidence_snippets = Column(JSONB, nullable=False)
    # Format: [{"text": "...", "position": [start, end]}, ...]
    
    # Reason tags (1-3 tags)
    reason_tags = Column(JSONB, nullable=False)
    # Format: ["semantic_mismatch", "wrong_connector_type"]
    
    # Confidence score (0.0-1.0)
    confidence_score = Column(Integer, default=80, nullable=False)  # 0-100
    
    # AI metadata
    analysis_metadata = Column(JSONB, nullable=True)
    # Format: {"model": "gpt-4", "prompt_version": "v2", "timestamp": "..."}
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    option = relationship("Option", foreign_keys=[option_id])
    trap_type = relationship("TrapType", back_populates="trap_analyses")


class QuestionExplanation(Base):
    """
    Comprehensive explanation for entire question
    Includes correct reasoning + all trap analyses
    """
    __tablename__ = "question_explanations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Correct answer reasoning (4-6 sentences)
    correct_reason_tr = Column(Text, nullable=False)
    correct_reason_en = Column(Text, nullable=True)
    
    # Reasoning breakdown
    correct_reasoning_points = Column(JSONB, nullable=False)
    # Format: [
    #   {"type": "relation_type", "detail": "neden-sonuç ilişkisi"},
    #   {"type": "evidence", "detail": "stem'den kanıt"},
    #   {"type": "why_correct", "detail": "neden doğru"}
    # ]
    
    # Evidence snippets from stem
    key_evidence_snippets = Column(JSONB, nullable=False)
    
    # Analysis metadata
    analysis_version = Column(String(20), default="v2.0", nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    question = relationship("Question", foreign_keys=[question_id])

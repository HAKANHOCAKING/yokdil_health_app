"""
Question-related schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class OptionBase(BaseModel):
    """Base option schema"""
    option_letter: str = Field(..., pattern="^[A-E]$")
    option_text: str
    is_correct: bool = False


class OptionResponse(OptionBase):
    """Option response with ID"""
    id: UUID
    
    class Config:
        from_attributes = True


class TrapAnalysisResponse(BaseModel):
    """Trap analysis response"""
    id: UUID
    trap_type: str
    explanation_tr: str
    explanation_en: Optional[str]
    reasoning_points: Optional[dict]
    
    class Config:
        from_attributes = True


class VocabularyResponse(BaseModel):
    """Vocabulary glossary response"""
    term: str
    definition_tr: Optional[str]
    definition_en: Optional[str]
    
    class Config:
        from_attributes = True


class TagResponse(BaseModel):
    """Tag response"""
    id: UUID
    name: str
    category: str
    
    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    """Question response"""
    id: UUID
    exam_date: str
    question_no: int
    stem_text: str
    blank_position: int
    difficulty: str
    is_ai_generated: bool
    options: List[OptionResponse]
    tags: List[TagResponse] = []
    glossary: List[VocabularyResponse] = []
    
    class Config:
        from_attributes = True


class QuestionWithTrapsResponse(QuestionResponse):
    """Question with trap analysis"""
    trap_analyses: List[TrapAnalysisResponse] = []


class QuestionListResponse(BaseModel):
    """Paginated question list"""
    questions: List[QuestionResponse]
    total: int
    page: int
    per_page: int

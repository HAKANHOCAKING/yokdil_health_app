"""
Session and attempt schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class SessionCreate(BaseModel):
    """Create session request"""
    mode: str = Field(..., pattern="^(exam|coaching|quick_review|daily_goal|smart_mix)$")
    metadata: Optional[dict] = None


class SessionResponse(BaseModel):
    """Session response"""
    id: UUID
    user_id: UUID
    mode: str
    started_at: datetime
    ended_at: Optional[datetime]
    total_questions: int
    correct_count: int
    metadata: Optional[dict]
    
    class Config:
        from_attributes = True


class AttemptCreate(BaseModel):
    """Create attempt request"""
    session_id: UUID
    question_id: UUID
    chosen_option_id: Optional[UUID] = None
    time_spent_seconds: int = Field(default=0, ge=0)
    hint_used: bool = False
    confidence: Optional[str] = Field(None, pattern="^(low|medium|high)$")


class AttemptResponse(BaseModel):
    """Attempt response with feedback"""
    id: UUID
    is_correct: bool
    correct_option_id: UUID
    chosen_option_id: Optional[UUID]
    trap_analysis: Optional[dict] = None
    points_earned: int
    streak_broken: bool
    
    class Config:
        from_attributes = True


class SessionCompleteRequest(BaseModel):
    """Complete session request"""
    session_id: UUID


class SessionSummaryResponse(BaseModel):
    """Session summary after completion"""
    session_id: UUID
    total_questions: int
    correct_count: int
    accuracy: float
    total_time_seconds: int
    average_time_per_question: float
    weak_traps: List[dict]
    weak_topics: List[dict]
    recommendations: List[str]

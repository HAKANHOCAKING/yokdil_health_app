"""
Session and Attempt endpoints
"""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.session import Session, Attempt
from app.models.question import Question, Option
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    AttemptCreate,
    AttemptResponse,
    SessionCompleteRequest,
    SessionSummaryResponse,
)

router = APIRouter()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new study session"""
    new_session = Session(
        user_id=current_user.id,
        mode=session_data.mode,
        metadata=session_data.metadata,
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    return new_session


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get session details"""
    result = await db.execute(
        select(Session).filter(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    return session


@router.post("/{session_id}/complete", response_model=SessionSummaryResponse)
async def complete_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a session and get summary"""
    # Get session
    result = await db.execute(
        select(Session).options(selectinload(Session.attempts)).filter(
            Session.id == session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    if session.ended_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed",
        )
    
    # Update session
    session.ended_at = datetime.utcnow()
    session.total_questions = len(session.attempts)
    session.correct_count = sum(1 for a in session.attempts if a.is_correct)
    
    await db.commit()
    
    # Calculate summary
    total_time = sum(a.time_spent_seconds for a in session.attempts)
    accuracy = session.correct_count / session.total_questions if session.total_questions > 0 else 0
    avg_time = total_time / session.total_questions if session.total_questions > 0 else 0
    
    # Analyze weak areas
    trap_counts = {}
    for attempt in session.attempts:
        if not attempt.is_correct and attempt.trap_type_encountered:
            trap_counts[attempt.trap_type_encountered] = trap_counts.get(attempt.trap_type_encountered, 0) + 1
    
    weak_traps = [{"trap_type": k, "count": v} for k, v in sorted(trap_counts.items(), key=lambda x: x[1], reverse=True)[:3]]
    
    recommendations = []
    if accuracy < 0.6:
        recommendations.append("Koçluk modunda daha fazla pratik yapın")
    if avg_time > 120:
        recommendations.append("Zaman yönetimine odaklanın - hedef 90 saniye/soru")
    if weak_traps:
        recommendations.append(f"{weak_traps[0]['trap_type']} tuzaklarını tekrar edin")
    
    return SessionSummaryResponse(
        session_id=session.id,
        total_questions=session.total_questions,
        correct_count=session.correct_count,
        accuracy=accuracy,
        total_time_seconds=total_time,
        average_time_per_question=avg_time,
        weak_traps=weak_traps,
        weak_topics=[],
        recommendations=recommendations,
    )


@router.post("/attempts", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_attempt(
    attempt_data: AttemptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit an answer attempt"""
    # Verify session belongs to user
    result = await db.execute(
        select(Session).filter(
            Session.id == attempt_data.session_id,
            Session.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    
    # Get question with options
    result = await db.execute(
        select(Question).options(selectinload(Question.options)).filter(Question.id == attempt_data.question_id)
    )
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    
    # Find correct option
    correct_option = next((opt for opt in question.options if opt.is_correct), None)
    if not correct_option:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Question has no correct answer",
        )
    
    # Check if answer is correct
    is_correct = attempt_data.chosen_option_id == correct_option.id
    
    # Get trap type if wrong
    trap_type = None
    if not is_correct and attempt_data.chosen_option_id:
        result = await db.execute(
            select(Option).options(selectinload(Option.trap_analysis)).filter(Option.id == attempt_data.chosen_option_id)
        )
        chosen_option = result.scalar_one_or_none()
        if chosen_option and chosen_option.trap_analysis:
            trap_type = chosen_option.trap_analysis.trap_type
    
    # Create attempt
    new_attempt = Attempt(
        session_id=attempt_data.session_id,
        user_id=current_user.id,
        question_id=attempt_data.question_id,
        chosen_option_id=attempt_data.chosen_option_id,
        correct_option_id=correct_option.id,
        is_correct=is_correct,
        time_spent_seconds=attempt_data.time_spent_seconds,
        hint_used=attempt_data.hint_used,
        confidence=attempt_data.confidence,
        trap_type_encountered=trap_type,
    )
    
    db.add(new_attempt)
    await db.commit()
    await db.refresh(new_attempt)
    
    return AttemptResponse(
        id=new_attempt.id,
        is_correct=is_correct,
        correct_option_id=correct_option.id,
        chosen_option_id=attempt_data.chosen_option_id,
        trap_analysis={"trap_type": trap_type} if trap_type else None,
        points_earned=10 if is_correct else 0,
        streak_broken=not is_correct,
    )

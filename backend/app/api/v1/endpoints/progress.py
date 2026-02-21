"""
Progress & SRS endpoints - Review queue, stats, study sessions
"""
from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Integer as SAInteger
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vocab import StudySession, StudyReview
from app.services.progress_service import ProgressService

router = APIRouter()


class ReviewRequest(BaseModel):
    word_id: str
    quality: int  # 0=Again, 3=Hard, 4=Good, 5=Easy
    session_id: Optional[str] = None
    time_spent_ms: int = 0


class StartSessionRequest(BaseModel):
    mode: str  # flashcard, quiz_en_tr, quiz_tr_en, fill_blank


# --- Review Queue ---

@router.get("/review-queue")
async def get_review_queue(
    limit: int = Query(default=20, ge=1, le=100),
    set_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get words due for review today"""
    service = ProgressService(db)
    queue = await service.get_review_queue(current_user.id, limit, set_id)
    return {"count": len(queue), "words": queue}


@router.get("/new-words")
async def get_new_words(
    set_id: str = Query(...),
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get words the user hasn't studied yet from a set"""
    service = ProgressService(db)
    words = await service.get_new_words(current_user.id, set_id, limit)
    return {"count": len(words), "words": words}


# --- Study Sessions ---

@router.post("/sessions/start")
async def start_study_session(
    req: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new study session"""
    session = StudySession(
        user_id=current_user.id,
        mode=req.mode,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return {
        "session_id": str(session.id),
        "mode": session.mode,
        "started_at": session.started_at.isoformat(),
    }


@router.post("/sessions/{session_id}/end")
async def end_study_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """End a study session"""
    result = await db.execute(
        select(StudySession).filter(StudySession.id == session_id)
    )
    session = result.scalar_one_or_none()

    if not session or str(session.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Session not found")

    # Count reviews in this session
    review_result = await db.execute(
        select(
            func.count(StudyReview.id),
            func.sum(func.cast(StudyReview.is_correct, SAInteger)),
        )
        .filter(StudyReview.session_id == session_id)
    )
    count_row = review_result.one()

    session.ended_at = datetime.utcnow()
    session.words_studied = count_row[0] or 0
    session.correct_count = count_row[1] or 0

    await db.commit()

    return {
        "session_id": str(session.id),
        "mode": session.mode,
        "words_studied": session.words_studied,
        "correct_count": session.correct_count,
        "duration_seconds": int((session.ended_at - session.started_at).total_seconds()),
    }


# --- Review a word ---

@router.post("/review")
async def review_word(
    req: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a word review (SM-2 algorithm)"""
    if req.quality not in (0, 3, 4, 5):
        raise HTTPException(status_code=400, detail="Quality must be 0, 3, 4, or 5")

    service = ProgressService(db)
    result = await service.record_review(
        user_id=current_user.id,
        word_id=UUID(req.word_id),
        quality=req.quality,
        session_id=UUID(req.session_id) if req.session_id else None,
        time_spent_ms=req.time_spent_ms,
    )

    await db.commit()
    return result


# --- Stats ---

@router.get("/stats")
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive study statistics"""
    service = ProgressService(db)
    stats = await service.get_stats(current_user.id)
    return stats

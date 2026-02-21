"""
Vocabulary endpoints - Browse sets, words, and generate quizzes
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.vocab import VocabSet, VocabWord
from app.services.quiz_service import QuizService

router = APIRouter()


@router.get("/sets")
async def list_vocab_sets(
    status: Optional[str] = Query(default="published"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all published vocabulary sets"""
    query = select(VocabSet).order_by(VocabSet.created_at.desc())
    if status:
        query = query.filter(VocabSet.status == status)

    result = await db.execute(query)
    sets = result.scalars().all()

    return {
        "sets": [
            {
                "id": str(s.id),
                "name": s.name,
                "word_count": s.word_count,
                "status": s.status,
                "created_at": s.created_at.isoformat(),
            }
            for s in sets
        ]
    }


@router.get("/sets/{set_id}/words")
async def get_set_words(
    set_id: str,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get words in a vocabulary set"""
    offset = (page - 1) * per_page

    result = await db.execute(
        select(VocabWord)
        .filter(VocabWord.set_id == set_id)
        .offset(offset)
        .limit(per_page)
    )
    words = result.scalars().all()

    return {
        "set_id": set_id,
        "page": page,
        "per_page": per_page,
        "words": [
            {
                "id": str(w.id),
                "english": w.english,
                "turkish": w.turkish,
                "example_sentence": w.example_sentence,
                "confidence": w.confidence,
            }
            for w in words
        ],
    }


@router.get("/quiz")
async def generate_quiz(
    set_id: str = Query(...),
    mode: str = Query(default="en_tr", regex="^(en_tr|tr_en|fill_blank)$"),
    count: int = Query(default=10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a quiz from a vocabulary set"""
    quiz_service = QuizService(db)
    questions = await quiz_service.generate_quiz(
        user_id=current_user.id,
        set_id=set_id,
        mode=mode,
        count=count,
    )

    if not questions:
        raise HTTPException(
            status_code=400,
            detail="Not enough words in the set to generate a quiz (minimum 4)",
        )

    return {
        "mode": mode,
        "count": len(questions),
        "questions": questions,
    }

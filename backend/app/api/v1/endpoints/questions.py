"""
Questions endpoints
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.question import Question, Option, TrapAnalysis, Tag
from app.schemas.question import QuestionListResponse, QuestionResponse, QuestionWithTrapsResponse

router = APIRouter()


@router.get("", response_model=QuestionListResponse)
async def list_questions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    mode: Optional[str] = Query(None, regex="^(exam|coaching|quick_review|smart_mix)$"),
    difficulty: Optional[str] = Query(None, regex="^(easy|medium|hard)$"),
    tags: Optional[str] = Query(None),  # comma-separated
    exam_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List questions with filtering and pagination"""
    # Build query
    query = select(Question).options(
        selectinload(Question.options).selectinload(Option.trap_analysis),
        selectinload(Question.tags),
        selectinload(Question.vocabulary),
    )
    
    # Apply filters
    if difficulty:
        query = query.filter(Question.difficulty == difficulty)
    
    if exam_date:
        query = query.filter(Question.exam_date == exam_date)
    
    if tags:
        tag_names = [t.strip() for t in tags.split(",")]
        query = query.join(Question.tags).filter(Tag.name.in_(tag_names))
    
    # Count total
    count_query = select(func.count()).select_from(Question)
    if difficulty:
        count_query = count_query.filter(Question.difficulty == difficulty)
    if exam_date:
        count_query = count_query.filter(Question.exam_date == exam_date)
    
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    # Execute
    result = await db.execute(query)
    questions = result.scalars().unique().all()
    
    return QuestionListResponse(
        questions=[
            QuestionResponse(
                id=q.id,
                exam_date=q.exam_date,
                question_no=q.question_no,
                stem_text=q.stem_text,
                blank_position=q.blank_position,
                difficulty=q.difficulty,
                is_ai_generated=q.is_ai_generated,
                options=[
                    {"id": opt.id, "option_letter": opt.option_letter, "option_text": opt.option_text, "is_correct": opt.is_correct}
                    for opt in q.options
                ],
                tags=[{"id": t.id, "name": t.name, "category": t.category} for t in q.tags],
                glossary=[{"term": v.term, "definition_tr": v.definition_tr, "definition_en": v.definition_en} for v in q.vocabulary],
            )
            for q in questions
        ],
        total=total or 0,
        page=page,
        per_page=per_page,
    )


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get single question by ID"""
    query = select(Question).options(
        selectinload(Question.options),
        selectinload(Question.tags),
        selectinload(Question.vocabulary),
    ).filter(Question.id == question_id)
    
    result = await db.execute(query)
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    
    return QuestionResponse(
        id=question.id,
        exam_date=question.exam_date,
        question_no=question.question_no,
        stem_text=question.stem_text,
        blank_position=question.blank_position,
        difficulty=question.difficulty,
        is_ai_generated=question.is_ai_generated,
        options=[
            {"id": opt.id, "option_letter": opt.option_letter, "option_text": opt.option_text, "is_correct": opt.is_correct}
            for opt in question.options
        ],
        tags=[{"id": t.id, "name": t.name, "category": t.category} for t in question.tags],
        glossary=[{"term": v.term, "definition_tr": v.definition_tr, "definition_en": v.definition_en} for v in question.vocabulary],
    )


@router.get("/{question_id}/traps", response_model=dict)
async def get_question_traps(
    question_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get trap analysis for a question"""
    query = select(Question).options(
        selectinload(Question.options).selectinload(Option.trap_analysis),
    ).filter(Question.id == question_id)
    
    result = await db.execute(query)
    question = result.scalar_one_or_none()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found",
        )
    
    trap_analyses = []
    correct_reasoning = []
    
    for option in question.options:
        if option.is_correct:
            # Correct option reasoning
            correct_reasoning.append({
                "option": option.option_letter,
                "text": option.option_text,
                "reasoning": "Doğru cevap - anlam ve gramer uyumu mükemmel"
            })
        elif option.trap_analysis:
            # Incorrect option trap
            trap_analyses.append({
                "option": option.option_letter,
                "trap_type": option.trap_analysis.trap_type,
                "explanation_tr": option.trap_analysis.explanation_tr,
                "explanation_en": option.trap_analysis.explanation_en,
                "reasoning_points": option.trap_analysis.reasoning_points,
            })
    
    return {
        "question_id": str(question_id),
        "correct_reasoning": correct_reasoning,
        "trap_analyses": trap_analyses,
    }

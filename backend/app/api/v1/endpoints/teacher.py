"""
Teacher endpoints for assignments and class management
"""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, List

from app.core.database import get_db
from app.core.security import require_teacher
from app.models.user import User, Class
from app.models.assignment import Assignment, AssignmentQuestion

router = APIRouter()


class AssignmentCreate(BaseModel):
    """Create assignment request"""
    class_id: UUID
    title: str
    description: Optional[str] = None
    question_count: int
    filter_criteria: Optional[dict] = None
    due_date: Optional[datetime] = None


@router.post("/assignments", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    assignment_data: AssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """Create a new assignment for a class"""
    # Verify class belongs to teacher
    result = await db.execute(
        select(Class).filter(
            Class.id == assignment_data.class_id,
            Class.teacher_id == current_user.id,
        )
    )
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Class not found or you don't have permission",
        )
    
    # Create assignment
    new_assignment = Assignment(
        teacher_id=current_user.id,
        class_id=assignment_data.class_id,
        title=assignment_data.title,
        description=assignment_data.description,
        question_count=assignment_data.question_count,
        filter_criteria=assignment_data.filter_criteria,
        due_date=assignment_data.due_date,
    )
    
    db.add(new_assignment)
    await db.commit()
    await db.refresh(new_assignment)
    
    # TODO: Select questions based on filter_criteria and link to assignment
    
    return {
        "id": new_assignment.id,
        "title": new_assignment.title,
        "class_id": str(new_assignment.class_id),
        "question_count": new_assignment.question_count,
        "due_date": new_assignment.due_date.isoformat() if new_assignment.due_date else None,
        "message": "Assignment created successfully",
    }


@router.get("/assignments")
async def list_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """List all assignments created by current teacher"""
    result = await db.execute(
        select(Assignment).options(selectinload(Assignment.class_obj)).filter(
            Assignment.teacher_id == current_user.id
        ).order_by(Assignment.created_at.desc())
    )
    assignments = result.scalars().unique().all()
    
    return {
        "assignments": [
            {
                "id": a.id,
                "title": a.title,
                "class_name": a.class_obj.name if a.class_obj else "N/A",
                "question_count": a.question_count,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "is_active": a.is_active,
                "created_at": a.created_at.isoformat(),
            }
            for a in assignments
        ]
    }


@router.get("/assignments/{assignment_id}/results")
async def get_assignment_results(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """Get student results for an assignment"""
    # Verify assignment belongs to teacher
    result = await db.execute(
        select(Assignment).options(
            selectinload(Assignment.class_obj).selectinload(lambda c: c.memberships)
        ).filter(
            Assignment.id == assignment_id,
            Assignment.teacher_id == current_user.id,
        )
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    # Get all students in class
    from app.models.session import Attempt
    
    student_ids = [m.student_id for m in assignment.class_obj.memberships]
    
    # Get attempts related to this assignment (simplified - would need session linking)
    result = await db.execute(
        select(Attempt).filter(
            Attempt.user_id.in_(student_ids)
        ).order_by(Attempt.created_at.desc()).limit(100)
    )
    attempts = result.scalars().all()
    
    # Group by student
    student_results = {}
    for attempt in attempts:
        if attempt.user_id not in student_results:
            student_results[attempt.user_id] = {
                "total": 0,
                "correct": 0,
            }
        student_results[attempt.user_id]["total"] += 1
        if attempt.is_correct:
            student_results[attempt.user_id]["correct"] += 1
    
    return {
        "assignment_id": str(assignment_id),
        "title": assignment.title,
        "student_results": [
            {
                "student_id": str(student_id),
                "total_attempts": stats["total"],
                "correct_count": stats["correct"],
                "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
            }
            for student_id, stats in student_results.items()
        ],
    }

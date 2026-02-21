"""
Student endpoints for assignments
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, ClassMembership
from app.models.assignment import Assignment

router = APIRouter()


@router.get("/assignments")
async def list_student_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List assignments assigned to current student"""
    # Get all classes student is in
    result = await db.execute(
        select(ClassMembership).filter(ClassMembership.student_id == current_user.id)
    )
    memberships = result.scalars().all()
    
    class_ids = [m.class_id for m in memberships]
    
    if not class_ids:
        return {"assignments": []}
    
    # Get assignments for those classes
    result = await db.execute(
        select(Assignment).options(selectinload(Assignment.class_obj)).filter(
            Assignment.class_id.in_(class_ids),
            Assignment.is_active == True,
        ).order_by(Assignment.due_date.asc())
    )
    assignments = result.scalars().unique().all()
    
    return {
        "assignments": [
            {
                "id": a.id,
                "title": a.title,
                "description": a.description,
                "class_name": a.class_obj.name if a.class_obj else "N/A",
                "question_count": a.question_count,
                "due_date": a.due_date.isoformat() if a.due_date else None,
            }
            for a in assignments
        ]
    }


@router.get("/assignments/{assignment_id}")
async def get_assignment_details(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get assignment details"""
    # Verify student is in the class
    result = await db.execute(
        select(Assignment).options(
            selectinload(Assignment.class_obj),
            selectinload(Assignment.assignment_questions),
        ).filter(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    # Check if student is in this class
    result = await db.execute(
        select(ClassMembership).filter(
            ClassMembership.class_id == assignment.class_id,
            ClassMembership.student_id == current_user.id,
        )
    )
    membership = result.scalar_one_or_none()
    
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this class",
        )
    
    return {
        "id": assignment.id,
        "title": assignment.title,
        "description": assignment.description,
        "question_count": assignment.question_count,
        "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
        "filter_criteria": assignment.filter_criteria,
    }


@router.post("/assignments/{assignment_id}/start")
async def start_assignment_session(
    assignment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start a new session for an assignment"""
    from app.models.session import Session, SessionMode
    
    # Verify assignment access (same as get_assignment_details)
    result = await db.execute(
        select(Assignment).filter(Assignment.id == assignment_id)
    )
    assignment = result.scalar_one_or_none()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )
    
    # Create session
    new_session = Session(
        user_id=current_user.id,
        mode=SessionMode.EXAM,
        metadata={"assignment_id": str(assignment_id)},
    )
    
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    
    return {
        "session_id": new_session.id,
        "assignment_id": str(assignment_id),
        "message": "Assignment session started",
    }

"""
Enhanced Analytics - Trap-based metrics for Teacher dashboard
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import require_teacher, get_current_user
from app.models.user import User, Class, ClassMembership
from app.models.session import Attempt
from app.models.trap_type import TrapAnalysisEnhanced, TrapType
from app.models.question import Question

router = APIRouter()


@router.get("/trap-performance")
async def get_trap_performance(
    days: int = Query(30, ge=7, le=365),
    class_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """
    Trap performance metrics for teacher's students
    Returns: accuracy_by_trap_type for last N days
    """
    # Get student IDs
    student_ids = await _get_teacher_student_ids(db, current_user, class_id)
    
    if not student_ids:
        return {"trap_performance": [], "total_students": 0}
    
    # Get attempts from last N days
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Attempt)
        .options(
            selectinload(Attempt.chosen_option)
            .selectinload(lambda o: o.trap_analysis)
        )
        .filter(
            and_(
                Attempt.user_id.in_(student_ids),
                Attempt.created_at >= cutoff_date
            )
        )
    )
    attempts = result.scalars().unique().all()
    
    # Group by trap type
    trap_stats = {}
    
    for attempt in attempts:
        if not attempt.chosen_option:
            continue
        
        # Get trap analysis
        from sqlalchemy import select as sql_select
        trap_result = await db.execute(
            sql_select(TrapAnalysisEnhanced)
            .options(selectinload(TrapAnalysisEnhanced.trap_type))
            .filter(TrapAnalysisEnhanced.option_id == attempt.chosen_option.id)
        )
        trap_analysis = trap_result.scalar_one_or_none()
        
        if not trap_analysis:
            continue
        
        trap_code = trap_analysis.trap_type.code
        
        if trap_code not in trap_stats:
            trap_stats[trap_code] = {
                "trap_code": trap_code,
                "trap_title_tr": trap_analysis.trap_type.title_tr,
                "category": trap_analysis.trap_type.category,
                "total_attempts": 0,
                "correct_attempts": 0,
                "total_time_seconds": 0,
            }
        
        trap_stats[trap_code]["total_attempts"] += 1
        if attempt.is_correct:
            trap_stats[trap_code]["correct_attempts"] += 1
        trap_stats[trap_code]["total_time_seconds"] += attempt.time_spent_seconds
    
    # Calculate accuracy and format
    trap_performance = []
    for trap_code, stats in trap_stats.items():
        accuracy = stats["correct_attempts"] / stats["total_attempts"] if stats["total_attempts"] > 0 else 0
        avg_time = stats["total_time_seconds"] / stats["total_attempts"] if stats["total_attempts"] > 0 else 0
        
        trap_performance.append({
            "trap_code": trap_code,
            "trap_title_tr": stats["trap_title_tr"],
            "category": stats["category"],
            "accuracy": round(accuracy, 3),
            "total_attempts": stats["total_attempts"],
            "avg_time_seconds": round(avg_time, 1),
        })
    
    # Sort by accuracy (lowest first - weakest traps)
    trap_performance.sort(key=lambda x: x["accuracy"])
    
    return {
        "trap_performance": trap_performance,
        "total_students": len(student_ids),
        "period_days": days,
        "top_5_weakest": trap_performance[:5],
    }


@router.get("/student-trap-heatmap")
async def get_student_trap_heatmap(
    class_id: UUID,
    days: int = Query(30, ge=7, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """
    Trap × Student heatmap for class
    Shows which student struggles with which trap type
    """
    # Verify class belongs to teacher
    result = await db.execute(
        select(Class)
        .options(selectinload(Class.memberships))
        .filter(
            and_(
                Class.id == class_id,
                Class.teacher_id == current_user.id,
            )
        )
    )
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        return {"error": "Class not found"}
    
    student_ids = [m.student_id for m in class_obj.memberships]
    
    if not student_ids:
        return {"heatmap": [], "students": [], "trap_types": []}
    
    # Get attempts
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    result = await db.execute(
        select(Attempt)
        .filter(
            and_(
                Attempt.user_id.in_(student_ids),
                Attempt.created_at >= cutoff_date
            )
        )
    )
    attempts = result.scalars().all()
    
    # Build heatmap: student_id → trap_code → {correct, total}
    heatmap_data = {}
    
    for attempt in attempts:
        student_id = str(attempt.user_id)
        
        if student_id not in heatmap_data:
            heatmap_data[student_id] = {}
        
        # Get trap analysis
        if not attempt.chosen_option:
            continue
        
        from sqlalchemy import select as sql_select
        trap_result = await db.execute(
            sql_select(TrapAnalysisEnhanced)
            .options(selectinload(TrapAnalysisEnhanced.trap_type))
            .filter(TrapAnalysisEnhanced.option_id == attempt.chosen_option.id)
        )
        trap_analysis = trap_result.scalar_one_or_none()
        
        if not trap_analysis:
            continue
        
        trap_code = trap_analysis.trap_type.code
        
        if trap_code not in heatmap_data[student_id]:
            heatmap_data[student_id][trap_code] = {"correct": 0, "total": 0}
        
        heatmap_data[student_id][trap_code]["total"] += 1
        if attempt.is_correct:
            heatmap_data[student_id][trap_code]["correct"] += 1
    
    # Format heatmap
    heatmap = []
    for student_id, traps in heatmap_data.items():
        for trap_code, stats in traps.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            heatmap.append({
                "student_id": student_id,
                "trap_code": trap_code,
                "accuracy": round(accuracy, 3),
                "attempts": stats["total"],
            })
    
    return {
        "heatmap": heatmap,
        "period_days": days,
    }


@router.get("/top-traps-per-student")
async def get_top_traps_per_student(
    class_id: UUID,
    limit: int = Query(5, ge=1, le=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """
    Top 5 weakest traps for each student in class
    """
    # Verify class
    result = await db.execute(
        select(Class)
        .options(selectinload(Class.memberships).selectinload(ClassMembership.student))
        .filter(
            and_(
                Class.id == class_id,
                Class.teacher_id == current_user.id,
            )
        )
    )
    class_obj = result.scalar_one_or_none()
    
    if not class_obj:
        return {"error": "Class not found"}
    
    students_data = []
    
    for membership in class_obj.memberships:
        student = membership.student
        
        # Get student's attempts (last 30 days)
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        result = await db.execute(
            select(Attempt)
            .filter(
                and_(
                    Attempt.user_id == student.id,
                    Attempt.created_at >= cutoff_date
                )
            )
        )
        attempts = result.scalars().all()
        
        # Group by trap
        trap_stats = {}
        
        for attempt in attempts:
            if not attempt.chosen_option:
                continue
            
            from sqlalchemy import select as sql_select
            trap_result = await db.execute(
                sql_select(TrapAnalysisEnhanced)
                .options(selectinload(TrapAnalysisEnhanced.trap_type))
                .filter(TrapAnalysisEnhanced.option_id == attempt.chosen_option.id)
            )
            trap_analysis = trap_result.scalar_one_or_none()
            
            if not trap_analysis:
                continue
            
            trap_code = trap_analysis.trap_type.code
            trap_title = trap_analysis.trap_type.title_tr
            
            if trap_code not in trap_stats:
                trap_stats[trap_code] = {"title": trap_title, "correct": 0, "total": 0}
            
            trap_stats[trap_code]["total"] += 1
            if attempt.is_correct:
                trap_stats[trap_code]["correct"] += 1
        
        # Calculate accuracy and sort
        trap_list = [
            {
                "trap_code": code,
                "trap_title": stats["title"],
                "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
                "attempts": stats["total"],
            }
            for code, stats in trap_stats.items()
        ]
        
        trap_list.sort(key=lambda x: x["accuracy"])
        
        students_data.append({
            "student_id": str(student.id),
            "student_name": student.full_name,
            "top_weak_traps": trap_list[:limit],
        })
    
    return {
        "students": students_data,
        "class_id": str(class_id),
    }


async def _get_teacher_student_ids(db: AsyncSession, teacher: User, class_id: Optional[UUID] = None) -> list:
    """Get student IDs for teacher (all classes or specific class)"""
    if class_id:
        # Specific class
        result = await db.execute(
            select(ClassMembership.student_id)
            .join(Class)
            .filter(
                and_(
                    Class.id == class_id,
                    Class.teacher_id == teacher.id,
                )
            )
        )
    else:
        # All teacher's classes
        result = await db.execute(
            select(ClassMembership.student_id)
            .join(Class)
            .filter(Class.teacher_id == teacher.id)
        )
    
    return [row[0] for row in result.all()]

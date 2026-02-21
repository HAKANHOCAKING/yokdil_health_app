"""
Analytics endpoints (role-based access)
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import get_current_user, require_teacher, require_admin
from app.models.user import User
from app.models.session import Attempt
from app.models.question import Tag

router = APIRouter()


@router.get("/student/me")
async def get_student_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current student's analytics"""
    # Get all attempts
    result = await db.execute(
        select(Attempt).filter(Attempt.user_id == current_user.id).order_by(Attempt.created_at.desc())
    )
    attempts = result.scalars().all()
    
    if not attempts:
        return {
            "total_attempts": 0,
            "overall_accuracy": 0,
            "total_time_spent": 0,
            "trap_performance": {},
            "recent_trend": "N/A",
        }
    
    total = len(attempts)
    correct = sum(1 for a in attempts if a.is_correct)
    total_time = sum(a.time_spent_seconds for a in attempts)
    
    # Trap performance
    trap_stats = {}
    for attempt in attempts:
        if attempt.trap_type_encountered:
            if attempt.trap_type_encountered not in trap_stats:
                trap_stats[attempt.trap_type_encountered] = {"total": 0, "correct": 0}
            trap_stats[attempt.trap_type_encountered]["total"] += 1
            if attempt.is_correct:
                trap_stats[attempt.trap_type_encountered]["correct"] += 1
    
    # Calculate accuracy per trap
    trap_performance = {
        trap: {
            "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
            "attempts": stats["total"],
        }
        for trap, stats in trap_stats.items()
    }
    
    # Recent trend (last 20 vs previous 20)
    recent_20 = attempts[:20]
    prev_20 = attempts[20:40] if len(attempts) > 20 else []
    
    recent_accuracy = sum(1 for a in recent_20 if a.is_correct) / len(recent_20) if recent_20 else 0
    prev_accuracy = sum(1 for a in prev_20 if a.is_correct) / len(prev_20) if prev_20 else 0
    
    trend = "improving" if recent_accuracy > prev_accuracy else "declining" if recent_accuracy < prev_accuracy else "stable"
    
    return {
        "total_attempts": total,
        "overall_accuracy": correct / total if total > 0 else 0,
        "total_time_spent": total_time,
        "average_time_per_question": total_time / total if total > 0 else 0,
        "trap_performance": trap_performance,
        "recent_trend": trend,
        "recent_accuracy": recent_accuracy,
        "previous_accuracy": prev_accuracy,
    }


@router.get("/teacher/students")
async def get_teacher_students_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_teacher),
):
    """Get analytics for all students in teacher's classes"""
    # Get all classes taught by current teacher
    from app.models.user import Class, ClassMembership
    
    result = await db.execute(
        select(Class).options(selectinload(Class.memberships)).filter(Class.teacher_id == current_user.id)
    )
    classes = result.scalars().unique().all()
    
    # Collect all student IDs
    student_ids = []
    for cls in classes:
        student_ids.extend([m.student_id for m in cls.memberships])
    
    if not student_ids:
        return {"students": [], "class_summary": {}}
    
    # Get attempts for all students
    result = await db.execute(
        select(Attempt).filter(Attempt.user_id.in_(student_ids)).order_by(Attempt.created_at.desc())
    )
    all_attempts = result.scalars().all()
    
    # Group by student
    student_stats = {}
    for attempt in all_attempts:
        if attempt.user_id not in student_stats:
            student_stats[attempt.user_id] = {
                "total": 0,
                "correct": 0,
                "total_time": 0,
            }
        student_stats[attempt.user_id]["total"] += 1
        if attempt.is_correct:
            student_stats[attempt.user_id]["correct"] += 1
        student_stats[attempt.user_id]["total_time"] += attempt.time_spent_seconds
    
    # Format response
    students_data = [
        {
            "student_id": str(student_id),
            "total_attempts": stats["total"],
            "accuracy": stats["correct"] / stats["total"] if stats["total"] > 0 else 0,
            "total_time_spent": stats["total_time"],
        }
        for student_id, stats in student_stats.items()
    ]
    
    return {
        "students": students_data,
        "total_students": len(student_ids),
        "class_summary": {
            "total_classes": len(classes),
            "total_attempts": len(all_attempts),
        },
    }


@router.get("/trap-heatmap")
async def get_trap_heatmap(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get trap type × topic heatmap for current user"""
    # Get all attempts with question tags
    result = await db.execute(
        select(Attempt).options(
            selectinload(Attempt.question).selectinload(lambda q: q.tags)
        ).filter(Attempt.user_id == current_user.id)
    )
    attempts = result.scalars().unique().all()
    
    if not attempts:
        return {"heatmap": [], "weakest_areas": []}
    
    # Build heatmap: topic -> trap_type -> {count, correct}
    heatmap_data = {}
    
    for attempt in attempts:
        if not attempt.question or not attempt.question.tags:
            continue
        
        for tag in attempt.question.tags:
            topic = tag.name
            trap = attempt.trap_type_encountered or "unknown"
            
            if topic not in heatmap_data:
                heatmap_data[topic] = {}
            
            if trap not in heatmap_data[topic]:
                heatmap_data[topic][trap] = {"count": 0, "correct": 0}
            
            heatmap_data[topic][trap]["count"] += 1
            if attempt.is_correct:
                heatmap_data[topic][trap]["correct"] += 1
    
    # Format heatmap
    heatmap = [
        {
            "topic": topic,
            "trap_types": {
                trap: {
                    "count": stats["count"],
                    "accuracy": stats["correct"] / stats["count"] if stats["count"] > 0 else 0,
                }
                for trap, stats in traps.items()
            },
        }
        for topic, traps in heatmap_data.items()
    ]
    
    # Find weakest areas (lowest accuracy)
    weak_areas = []
    for topic_data in heatmap:
        for trap, stats in topic_data["trap_types"].items():
            weak_areas.append({
                "topic": topic_data["topic"],
                "trap": trap,
                "accuracy": stats["accuracy"],
                "count": stats["count"],
            })
    
    weak_areas.sort(key=lambda x: x["accuracy"])
    weakest = weak_areas[:5]
    
    return {
        "heatmap": heatmap,
        "weakest_areas": weakest,
        "recommendations": [
            f"{area['topic']} konusunda {area['trap']} tuzağına dikkat edin (doğruluk: %{area['accuracy']*100:.0f})"
            for area in weakest[:3]
        ],
    }

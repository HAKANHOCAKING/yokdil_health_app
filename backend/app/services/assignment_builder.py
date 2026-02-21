"""
Assignment Builder Service
Creates assignments based on criteria_json with mastery exclusion
"""
from typing import List, Dict
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.question import Question, QuestionTag, Tag
from app.models.trap_type import TrapAnalysisEnhanced, TrapType
from app.models.session import Attempt
from app.models.assignment import Assignment, AssignmentQuestion


class AssignmentBuilder:
    """Build assignments with smart question selection"""
    
    def __init__(self, db: AsyncSession, tenant_id: UUID):
        self.db = db
        self.tenant_id = tenant_id
    
    async def build_assignment(
        self,
        criteria: Dict,
        student_ids: List[UUID],
    ) -> List[UUID]:
        """
        Build assignment based on criteria
        Returns: List of question IDs
        
        criteria = {
            "branch": "health",
            "tags": ["anatomy"],
            "trap_type_codes": ["TRAP_LOGIC_RELATION"],
            "difficulty_range": ["medium", "hard"],
            "exclude_mastered": True,
            "count": 20,
            "mastery_threshold": 0.85,
            "mastery_window_days": 30
        }
        """
        # Start with base query (tenant-scoped)
        query = select(Question).filter(Question.tenant_id == self.tenant_id)
        
        # Apply tag filter
        if criteria.get("tags"):
            query = query.join(QuestionTag).join(Tag).filter(
                Tag.name.in_(criteria["tags"])
            )
        
        # Apply difficulty filter
        if criteria.get("difficulty_range"):
            query = query.filter(Question.difficulty.in_(criteria["difficulty_range"]))
        
        # Apply trap type filter (if specified)
        if criteria.get("trap_type_codes"):
            trap_type_ids = await self._get_trap_type_ids(criteria["trap_type_codes"])
            
            if trap_type_ids:
                # Find questions that have options with these trap types
                query = query.join(Question.options).join(
                    TrapAnalysisEnhanced,
                    TrapAnalysisEnhanced.option_id == Question.options.property.mapper.class_.id
                ).filter(
                    TrapAnalysisEnhanced.trap_type_id.in_(trap_type_ids)
                ).distinct()
        
        # Execute query
        result = await self.db.execute(query)
        candidate_questions = result.scalars().unique().all()
        
        # Exclude mastered traps (if enabled)
        if criteria.get("exclude_mastered", False):
            mastered_trap_ids = await self._get_mastered_trap_ids(
                student_ids=student_ids,
                threshold=criteria.get("mastery_threshold", 0.85),
                window_days=criteria.get("mastery_window_days", 30),
            )
            
            if mastered_trap_ids:
                candidate_questions = await self._filter_mastered_questions(
                    candidate_questions,
                    mastered_trap_ids
                )
        
        # Select questions (random sampling if more than needed)
        import random
        count = criteria.get("count", 20)
        
        if len(candidate_questions) > count:
            selected = random.sample(candidate_questions, count)
        else:
            selected = candidate_questions
        
        return [q.id for q in selected]
    
    async def _get_trap_type_ids(self, trap_codes: List[str]) -> List[UUID]:
        """Get trap type IDs from codes"""
        result = await self.db.execute(
            select(TrapType.id).filter(TrapType.code.in_(trap_codes))
        )
        return [row[0] for row in result.all()]
    
    async def _get_mastered_trap_ids(
        self,
        student_ids: List[UUID],
        threshold: float,
        window_days: int,
    ) -> List[UUID]:
        """
        Get trap type IDs that students have mastered
        Mastery = accuracy >= threshold in last N days
        """
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        
        # Get all attempts in window
        result = await self.db.execute(
            select(Attempt)
            .filter(
                and_(
                    Attempt.user_id.in_(student_ids),
                    Attempt.created_at >= cutoff_date
                )
            )
        )
        attempts = result.scalars().all()
        
        # Group by trap type
        trap_stats = {}
        
        for attempt in attempts:
            if not attempt.chosen_option:
                continue
            
            # Get trap analysis
            trap_result = await self.db.execute(
                select(TrapAnalysisEnhanced)
                .filter(TrapAnalysisEnhanced.option_id == attempt.chosen_option.id)
            )
            trap_analysis = trap_result.scalar_one_or_none()
            
            if not trap_analysis:
                continue
            
            trap_id = trap_analysis.trap_type_id
            
            if trap_id not in trap_stats:
                trap_stats[trap_id] = {"correct": 0, "total": 0}
            
            trap_stats[trap_id]["total"] += 1
            if attempt.is_correct:
                trap_stats[trap_id]["correct"] += 1
        
        # Find mastered traps
        mastered = []
        for trap_id, stats in trap_stats.items():
            accuracy = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            if accuracy >= threshold:
                mastered.append(trap_id)
        
        return mastered
    
    async def _filter_mastered_questions(
        self,
        questions: List[Question],
        mastered_trap_ids: List[UUID],
    ) -> List[Question]:
        """Filter out questions that only test mastered traps"""
        filtered = []
        
        for question in questions:
            # Get all trap types for this question
            trap_result = await self.db.execute(
                select(TrapAnalysisEnhanced.trap_type_id)
                .join(TrapAnalysisEnhanced.option)
                .filter(TrapAnalysisEnhanced.option.has(question_id=question.id))
            )
            question_trap_ids = [row[0] for row in trap_result.all()]
            
            # Check if question has any non-mastered trap
            has_non_mastered = any(
                trap_id not in mastered_trap_ids
                for trap_id in question_trap_ids
            )
            
            if has_non_mastered or not question_trap_ids:
                filtered.append(question)
        
        return filtered

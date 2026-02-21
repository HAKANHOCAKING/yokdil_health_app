"""
Progress Service - Manages SRS progress, review queue, and stats
"""
import logging
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.models.vocab import (
    VocabWord, VocabSet, VocabProgress, StudySession,
    StudyReview, DailyStreak, MasteryLevel,
)
from app.services.srs_algorithm import sm2_algorithm, SRSState

logger = logging.getLogger(__name__)


class ProgressService:
    """Manages vocabulary learning progress"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_progress(self, user_id: UUID, word_id: UUID) -> VocabProgress:
        """Get existing progress or create new entry"""
        result = await self.db.execute(
            select(VocabProgress).filter(
                and_(
                    VocabProgress.user_id == user_id,
                    VocabProgress.word_id == word_id,
                )
            )
        )
        progress = result.scalar_one_or_none()

        if not progress:
            progress = VocabProgress(
                user_id=user_id,
                word_id=word_id,
            )
            self.db.add(progress)
            await self.db.flush()

        return progress

    async def record_review(
        self,
        user_id: UUID,
        word_id: UUID,
        quality: int,
        session_id: Optional[UUID] = None,
        time_spent_ms: int = 0,
    ) -> Dict:
        """
        Record a word review and update SRS progress.

        Args:
            quality: 0=Again, 3=Hard, 4=Good, 5=Easy
        """
        progress = await self.get_or_create_progress(user_id, word_id)

        # Build current state
        state = SRSState(
            ease_factor=progress.ease_factor,
            interval=progress.interval,
            repetition=progress.repetition,
            mastery_level=progress.mastery_level.value if progress.mastery_level else "new",
        )

        # Apply SM-2
        result = sm2_algorithm(state, quality)

        # Update progress
        progress.ease_factor = result.ease_factor
        progress.interval = result.interval
        progress.repetition = result.repetition
        progress.next_review_date = result.next_review_date
        progress.mastery_level = MasteryLevel(result.mastery_level)
        progress.last_reviewed_at = datetime.utcnow()
        progress.total_reviews += 1
        if quality >= 3:
            progress.correct_count += 1

        # Record review in session
        if session_id:
            review = StudyReview(
                session_id=session_id,
                word_id=word_id,
                quality=quality,
                is_correct=quality >= 3,
                time_spent_ms=time_spent_ms,
            )
            self.db.add(review)

        # Update streak
        await self._update_streak(user_id)

        await self.db.flush()

        return {
            "word_id": str(word_id),
            "quality": quality,
            "new_interval": result.interval,
            "next_review": str(result.next_review_date),
            "mastery_level": result.mastery_level,
            "ease_factor": result.ease_factor,
        }

    async def get_review_queue(
        self,
        user_id: UUID,
        limit: int = 20,
        set_id: Optional[str] = None,
    ) -> List[Dict]:
        """Get words due for review today"""
        today = date.today()

        query = (
            select(VocabProgress, VocabWord)
            .join(VocabWord, VocabProgress.word_id == VocabWord.id)
            .filter(
                and_(
                    VocabProgress.user_id == user_id,
                    or_(
                        VocabProgress.next_review_date <= today,
                        VocabProgress.next_review_date.is_(None),
                    ),
                )
            )
            .order_by(VocabProgress.next_review_date.asc().nullsfirst())
            .limit(limit)
        )

        if set_id:
            query = query.filter(VocabWord.set_id == set_id)

        result = await self.db.execute(query)
        rows = result.all()

        queue = []
        for progress, word in rows:
            queue.append({
                "word_id": str(word.id),
                "english": word.english,
                "turkish": word.turkish,
                "example_sentence": word.example_sentence,
                "mastery_level": progress.mastery_level.value if progress.mastery_level else "new",
                "ease_factor": progress.ease_factor,
                "interval": progress.interval,
                "next_review_date": str(progress.next_review_date) if progress.next_review_date else None,
                "total_reviews": progress.total_reviews,
            })

        return queue

    async def get_new_words(
        self,
        user_id: UUID,
        set_id: str,
        limit: int = 10,
    ) -> List[Dict]:
        """Get words that the user hasn't studied yet"""
        # Find word IDs the user has already studied
        studied_subq = (
            select(VocabProgress.word_id)
            .filter(VocabProgress.user_id == user_id)
            .subquery()
        )

        result = await self.db.execute(
            select(VocabWord)
            .filter(
                and_(
                    VocabWord.set_id == set_id,
                    ~VocabWord.id.in_(select(studied_subq.c.word_id)),
                )
            )
            .limit(limit)
        )
        words = result.scalars().all()

        return [
            {
                "word_id": str(w.id),
                "english": w.english,
                "turkish": w.turkish,
                "example_sentence": w.example_sentence,
                "mastery_level": "new",
            }
            for w in words
        ]

    async def get_stats(self, user_id: UUID) -> Dict:
        """Get comprehensive study statistics"""
        # Mastery distribution
        mastery_result = await self.db.execute(
            select(
                VocabProgress.mastery_level,
                func.count(VocabProgress.id),
            )
            .filter(VocabProgress.user_id == user_id)
            .group_by(VocabProgress.mastery_level)
        )
        mastery_dist = {row[0].value if row[0] else "new": row[1] for row in mastery_result.all()}

        # Total words studied
        total_studied = sum(mastery_dist.values())

        # Total reviews & accuracy
        review_result = await self.db.execute(
            select(
                func.count(VocabProgress.id),
                func.sum(VocabProgress.total_reviews),
                func.sum(VocabProgress.correct_count),
            )
            .filter(VocabProgress.user_id == user_id)
        )
        row = review_result.one()
        total_reviews = row[1] or 0
        total_correct = row[2] or 0
        accuracy = (total_correct / total_reviews * 100) if total_reviews > 0 else 0

        # Due for review today
        today = date.today()
        due_result = await self.db.execute(
            select(func.count(VocabProgress.id))
            .filter(
                and_(
                    VocabProgress.user_id == user_id,
                    VocabProgress.next_review_date <= today,
                )
            )
        )
        due_today = due_result.scalar() or 0

        # Streak
        streak_result = await self.db.execute(
            select(DailyStreak).filter(DailyStreak.user_id == user_id)
        )
        streak = streak_result.scalar_one_or_none()

        # Weekly activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_result = await self.db.execute(
            select(
                func.date(StudyReview.created_at).label("day"),
                func.count(StudyReview.id).label("count"),
            )
            .join(StudySession, StudyReview.session_id == StudySession.id)
            .filter(
                and_(
                    StudySession.user_id == user_id,
                    StudyReview.created_at >= week_ago,
                )
            )
            .group_by(func.date(StudyReview.created_at))
        )
        weekly_activity = {str(row[0]): row[1] for row in weekly_result.all()}

        return {
            "total_words_studied": total_studied,
            "total_reviews": total_reviews,
            "accuracy": round(accuracy, 1),
            "due_today": due_today,
            "mastery_distribution": {
                "new": mastery_dist.get("new", 0),
                "learning": mastery_dist.get("learning", 0),
                "review": mastery_dist.get("review", 0),
                "mastered": mastery_dist.get("mastered", 0),
            },
            "streak": {
                "current": streak.current_streak if streak else 0,
                "longest": streak.longest_streak if streak else 0,
                "last_study_date": str(streak.last_study_date) if streak and streak.last_study_date else None,
            },
            "weekly_activity": weekly_activity,
        }

    async def _update_streak(self, user_id: UUID):
        """Update daily study streak"""
        today = date.today()

        result = await self.db.execute(
            select(DailyStreak).filter(DailyStreak.user_id == user_id)
        )
        streak = result.scalar_one_or_none()

        if not streak:
            streak = DailyStreak(
                user_id=user_id,
                current_streak=1,
                longest_streak=1,
                last_study_date=today,
            )
            self.db.add(streak)
            return

        if streak.last_study_date == today:
            return  # Already counted today

        yesterday = today - timedelta(days=1)
        if streak.last_study_date == yesterday:
            streak.current_streak += 1
        else:
            streak.current_streak = 1

        streak.longest_streak = max(streak.longest_streak, streak.current_streak)
        streak.last_study_date = today

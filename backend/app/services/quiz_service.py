"""
Quiz Service - Generates quiz questions in multiple modes
Modes: EN->TR, TR->EN, Fill-in-the-blank
"""
import random
import re
import logging
from typing import List, Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.vocab import VocabWord, VocabProgress

logger = logging.getLogger(__name__)


class QuizService:
    """Generates quiz questions from vocabulary words"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_quiz(
        self,
        user_id: UUID,
        set_id: str,
        mode: str = "en_tr",
        count: int = 10,
    ) -> List[Dict]:
        """
        Generate quiz questions.

        Modes:
            en_tr: Show English, pick Turkish translation
            tr_en: Show Turkish, pick English translation
            fill_blank: Fill in the blank in a sentence

        Returns:
            List of quiz question dicts
        """
        # Get all words from the set
        result = await self.db.execute(
            select(VocabWord).filter(VocabWord.set_id == set_id)
        )
        all_words = result.scalars().all()

        if len(all_words) < 4:
            return []  # Need at least 4 words for distractors

        # Prioritize words that need review
        word_list = await self._prioritize_words(user_id, all_words, count)

        questions = []
        for word in word_list:
            if mode == "en_tr":
                q = self._make_en_tr_question(word, all_words)
            elif mode == "tr_en":
                q = self._make_tr_en_question(word, all_words)
            elif mode == "fill_blank":
                q = self._make_fill_blank_question(word, all_words)
            else:
                q = self._make_en_tr_question(word, all_words)

            if q:
                questions.append(q)

        return questions

    async def _prioritize_words(
        self,
        user_id: UUID,
        all_words: List[VocabWord],
        count: int,
    ) -> List[VocabWord]:
        """Prioritize words: due for review > low mastery > random"""
        word_ids = [w.id for w in all_words]

        # Get progress for these words
        result = await self.db.execute(
            select(VocabProgress)
            .filter(
                and_(
                    VocabProgress.user_id == user_id,
                    VocabProgress.word_id.in_(word_ids),
                )
            )
        )
        progress_map = {str(p.word_id): p for p in result.scalars().all()}

        # Sort: unstudied first, then low mastery, then due date
        def sort_key(word):
            p = progress_map.get(str(word.id))
            if not p:
                return (0, 0, 0)  # Never studied - highest priority
            mastery_order = {"new": 1, "learning": 2, "review": 3, "mastered": 4}
            m = mastery_order.get(p.mastery_level.value if p.mastery_level else "new", 0)
            return (m, p.correct_count, p.interval)

        sorted_words = sorted(all_words, key=sort_key)

        # Take top N, with some randomization
        if len(sorted_words) > count:
            # Take 70% prioritized, 30% random
            priority_count = max(1, int(count * 0.7))
            random_count = count - priority_count
            selected = sorted_words[:priority_count]
            remaining = [w for w in sorted_words[priority_count:]]
            if remaining:
                selected.extend(random.sample(remaining, min(random_count, len(remaining))))
            random.shuffle(selected)
            return selected

        random.shuffle(sorted_words)
        return sorted_words[:count]

    def _make_en_tr_question(self, word: VocabWord, all_words: List[VocabWord]) -> Dict:
        """EN->TR: Show English word, pick correct Turkish"""
        distractors = self._get_distractors(word, all_words, field="turkish")
        options = [{"text": word.turkish, "is_correct": True}]
        for d in distractors:
            options.append({"text": d, "is_correct": False})
        random.shuffle(options)

        return {
            "word_id": str(word.id),
            "mode": "en_tr",
            "prompt": word.english,
            "prompt_label": "English",
            "answer_label": "Turkce karsiligi nedir?",
            "correct_answer": word.turkish,
            "options": options,
        }

    def _make_tr_en_question(self, word: VocabWord, all_words: List[VocabWord]) -> Dict:
        """TR->EN: Show Turkish word, pick correct English"""
        distractors = self._get_distractors(word, all_words, field="english")
        options = [{"text": word.english, "is_correct": True}]
        for d in distractors:
            options.append({"text": d, "is_correct": False})
        random.shuffle(options)

        return {
            "word_id": str(word.id),
            "mode": "tr_en",
            "prompt": word.turkish,
            "prompt_label": "Turkce",
            "answer_label": "What is the English word?",
            "correct_answer": word.english,
            "options": options,
        }

    def _make_fill_blank_question(self, word: VocabWord, all_words: List[VocabWord]) -> Dict:
        """Fill-blank: Show sentence with blank, fill in the word"""
        sentence = word.example_sentence
        if not sentence:
            # Fallback: create a simple template sentence
            sentence = f"The meaning of _____ is '{word.turkish}'."
        else:
            # Replace the English word in the sentence with _____
            sentence = re.sub(
                re.escape(word.english),
                "_____",
                sentence,
                flags=re.IGNORECASE,
                count=1,
            )
            if "_____" not in sentence:
                sentence = f"{sentence} (_____)"

        distractors = self._get_distractors(word, all_words, field="english")
        options = [{"text": word.english, "is_correct": True}]
        for d in distractors:
            options.append({"text": d, "is_correct": False})
        random.shuffle(options)

        return {
            "word_id": str(word.id),
            "mode": "fill_blank",
            "prompt": sentence,
            "prompt_label": "Cumleyi tamamlayin",
            "hint": word.turkish,
            "correct_answer": word.english,
            "options": options,
        }

    def _get_distractors(
        self,
        target: VocabWord,
        all_words: List[VocabWord],
        field: str,
        count: int = 3,
    ) -> List[str]:
        """Get distractor options (wrong answers) for a quiz question"""
        target_value = getattr(target, field)
        candidates = []

        for w in all_words:
            val = getattr(w, field)
            if val != target_value and str(w.id) != str(target.id):
                candidates.append(val)

        # Deduplicate
        candidates = list(set(candidates))
        random.shuffle(candidates)

        return candidates[:count]

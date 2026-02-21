"""
SM-2 Spaced Repetition Algorithm
Based on the SuperMemo 2 algorithm by P.A. Wozniak

Quality scale:
  0 = Again (complete failure, reset)
  3 = Hard  (correct but difficult)
  4 = Good  (correct with some effort)
  5 = Easy  (effortless recall)

Mastery levels:
  New(0)      -> Learning(1)  : first review
  Learning(1) -> Review(2)    : 3+ successful repetitions
  Review(2)   -> Mastered(3)  : 8+ successful reps & EF > 2.5 & interval > 21 days
"""
from datetime import date, timedelta
from dataclasses import dataclass
from typing import Tuple


@dataclass
class SRSState:
    """Current SRS state for a word"""
    ease_factor: float = 2.5
    interval: int = 0          # days
    repetition: int = 0        # successful reps in a row
    mastery_level: str = "new"  # new, learning, review, mastered


@dataclass
class SRSResult:
    """Result after applying SM-2"""
    ease_factor: float
    interval: int
    repetition: int
    next_review_date: date
    mastery_level: str


def sm2_algorithm(state: SRSState, quality: int) -> SRSResult:
    """
    Apply SM-2 algorithm to compute next review schedule.

    Args:
        state: Current SRS state
        quality: Response quality (0=Again, 3=Hard, 4=Good, 5=Easy)

    Returns:
        SRSResult with updated values
    """
    ef = state.ease_factor
    interval = state.interval
    repetition = state.repetition

    if quality < 3:
        # Failed: reset repetition count, short interval
        repetition = 0
        interval = 1  # review tomorrow
    else:
        # Successful recall
        repetition += 1

        if repetition == 1:
            interval = 1
        elif repetition == 2:
            interval = 6
        else:
            interval = round(interval * ef)

        # Update ease factor using SM-2 formula
        ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # Clamp ease factor (minimum 1.3)
    ef = max(1.3, ef)

    # Cap interval at 365 days
    interval = min(interval, 365)

    # Calculate mastery level
    mastery = _calculate_mastery(repetition, ef, interval, quality)

    next_review = date.today() + timedelta(days=interval)

    return SRSResult(
        ease_factor=round(ef, 2),
        interval=interval,
        repetition=repetition,
        next_review_date=next_review,
        mastery_level=mastery,
    )


def _calculate_mastery(repetition: int, ef: float, interval: int, quality: int) -> str:
    """Determine mastery level based on SRS metrics"""
    if repetition == 0:
        if quality < 3:
            return "learning"  # Failed but at least seen
        return "learning"

    if repetition >= 8 and ef >= 2.5 and interval >= 21:
        return "mastered"

    if repetition >= 3:
        return "review"

    return "learning"


def quality_from_response(is_correct: bool, time_ms: int = 0, hint_used: bool = False) -> int:
    """
    Helper: estimate quality from response characteristics.

    Args:
        is_correct: Whether the answer was correct
        time_ms: Response time in milliseconds
        hint_used: Whether a hint was used

    Returns:
        Quality score (0, 3, 4, or 5)
    """
    if not is_correct:
        return 0  # Again

    if hint_used:
        return 3  # Hard

    # Fast correct response = Easy
    if time_ms > 0 and time_ms < 3000:
        return 5  # Easy

    if time_ms > 0 and time_ms < 8000:
        return 4  # Good

    return 4  # Default to Good

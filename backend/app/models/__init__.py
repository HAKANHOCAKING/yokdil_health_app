"""
Database Models Package
UPDATED: Multi-tenancy, audit logging, trap types, vocabulary & SRS
"""
from app.models.tenant import Tenant
from app.models.user import User, Class, ClassMembership
from app.models.question import (
    Question,
    Option,
    TrapAnalysis,
    Tag,
    QuestionTag,
    VocabularyGlossary,
)
from app.models.trap_type import TrapType, TrapAnalysisEnhanced, QuestionExplanation
from app.models.session import Session, Attempt
from app.models.session_device import SessionDevice, RefreshToken
from app.models.pdf import PDF
from app.models.assignment import Assignment, AssignmentQuestion
from app.models.audit_log import AuditLog
from app.models.vocab import (
    VocabSet,
    VocabWord,
    VocabProgress,
    StudySession,
    StudyReview,
    DailyStreak,
)

__all__ = [
    # Multi-tenancy
    "Tenant",

    # Users
    "User",
    "Class",
    "ClassMembership",

    # Questions
    "Question",
    "Option",
    "TrapAnalysis",  # Legacy
    "Tag",
    "QuestionTag",
    "VocabularyGlossary",

    # Trap System (Enhanced)
    "TrapType",
    "TrapAnalysisEnhanced",
    "QuestionExplanation",

    # Sessions
    "Session",
    "Attempt",

    # Session Management
    "SessionDevice",
    "RefreshToken",

    # Content
    "PDF",

    # Assignments
    "Assignment",
    "AssignmentQuestion",

    # Audit
    "AuditLog",

    # Vocabulary & SRS
    "VocabSet",
    "VocabWord",
    "VocabProgress",
    "StudySession",
    "StudyReview",
    "DailyStreak",
]

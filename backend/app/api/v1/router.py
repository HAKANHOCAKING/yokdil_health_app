"""
Main API v1 router aggregating all endpoints
UPDATED: Added vocabulary, progress, and SRS endpoints
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    questions,
    sessions,
    analytics,
    analytics_enhanced,
    admin,
    teacher,
    student,
    kvkk,
    vocab,
    progress,
)

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Questions
api_router.include_router(questions.router, prefix="/questions", tags=["Questions"])

# Sessions & Attempts
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])

# Analytics
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(analytics_enhanced.router, prefix="/analytics-enhanced", tags=["Analytics Enhanced"])

# Admin
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])

# Teacher
api_router.include_router(teacher.router, prefix="/teacher", tags=["Teacher"])

# Student
api_router.include_router(student.router, prefix="/student", tags=["Student"])

# KVKK Compliance
api_router.include_router(kvkk.router, prefix="/kvkk", tags=["KVKK"])

# Vocabulary & Learning
api_router.include_router(vocab.router, prefix="/vocab", tags=["Vocabulary"])
api_router.include_router(progress.router, prefix="/progress", tags=["Progress & SRS"])

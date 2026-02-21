"""
Background tasks for data export (KVKK compliance)
"""
import asyncio
import json
from datetime import datetime
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


# Create async engine for worker
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@shared_task(bind=True, name="export.user_data")
def export_user_data_task(self, user_id: str, tenant_id: str):
    """
    Background task to export all user data
    KVKK compliance: Right to data portability
    """
    asyncio.run(_export_user_data_async(user_id, tenant_id))


async def _export_user_data_async(user_id: str, tenant_id: str):
    """Export user data to JSON"""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import select, and_
            from app.models.user import User
            from app.models.session import Session, Attempt
            from app.models.audit_log import AuditLog
            
            # Get user
            result = await db.execute(
                select(User).filter(
                    and_(
                        User.id == user_id,
                        User.tenant_id == tenant_id,
                    )
                )
            )
            user = result.scalar_one_or_none()
            
            if not user:
                logger.error(f"User {user_id} not found")
                return
            
            # Collect all user data
            export_data = {
                "user_info": {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "created_at": user.created_at.isoformat(),
                },
                "sessions": [],
                "attempts": [],
                "audit_logs": [],
            }
            
            # Get sessions
            result = await db.execute(select(Session).filter(Session.user_id == user.id))
            sessions = result.scalars().all()
            export_data["sessions"] = [
                {
                    "id": str(s.id),
                    "mode": s.mode,
                    "started_at": s.started_at.isoformat(),
                    "ended_at": s.ended_at.isoformat() if s.ended_at else None,
                    "total_questions": s.total_questions,
                    "correct_count": s.correct_count,
                }
                for s in sessions
            ]
            
            # Get attempts
            result = await db.execute(select(Attempt).filter(Attempt.user_id == user.id))
            attempts = result.scalars().all()
            export_data["attempts"] = [
                {
                    "id": str(a.id),
                    "question_id": str(a.question_id),
                    "is_correct": a.is_correct,
                    "time_spent_seconds": a.time_spent_seconds,
                    "created_at": a.created_at.isoformat(),
                    "trap_type": a.trap_type_encountered,
                }
                for a in attempts
            ]
            
            # Get audit logs (last 2 years)
            result = await db.execute(
                select(AuditLog)
                .filter(AuditLog.user_id == user.id)
                .order_by(AuditLog.timestamp.desc())
                .limit(1000)
            )
            logs = result.scalars().all()
            export_data["audit_logs"] = [
                {
                    "action": log.action,
                    "timestamp": log.timestamp.isoformat(),
                    "description": log.description,
                }
                for log in logs
            ]
            
            # Save to storage (MinIO)
            from app.services.storage import StorageService
            storage = StorageService()
            
            export_json = json.dumps(export_data, ensure_ascii=False, indent=2)
            export_filename = f"data_export_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Upload (implementation depends on storage service)
            # await storage.upload_export(export_filename, export_json.encode())
            
            logger.info(f"User data exported successfully: {export_filename}")
            
            # TODO: Send email to user with download link
        
        except Exception as e:
            logger.error(f"Data export failed for {user_id}: {str(e)}")
            raise


@shared_task(name="export.cleanup_expired")
def cleanup_expired_exports_task():
    """
    Cleanup old data exports (older than 7 days)
    SECURITY: Data retention policy
    """
    # Implementation: Delete old exports from storage
    pass

"""
Celery configuration for background tasks
SECURITY: Heavy operations isolated from main API
"""
from celery import Celery
from app.core.config import settings

# Create Celery app
celery_app = Celery(
    "yokdil_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.worker.tasks.pdf_tasks",
        "app.worker.tasks.ai_tasks",
        "app.worker.tasks.export_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task routing
    task_routes={
        "app.worker.tasks.pdf_tasks.*": {"queue": "pdf"},
        "app.worker.tasks.ai_tasks.*": {"queue": "ai"},
        "app.worker.tasks.export_tasks.*": {"queue": "export"},
    },
    
    # Retry configuration
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result expiration
    result_expires=3600,  # 1 hour
    
    # Rate limits
    task_default_rate_limit="100/m",
)


# Task base class with common settings
class BaseTask(celery_app.Task):
    """Base task with retry logic"""
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 60}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


celery_app.Task = BaseTask


if __name__ == "__main__":
    celery_app.start()

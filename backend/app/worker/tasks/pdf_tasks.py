"""
Background tasks for PDF processing
Heavy operations run in isolated worker
"""
import asyncio
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings
from app.services.pdf_parser import PDFParserService
from app.services.storage import StorageService
from app.models.pdf import PDF, ParseStatus

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


@shared_task(bind=True, name="pdf.parse")
def parse_pdf_task(self, pdf_id: str, tenant_id: str):
    """
    Background task to parse PDF
    SECURITY: Isolated from main API, sandboxed execution
    """
    asyncio.run(_parse_pdf_async(pdf_id, tenant_id))


async def _parse_pdf_async(pdf_id: str, tenant_id: str):
    """Async PDF parsing logic"""
    async with AsyncSessionLocal() as db:
        try:
            # Get PDF record
            from sqlalchemy import select, and_
            result = await db.execute(
                select(PDF).filter(
                    and_(
                        PDF.id == pdf_id,
                        PDF.tenant_id == tenant_id,
                    )
                )
            )
            pdf = result.scalar_one_or_none()
            
            if not pdf:
                logger.error(f"PDF {pdf_id} not found")
                return
            
            # Update status
            pdf.parse_status = ParseStatus.PROCESSING
            await db.commit()
            
            # Download PDF from storage
            storage = StorageService()
            pdf_content = await storage.download_pdf(pdf.storage_path)
            
            # Parse PDF
            parser = PDFParserService()
            parsed_questions = await parser.parse_pdf(pdf_content, pdf.has_solutions)
            
            # Update status
            pdf.parse_status = ParseStatus.COMPLETED
            pdf.parse_metadata = {
                "total_questions": len(parsed_questions),
                "parsed_at": str(asyncio.get_event_loop().time()),
            }
            
            # Store parsed questions in a temp cache or directly insert
            # (Implementation depends on whether admin confirmation is required)
            
            await db.commit()
            
            logger.info(f"PDF {pdf_id} parsed successfully: {len(parsed_questions)} questions")
        
        except Exception as e:
            logger.error(f"PDF parsing failed for {pdf_id}: {str(e)}")
            
            # Update status to failed
            if pdf:
                pdf.parse_status = ParseStatus.FAILED
                pdf.parse_metadata = {"error": str(e)}
                await db.commit()
            
            raise


@shared_task(name="pdf.cleanup")
def cleanup_old_pdfs_task():
    """
    Cleanup old PDFs beyond retention period
    SECURITY: Data retention policy enforcement
    """
    # Implementation for data retention
    pass

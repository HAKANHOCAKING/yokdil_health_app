"""
Background tasks for AI operations
Trap analysis, question generation
"""
import asyncio
from celery import shared_task
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
import logging

from app.core.config import settings
from app.services.trap_analyzer_enhanced import TrapAnalyzerEnhanced

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


@shared_task(bind=True, name="ai.analyze_question")
def analyze_question_task(self, question_id: str, tenant_id: str):
    """
    Background task to analyze question and generate trap labels
    SECURITY: Rate limited, tenant-scoped
    """
    asyncio.run(_analyze_question_async(question_id, tenant_id))


async def _analyze_question_async(question_id: str, tenant_id: str):
    """Async question analysis logic"""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import select, and_
            from app.models.question import Question
            from app.models.trap_type import TrapAnalysisEnhanced, QuestionExplanation
            
            # Get question
            result = await db.execute(
                select(Question)
                .options(selectinload(Question.options))
                .filter(
                    and_(
                        Question.id == question_id,
                        Question.tenant_id == tenant_id,
                    )
                )
            )
            question = result.scalar_one_or_none()
            
            if not question:
                logger.error(f"Question {question_id} not found")
                return
            
            # Prepare options data
            options_data = [
                {
                    "letter": opt.option_letter,
                    "text": opt.option_text,
                    "is_correct": opt.is_correct,
                }
                for opt in question.options
            ]
            
            # Run AI analysis
            analyzer = TrapAnalyzerEnhanced()
            analysis = await analyzer.analyze_question_complete(
                stem=question.stem_text,
                options=options_data,
            )
            
            # Save correct reasoning
            explanation = QuestionExplanation(
                question_id=question.id,
                correct_reason_tr=analysis["correct_analysis"]["explanation_tr"],
                correct_reason_en=analysis["correct_analysis"].get("explanation_en"),
                correct_reasoning_points=analysis["correct_analysis"]["reasoning_points"],
                key_evidence_snippets=analysis["correct_analysis"]["evidence_snippets"],
            )
            db.add(explanation)
            
            # Save trap analyses
            for wrong in analysis["wrong_analyses"]:
                # Find option
                option = next(
                    (opt for opt in question.options if opt.option_letter == wrong["option_letter"]),
                    None
                )
                
                if not option:
                    continue
                
                # Find trap type
                from app.models.trap_type import TrapType
                trap_result = await db.execute(
                    select(TrapType).filter(TrapType.code == wrong["trap_type"])
                )
                trap_type = trap_result.scalar_one_or_none()
                
                if not trap_type:
                    logger.warning(f"Trap type {wrong['trap_type']} not found")
                    continue
                
                # Create trap analysis
                trap_analysis = TrapAnalysisEnhanced(
                    option_id=option.id,
                    trap_type_id=trap_type.id,
                    explanation_tr=wrong["explanation_tr"],
                    explanation_en=wrong.get("explanation_en"),
                    evidence_snippets=wrong.get("evidence_snippets", []),
                    reason_tags=wrong.get("reason_tags", []),
                    confidence_score=wrong.get("confidence", 80),
                    analysis_metadata={"model": settings.OPENAI_MODEL, "timestamp": str(asyncio.get_event_loop().time())},
                )
                db.add(trap_analysis)
            
            await db.commit()
            
            logger.info(f"Question {question_id} analyzed successfully")
        
        except Exception as e:
            logger.error(f"Question analysis failed for {question_id}: {str(e)}")
            raise

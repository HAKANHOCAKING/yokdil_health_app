"""
Admin endpoints for PDF management, content moderation, and vocabulary import
"""
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.pdf import PDF, ParseStatus
from app.services.pdf_parser import PDFParserService
from app.services.pdf_renderer import PDFRendererService
from app.services.storage import StorageService

router = APIRouter()


# --- Pydantic schemas for vocab import ---

class VocabDraftItem(BaseModel):
    english: str
    turkish: str
    example_sentence: Optional[str] = None
    confidence: Optional[float] = 1.0


class BulkVocabImport(BaseModel):
    set_name: str
    source_pdf_id: Optional[str] = None
    words: List[VocabDraftItem]


# --- PDF Upload & Management ---

@router.post("/pdfs/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    has_solutions: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Upload PDF for parsing"""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    storage_service = StorageService()
    storage_path = await storage_service.upload_pdf(file)

    new_pdf = PDF(
        filename=file.filename,
        storage_path=storage_path,
        has_solutions=has_solutions,
        uploaded_by=current_user.id,
        parse_status=ParseStatus.PENDING,
    )

    db.add(new_pdf)
    await db.commit()
    await db.refresh(new_pdf)

    return {
        "id": new_pdf.id,
        "filename": new_pdf.filename,
        "status": new_pdf.parse_status,
        "message": "PDF uploaded successfully. Parsing will start shortly.",
    }


@router.get("/pdfs")
async def list_pdfs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all uploaded PDFs"""
    result = await db.execute(select(PDF).order_by(PDF.uploaded_at.desc()))
    pdfs = result.scalars().all()

    return {
        "pdfs": [
            {
                "id": pdf.id,
                "filename": pdf.filename,
                "has_solutions": pdf.has_solutions,
                "parse_status": pdf.parse_status,
                "uploaded_at": pdf.uploaded_at.isoformat(),
                "metadata": pdf.parse_metadata,
            }
            for pdf in pdfs
        ]
    }


# --- PDF Page Rendering ---

@router.get("/pdfs/{pdf_id}/page-count")
async def get_pdf_page_count(
    pdf_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get total page count for a PDF"""
    result = await db.execute(select(PDF).filter(PDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    storage_service = StorageService()
    pdf_content = await storage_service.download_pdf(pdf.storage_path)

    renderer = PDFRendererService()
    page_count = renderer.get_page_count(pdf_content)

    return {"pdf_id": str(pdf_id), "page_count": page_count}


@router.get("/pdfs/{pdf_id}/pages/{page_num}")
async def get_pdf_page_image(
    pdf_id: UUID,
    page_num: int,
    dpi: int = Query(default=200, ge=72, le=400),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Render and return a single PDF page as PNG image"""
    result = await db.execute(select(PDF).filter(PDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    storage_service = StorageService()
    pdf_content = await storage_service.download_pdf(pdf.storage_path)

    renderer = PDFRendererService(dpi=dpi)
    try:
        png_bytes = renderer.render_page(pdf_content, page_num)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(
        content=png_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{pdf.filename}_page{page_num}.png"',
            "Cache-Control": "public, max-age=86400",
        },
    )


@router.post("/pdfs/{pdf_id}/render")
async def bulk_render_pdf(
    pdf_id: UUID,
    dpi: int = Query(default=200, ge=72, le=400),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Bulk render all pages of a PDF (admin tool)"""
    result = await db.execute(select(PDF).filter(PDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    storage_service = StorageService()
    pdf_content = await storage_service.download_pdf(pdf.storage_path)

    renderer = PDFRendererService(dpi=dpi)
    results = renderer.render_all_pages(pdf_content)

    return {
        "pdf_id": str(pdf_id),
        "total_pages": len(results),
        "pages": results,
    }


# --- PDF Parse Preview ---

@router.get("/pdfs/{pdf_id}/parse-preview")
async def get_parse_preview(
    pdf_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get preview of parsed questions before confirming"""
    result = await db.execute(select(PDF).filter(PDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    if pdf.parse_status == ParseStatus.PENDING:
        parser_service = PDFParserService()
        storage_service = StorageService()

        pdf_content = await storage_service.download_pdf(pdf.storage_path)

        pdf.parse_status = ParseStatus.PROCESSING
        await db.commit()

        try:
            parsed_questions = await parser_service.parse_pdf(pdf_content, pdf.has_solutions)

            pdf.parse_status = ParseStatus.COMPLETED
            pdf.parse_metadata = {
                "total_questions": len(parsed_questions),
                "preview_mode": True,
            }
            await db.commit()

            return {
                "pdf_id": str(pdf.id),
                "status": "completed",
                "questions_preview": parsed_questions[:5],
                "total_questions": len(parsed_questions),
            }
        except Exception as e:
            pdf.parse_status = ParseStatus.FAILED
            pdf.parse_metadata = {"error": str(e)}
            await db.commit()
            raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    return {
        "pdf_id": str(pdf.id),
        "status": pdf.parse_status,
        "metadata": pdf.parse_metadata,
    }


@router.post("/pdfs/{pdf_id}/confirm")
async def confirm_and_save_questions(
    pdf_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Confirm parsed questions and save to database"""
    result = await db.execute(select(PDF).filter(PDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    if pdf.parse_status != ParseStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="PDF must be successfully parsed first")

    return {
        "message": "Questions imported successfully",
        "pdf_id": str(pdf_id),
    }


# --- OCR & Vocabulary Import ---

@router.post("/pdfs/{pdf_id}/ocr")
async def run_ocr_on_pdf(
    pdf_id: UUID,
    page_start: int = Query(default=0, ge=0),
    page_end: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Run OCR on PDF pages and extract vocabulary drafts"""
    from app.services.ocr_service import OCRService
    from app.services.vocab_parser import VocabParserService

    result = await db.execute(select(PDF).filter(PDF.id == pdf_id))
    pdf = result.scalar_one_or_none()

    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    storage_service = StorageService()
    pdf_content = await storage_service.download_pdf(pdf.storage_path)

    renderer = PDFRendererService(dpi=300)
    page_count = renderer.get_page_count(pdf_content)

    if page_end is None:
        page_end = page_count - 1
    page_end = min(page_end, page_count - 1)

    ocr_service = OCRService()
    vocab_parser = VocabParserService()
    all_drafts = []

    for page_num in range(page_start, page_end + 1):
        png_bytes = renderer.render_page(pdf_content, page_num)
        ocr_text = ocr_service.extract_text(png_bytes)
        words = vocab_parser.parse_vocabulary(ocr_text)

        for word in words:
            word["page"] = page_num
            word["source_pdf_id"] = str(pdf_id)

        all_drafts.extend(words)

    return {
        "pdf_id": str(pdf_id),
        "pages_processed": page_end - page_start + 1,
        "drafts_found": len(all_drafts),
        "drafts": all_drafts,
    }


@router.post("/imports/bulk")
async def bulk_import_vocab(
    data: BulkVocabImport,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Bulk import vocabulary words as a set"""
    from app.models.vocab import VocabSet, VocabWord

    vocab_set = VocabSet(
        name=data.set_name,
        source_pdf_id=data.source_pdf_id,
        created_by=str(current_user.id),
        word_count=len(data.words),
        status="published",
    )
    db.add(vocab_set)
    await db.flush()

    for item in data.words:
        word = VocabWord(
            set_id=str(vocab_set.id),
            english=item.english,
            turkish=item.turkish,
            example_sentence=item.example_sentence,
            confidence=item.confidence or 1.0,
        )
        db.add(word)

    await db.commit()
    await db.refresh(vocab_set)

    return {
        "set_id": str(vocab_set.id),
        "set_name": vocab_set.name,
        "word_count": len(data.words),
        "message": "Vocabulary set imported successfully",
    }


@router.post("/imports/drafts")
async def add_single_draft(
    word: VocabDraftItem,
    set_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Add a single vocabulary word to an existing set"""
    from app.models.vocab import VocabSet, VocabWord

    result = await db.execute(select(VocabSet).filter(VocabSet.id == set_id))
    vocab_set = result.scalar_one_or_none()

    if not vocab_set:
        raise HTTPException(status_code=404, detail="Vocabulary set not found")

    new_word = VocabWord(
        set_id=set_id,
        english=word.english,
        turkish=word.turkish,
        example_sentence=word.example_sentence,
        confidence=word.confidence or 1.0,
    )
    db.add(new_word)

    vocab_set.word_count = vocab_set.word_count + 1
    await db.commit()
    await db.refresh(new_word)

    return {
        "word_id": str(new_word.id),
        "english": new_word.english,
        "turkish": new_word.turkish,
        "message": "Word added successfully",
    }


# --- Question management ---

@router.patch("/questions/{question_id}")
async def update_question(
    question_id: UUID,
    update_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Manually correct a question"""
    from app.models.question import Question

    result = await db.execute(select(Question).filter(Question.id == question_id))
    question = result.scalar_one_or_none()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    for key, value in update_data.items():
        if hasattr(question, key):
            setattr(question, key, value)

    await db.commit()
    await db.refresh(question)

    return {"message": "Question updated successfully", "question_id": str(question_id)}

import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.fiscal_period import FiscalPeriod
from app.models.pdf_apuracao import PdfApuracaoFile, PdfExtractedPage
from app.services.apuracao.pdf_text_extraction_service import extract_pdf_text

router = APIRouter(prefix="/api/v1", tags=["pdf-apuracao"])


@router.post(
    "/fiscal-periods/{period_id}/pdf-apuracao-files",
    status_code=status.HTTP_201_CREATED,
)
def upload_pdf(period_id: uuid.UUID, file: UploadFile, db: Session = Depends(get_db)):
    period = db.query(FiscalPeriod).filter(FiscalPeriod.id == period_id).first()
    if not period:
        raise HTTPException(404, "Competência não encontrada")
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Apenas arquivos .pdf são aceitos")

    upload_dir = os.path.join(settings.upload_dir, str(period_id), "pdf")
    os.makedirs(upload_dir, exist_ok=True)

    file_id = uuid.uuid4()
    stored_path = os.path.join(upload_dir, f"{file_id}_{file.filename}")
    content = file.file.read()
    with open(stored_path, "wb") as f:
        f.write(content)

    pdf_record = PdfApuracaoFile(
        id=file_id,
        fiscal_period_id=period_id,
        company_id=period.company_id,
        original_filename=file.filename,
        stored_path=stored_path,
        file_size_bytes=len(content),
        extraction_status="pending",
    )
    db.add(pdf_record)
    db.flush()

    # Extract immediately on upload
    extract_pdf_text(db, pdf_record, stored_path)

    db.commit()
    db.refresh(pdf_record)
    return _pdf_to_dict(pdf_record)


@router.get("/fiscal-periods/{period_id}/pdf-apuracao-files")
def list_pdfs(period_id: uuid.UUID, db: Session = Depends(get_db)):
    rows = db.query(PdfApuracaoFile).filter(
        PdfApuracaoFile.fiscal_period_id == period_id
    ).order_by(PdfApuracaoFile.created_at.desc()).all()
    return [_pdf_to_dict(r) for r in rows]


@router.post("/pdf-apuracao-files/{pdf_file_id}/extract-text")
def re_extract(pdf_file_id: uuid.UUID, db: Session = Depends(get_db)):
    pdf_file = _get_pdf(db, pdf_file_id)
    result = extract_pdf_text(db, pdf_file, pdf_file.stored_path)
    db.commit()
    return {
        "pdf_file_id": str(pdf_file_id),
        "status": result.status,
        "pages": result.total_pages,
        "average_confidence": round(result.average_confidence, 2),
    }


@router.get("/pdf-apuracao-files/{pdf_file_id}/extracted-pages")
def get_pages(pdf_file_id: uuid.UUID, db: Session = Depends(get_db)):
    _get_pdf(db, pdf_file_id)
    pages = db.query(PdfExtractedPage).filter(
        PdfExtractedPage.pdf_file_id == pdf_file_id
    ).order_by(PdfExtractedPage.page_number).all()
    return [
        {
            "page_number": p.page_number,
            "char_count": p.char_count,
            "confidence_score": float(p.confidence_score) if p.confidence_score else 0,
            "extraction_method": p.extraction_method,
            "extracted_text": p.extracted_text,
        }
        for p in pages
    ]


def _get_pdf(db: Session, pdf_file_id: uuid.UUID) -> PdfApuracaoFile:
    f = db.query(PdfApuracaoFile).filter(PdfApuracaoFile.id == pdf_file_id).first()
    if not f:
        raise HTTPException(404, "Arquivo PDF não encontrado")
    return f


def _pdf_to_dict(r: PdfApuracaoFile) -> dict:
    return {
        "id": str(r.id),
        "fiscal_period_id": str(r.fiscal_period_id),
        "original_filename": r.original_filename,
        "file_size_bytes": r.file_size_bytes,
        "total_pages": r.total_pages,
        "extraction_status": r.extraction_status,
        "extraction_error": r.extraction_error,
        "average_confidence": float(r.average_confidence) if r.average_confidence else None,
        "created_at": r.created_at.isoformat(),
    }

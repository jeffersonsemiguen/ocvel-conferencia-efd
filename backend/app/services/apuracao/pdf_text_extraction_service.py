"""
Extrai texto de PDFs usando PyMuPDF.
Regra de confiança:
  char_count > 500  => 90
  100-500           => 60
  1-99              => 30
  0                 => 0
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass

import fitz  # PyMuPDF

from sqlalchemy.orm import Session

from app.models.pdf_apuracao import PdfApuracaoFile, PdfExtractedPage


@dataclass
class ExtractionResult:
    total_pages: int
    pages_extracted: int
    average_confidence: float
    status: str  # extracted | low_confidence | failed
    error: str | None = None


def _confidence(char_count: int) -> float:
    if char_count > 500:
        return 90.0
    if char_count >= 100:
        return 60.0
    if char_count >= 1:
        return 30.0
    return 0.0


def extract_pdf_text(
    db: Session,
    pdf_file: PdfApuracaoFile,
    stored_path: str,
) -> ExtractionResult:
    # Clear previous extraction for this file
    db.query(PdfExtractedPage).filter(PdfExtractedPage.pdf_file_id == pdf_file.id).delete()

    try:
        doc = fitz.open(stored_path)
    except Exception as exc:
        pdf_file.extraction_status = "failed"
        pdf_file.extraction_error = str(exc)
        db.flush()
        return ExtractionResult(0, 0, 0.0, "failed", str(exc))

    total_pages = len(doc)
    confidence_scores: list[float] = []

    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text") or ""
        char_count = len(text.strip())
        confidence = _confidence(char_count)
        confidence_scores.append(confidence)

        db.add(PdfExtractedPage(
            pdf_file_id=pdf_file.id,
            page_number=page_num + 1,
            extracted_text=text if char_count > 0 else None,
            char_count=char_count,
            extraction_method="pymupdf",
            confidence_score=confidence,
        ))

    doc.close()

    avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
    pages_with_text = sum(1 for c in confidence_scores if c > 0)

    if avg_confidence >= 60:
        status = "extracted"
    elif avg_confidence > 0:
        status = "low_confidence"
    else:
        status = "low_confidence"

    pdf_file.total_pages = total_pages
    pdf_file.average_confidence = round(avg_confidence, 2)
    pdf_file.extraction_status = status
    pdf_file.extraction_error = None
    db.flush()

    return ExtractionResult(
        total_pages=total_pages,
        pages_extracted=pages_with_text,
        average_confidence=avg_confidence,
        status=status,
    )

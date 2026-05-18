import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PdfApuracaoFile(Base):
    __tablename__ = "pdf_apuracao_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # extracted | low_confidence | failed | pending
    extraction_status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    extraction_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    average_confidence: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)


class PdfExtractedPage(Base):
    __tablename__ = "pdf_extracted_pages"
    __table_args__ = (UniqueConstraint("pdf_file_id", "page_number"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pdf_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("pdf_apuracao_files.id"), nullable=False, index=True)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    char_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # pymupdf | pdfplumber | manual | ocr_future
    extraction_method: Mapped[str] = mapped_column(String(20), nullable=False, default="pymupdf")
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

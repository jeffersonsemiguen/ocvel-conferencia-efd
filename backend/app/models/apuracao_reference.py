import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ApuracaoReferenceValue(Base):
    __tablename__ = "apuracao_reference_values"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True)
    pdf_file_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("pdf_apuracao_files.id"), nullable=True)

    # pdf_auto | spreadsheet | manual
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    source_label: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # entrada | saida | apuracao_icms | apuracao_icms_st | apuracao_ipi | ajuste_icms | ajuste_ipi
    operation_type: Mapped[str] = mapped_column(String(30), nullable=False)
    # icms | icms_st | ipi | difal | fecop | outros
    tax_type: Mapped[str] = mapped_column(String(20), nullable=False)

    cfop: Mapped[str | None] = mapped_column(String(4), nullable=True)
    cst: Mapped[str | None] = mapped_column(String(3), nullable=True)
    csosn: Mapped[str | None] = mapped_column(String(3), nullable=True)
    cst_ipi: Mapped[str | None] = mapped_column(String(2), nullable=True)
    aliquot: Mapped[float | None] = mapped_column(Numeric(15, 4), nullable=True)

    accounting_value: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    icms_base: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    icms_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    icms_st_base: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    icms_st_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    ipi_base: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)
    ipi_amount: Mapped[float | None] = mapped_column(Numeric(15, 2), nullable=True)

    adjustment_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    adjustment_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_page: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_row: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)

    is_reviewed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

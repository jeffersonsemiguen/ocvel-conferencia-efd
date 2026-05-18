import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text, func
from sqlalchemy import Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PrAdjustmentCode(Base):
    __tablename__ = "pr_adjustment_codes"
    __table_args__ = (
        Index("ix_pr_adjustment_codes_code_table_type", "code", "table_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # unique=True removed — same code may appear in different periods
    code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    start_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    adjustment_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_e112: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_e113: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # True quando a exigência é condicional ("Se for o caso")
    optional_e112: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    optional_e113: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    page_ref: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # --- Sprint 5 new fields ---
    table_type: Mapped[str] = mapped_column(String(30), default="ajuste_apuracao", nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(100), nullable=True)
    register_expected: Mapped[str | None] = mapped_column(String(10), nullable=True)
    apuracao_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    adjustment_nature: Mapped[str | None] = mapped_column(String(30), nullable=True)
    operation_scope: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requires_fiscal_document: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_process: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_auxiliary_ie: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_item: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_participant: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    valid_from: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    orientation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)


class PrAdjustmentImportBatch(Base):
    __tablename__ = "pr_adjustment_import_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_version: Mapped[str | None] = mapped_column(String(30), nullable=True)
    imported_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    # processing | imported | imported_with_errors | failed
    status: Mapped[str] = mapped_column(String(30), default="processing", nullable=False)
    records_total: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_imported: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    records_failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=True)


class PrAdjustmentValidationResult(Base):
    __tablename__ = "pr_adjustment_validation_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    validation_run_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    fiscal_period_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    register_code: Mapped[str] = mapped_column(String(10), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    adjustment_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    adjustment_table_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    pr_adjustment_code_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    validation_rule_code: Mapped[str] = mapped_column(String(20), nullable=False)
    # valid | warning | invalid | not_applicable | not_found
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    requires_e112: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_e112: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_e113: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_e113: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_process: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_process: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_fiscal_document: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_fiscal_document: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_auxiliary_ie: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_auxiliary_ie: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdE112AdjustmentInfo(Base):
    """Informações adicionais de um ajuste E111."""
    __tablename__ = "efd_e112_adjustment_info"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    parent_e111_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    num_da: Mapped[str | None] = mapped_column(String(255), nullable=True)
    num_proc: Mapped[str | None] = mapped_column(String(60), nullable=True)
    ind_proc: Mapped[str | None] = mapped_column(String(1), nullable=True)
    proc: Mapped[str | None] = mapped_column(String(255), nullable=True)
    txt_compl: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdE113AdjustmentDoc(Base):
    """Documentos fiscais relacionados a um ajuste E111."""
    __tablename__ = "efd_e113_adjustment_docs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    parent_e111_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    cod_part: Mapped[str | None] = mapped_column(String(60), nullable=True)
    cod_mod: Mapped[str | None] = mapped_column(String(2), nullable=True)
    ser: Mapped[str | None] = mapped_column(String(4), nullable=True)
    sub: Mapped[str | None] = mapped_column(String(3), nullable=True)
    num_doc: Mapped[str | None] = mapped_column(String(9), nullable=True)
    dt_doc: Mapped[str | None] = mapped_column(String(8), nullable=True)
    cod_item: Mapped[str | None] = mapped_column(String(60), nullable=True)
    chv_doc_e: Mapped[str | None] = mapped_column(String(44), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

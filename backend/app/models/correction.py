import hashlib
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CorrectionSuggestion(Base):
    __tablename__ = "correction_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("validation_findings.id"), nullable=False, index=True)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)

    # Contexto FK adicionados na Sprint 6
    validation_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("validation_runs.id"), nullable=True, index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    fiscal_period_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=True)

    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    register_code: Mapped[str] = mapped_column(String(10), nullable=False)
    field_index: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str] = mapped_column(String(60), nullable=False)
    original_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    suggested_value: Mapped[str] = mapped_column(String(100), nullable=False)
    suggestion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # low | medium | high | critical
    risk_level: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)

    # pending | approved | rejected | applied | canceled | conflict
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)

    # technical | fiscal | structural | informational
    suggestion_type: Mapped[str] = mapped_column(String(20), default="technical", nullable=False)

    # update_field | replace_line | insert_line_after | insert_line_before | delete_line | recalculate_total
    action_type: Mapped[str] = mapped_column(String(30), default="update_field", nullable=False)

    original_line: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_line: Mapped[str | None] = mapped_column(Text, nullable=True)

    rule_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source: Mapped[str | None] = mapped_column(String(60), nullable=True)

    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=func.now())


class CorrectedFile(Base):
    __tablename__ = "corrected_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False)

    # Sprint 6 FKs
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    fiscal_period_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    generated_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    applied_suggestions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    total_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    total_lines: Mapped[int | None] = mapped_column(Integer, nullable=True)
    generated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    # ready | error | generated | downloaded | archived | invalidated
    status: Mapped[str] = mapped_column(String(20), default="ready", nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, onupdate=func.now())


class CorrectionLog(Base):
    __tablename__ = "correction_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    corrected_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("corrected_files.id"), nullable=False, index=True)
    suggestion_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("correction_suggestions.id"), nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    register_code: Mapped[str] = mapped_column(String(10), nullable=False)
    field_index: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str] = mapped_column(String(60), nullable=False)
    original_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    applied_value: Mapped[str] = mapped_column(String(100), nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Sprint 6 additions
    original_efd_file_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    action_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    original_line: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_line: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    rule_code: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now(), nullable=True)

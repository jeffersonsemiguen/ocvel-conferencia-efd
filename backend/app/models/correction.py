import hashlib
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CorrectionSuggestion(Base):
    __tablename__ = "correction_suggestions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    finding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("validation_findings.id"), nullable=False, index=True)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)

    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    register_code: Mapped[str] = mapped_column(String(10), nullable=False)
    field_index: Mapped[int] = mapped_column(Integer, nullable=False)
    field_name: Mapped[str] = mapped_column(String(60), nullable=False)
    original_value: Mapped[str | None] = mapped_column(String(100), nullable=True)
    suggested_value: Mapped[str] = mapped_column(String(100), nullable=False)
    suggestion_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    # low | medium | high
    risk_level: Mapped[str] = mapped_column(String(10), default="medium", nullable=False)

    # pending | approved | rejected | applied | canceled
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[str | None] = mapped_column(String(255), nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class CorrectedFile(Base):
    __tablename__ = "corrected_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False)
    generated_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    applied_suggestions_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # ready | error
    status: Mapped[str] = mapped_column(String(20), default="ready", nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


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

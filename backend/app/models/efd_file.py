import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EfdFile(Base):
    __tablename__ = "efd_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fiscal_period_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    # Status: uploaded, parsing, parsed, error
    parse_status: Mapped[str] = mapped_column(String(20), default="uploaded", nullable=False)
    parse_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    total_lines: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # EFD header info extracted from 0000 record
    efd_version: Mapped[str | None] = mapped_column(String(10), nullable=True)
    efd_cnpj: Mapped[str | None] = mapped_column(String(14), nullable=True)
    efd_company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    efd_state: Mapped[str | None] = mapped_column(String(2), nullable=True)
    efd_start_date: Mapped[str | None] = mapped_column(String(8), nullable=True)
    efd_end_date: Mapped[str | None] = mapped_column(String(8), nullable=True)
    # empresa | contabil | merged
    file_role: Mapped[str] = mapped_column(String(10), default="merged", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    fiscal_period: Mapped["FiscalPeriod"] = relationship("FiscalPeriod", back_populates="efd_files")

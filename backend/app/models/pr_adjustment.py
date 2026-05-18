import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PrAdjustmentCode(Base):
    __tablename__ = "pr_adjustment_codes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
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

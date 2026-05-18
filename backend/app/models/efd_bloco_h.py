import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EfdBlocoH005(Base):
    """Registro H005 — Totais do Inventário."""
    __tablename__ = "efd_bloco_h005"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    dt_inv: Mapped[str | None] = mapped_column(String(8), nullable=True)   # DDMMAAAA
    vl_inv: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    mot_inv: Mapped[str | None] = mapped_column(String(2), nullable=True)  # 01–05

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)


class EfdBlocoH010(Base):
    """Registro H010 — Inventário."""
    __tablename__ = "efd_bloco_h010"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    efd_file_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("efd_files.id"), nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_h005_line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)

    cod_item: Mapped[str | None] = mapped_column(String(60), nullable=True, index=True)
    unid: Mapped[str | None] = mapped_column(String(6), nullable=True)
    qtd: Mapped[float | None] = mapped_column(Numeric(18, 3), nullable=True)
    vl_unit: Mapped[float | None] = mapped_column(Numeric(18, 6), nullable=True)
    vl_item: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)
    ind_prop: Mapped[str | None] = mapped_column(String(1), nullable=True)
    cod_part: Mapped[str | None] = mapped_column(String(60), nullable=True)
    txt_compl: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cod_cta: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vl_item_ir: Mapped[float | None] = mapped_column(Numeric(18, 2), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
